import redis
import docker
import json
import os

r = redis.Redis.from_url(os.getenv("REDIS_URL"))
client = docker.from_env()

print("Worker listening...")

while True:
    task = r.blpop('job_queue', timeout=0)
    if not task:
        continue

    _, data = task
    job = json.loads(data)
    print(f"Processing {job['job_id']}...")

    # Pass MinIO config to the analysis container
    env_vars = {
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "S3_ENDPOINT": os.getenv("S3_ENDPOINT"),
        "JOB_BUCKET": "job-data",
        "INPUT_KEY": job['input_key'],
        "JOB_ID": job['job_id']
    }

    try:
        # Note: We use network="my-app_default" so it can reach MinIO
        # You might need to check 'docker network ls' to get the exact name
        # created by docker-compose. Usually it is foldername_default.
        client.containers.run(
            image=f"isoquac-job:{job['version']}",
            environment=env_vars,
            # <--- UPDATE THIS to your project network name
            network="isoquac-rewrite_default",
            remove=True
        )
        print(f"Job {job['job_id']} completed.")
    except Exception as e:
        print(f"Error: {e}")

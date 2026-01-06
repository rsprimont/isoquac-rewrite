import boto3
import os
import json
import time

# 1. Setup S3 Connection
s3 = boto3.client('s3',
                  endpoint_url=os.getenv("S3_ENDPOINT"),
                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                  )

bucket = os.getenv("JOB_BUCKET")
input_key = os.getenv("INPUT_KEY")
job_id = os.getenv("JOB_ID")

print(f"🧪 Analyzing {input_key}...")

# 2. Download Input
local_input = "input.raw"
s3.download_file(bucket, input_key, local_input)

# 3. RUN ANALYSIS (Simulation)
# In real life, you read 'local_input' here
time.sleep(2)
results = {
    "some_metric": 42,
}

# 4. Upload Output
local_output = "results.json"
with open(local_output, "w") as f:
    json.dump(results, f)

output_key = f"{job_id}/results.json"
s3.upload_file(local_output, bucket, output_key)

print(f"🎉 Results saved to {output_key}")

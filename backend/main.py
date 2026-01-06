from fastapi import FastAPI, UploadFile, File
import redis
import boto3
import json
import uuid
import os

app = FastAPI()

# Configuration
REDIS_URL = os.getenv("REDIS_URL")
S3_ENDPOINT = os.getenv("S3_ENDPOINT")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "job-data"

# Clients
r = redis.Redis.from_url(REDIS_URL)
s3 = boto3.client('s3', endpoint_url=S3_ENDPOINT,
                  aws_access_key_id=ACCESS_KEY,
                  aws_secret_access_key=SECRET_KEY)

# Ensure bucket exists on startup
try:
    s3.create_bucket(Bucket=BUCKET_NAME)
except:
    pass


@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    file_key = f"{job_id}/{file.filename}"

    # 1. Upload to MinIO (Streams file, good for RAM)
    s3.upload_fileobj(file.file, BUCKET_NAME, file_key)

    # 2. Queue Job
    payload = {
        "job_id": job_id,
        "input_key": file_key,
        "version": "v1.0.0"
    }
    r.rpush('job_queue', json.dumps(payload))

    return {"job_id": job_id, "status": "queued"}

import json
import requests
import boto3

# Configuration
API_URL = "https://datausa.io/api/data?drilldowns=Nation&measures=Population"
BUCKET_NAME = "your-target-s3-bucket"
S3_PREFIX = "datausa/"
S3_KEY = f"{S3_PREFIX}population_data.json"
REGION = "us-east-1"

s3 = boto3.client("s3", region_name=REGION)

def clear_s3_prefix(bucket, prefix):
    print(f"Clearing s3://{bucket}/{prefix}")
    paginator = s3.get_paginator('list_objects_v2')
    objects_to_delete = []

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            objects_to_delete.append({'Key': obj['Key']})

    if objects_to_delete:
        s3.delete_objects(Bucket=bucket, Delete={'Objects': objects_to_delete})
        print(f"Deleted {len(objects_to_delete)} object(s)")
    else:
        print("Nothing to delete.")

def lambda_handler(event=None, context=None):
    print("Fetching population data from Data USA API...")

    response = requests.get(API_URL)
    if response.status_code != 200:
        print(f"API error: {response.status_code}")
        return

    data = response.json()

    # Step 1: Clear existing files under the prefix
    clear_s3_prefix(BUCKET_NAME, S3_PREFIX)

    # Step 2: Upload new data
    print(f"Uploading to s3://{BUCKET_NAME}/{S3_KEY}...")
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=S3_KEY,
        Body=json.dumps(data, indent=2).encode("utf-8"),
        ContentType="application/json"
    )

    print("Upload complete.")

import boto3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import email.utils
from botocore.exceptions import ClientError

# Configuration
SOURCE_URL = "https://download.bls.gov/pub/time.series/pr/"
BUCKET_NAME = "my-bls-data-sync"
PREFIX = ""
REGION = "us-east-1"

s3 = boto3.client("s3", region_name=REGION)


headers = {
    "User-Agent": "BLSSyncBot/1.0 (contact: your.email@example.com)"
}

def fetch_remote_files():
    response = requests.get(SOURCE_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    remote_files = {}
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and not href.endswith("/"):
            file_url = urljoin(SOURCE_URL, href)
            try:
                head = requests.head(file_url, headers=headers)
                etag = head.headers.get("ETag")
                if etag:
                    remote_files[href] = {"url": file_url, "etag": etag.strip('"')}
            except Exception as e:
                print(f"⚠️ Failed HEAD for {href}: {e}")
    return remote_files


def list_s3_etags():
    etag_map = {}
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=PREFIX):
        for obj in page.get('Contents', []):
            key = obj["Key"]
            file_name = key.replace(PREFIX, "")
            try:
                head = s3.head_object(Bucket=BUCKET_NAME, Key=key)
                etag = head.get("ETag", "").strip('"')
                etag_map[file_name] = etag
            except Exception as e:
                print(f"Error reading ETag for {file_name}: {e}")
    return etag_map


def upload_file(file_name, file_url):
    response = requests.get(file_url, headers=headers)
    s3.put_object(Bucket=BUCKET_NAME, Key=f"{PREFIX}{file_name}", Body=response.content)
    print(f"Uploaded: {file_name}")


def delete_file_from_s3(file_name):
    key = f"{PREFIX}{file_name}"
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=key)
        print(f"Deleted: {file_name}")
    except ClientError as e:
        print(f"Failed to delete {file_name}: {e}")


def lambda_handler(event=None, context=None):
    print("🚀 Starting stateless ETag-based sync...")

    remote_files = fetch_remote_files()
    s3_etags = list_s3_etags()

    # Upload new or changed
    for file_name, file_info in remote_files.items():
        remote_etag = file_info["etag"]
        s3_etag = s3_etags.get(file_name)

        if s3_etag != remote_etag:
            print(f"ETag mismatch or new file: {file_name}")
            upload_file(file_name, file_info["url"])
        else:
            print(f"Unchanged: {file_name}")

    # Delete missing files
    for file_name in s3_etags:
        if file_name not in remote_files:
            delete_file_from_s3(file_name)

    print("sync complete.")
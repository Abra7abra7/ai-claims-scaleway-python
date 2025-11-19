import os
import boto3
from mistralai import Mistral
from dotenv import load_dotenv
import sys

# Load .env
load_dotenv()

def check_mistral():
    print("Testing Mistral AI Connection...", end=" ")
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("FAILED: MISTRAL_API_KEY not found in .env")
        return False
    
    try:
        client = Mistral(api_key=api_key)
        # Simple list models call to verify auth
        client.models.list()
        print("SUCCESS")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def check_s3():
    print("Testing Scaleway S3 Connection...", end=" ")
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    bucket_name = os.getenv("S3_BUCKET_NAME")
    endpoint = os.getenv("S3_ENDPOINT_URL")
    region = os.getenv("S3_REGION")

    if not all([access_key, secret_key, bucket_name, endpoint]):
        print("FAILED: Missing S3 variables in .env")
        return False

    try:
        s3 = boto3.client(
            's3',
            region_name=region,
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        # List buckets to verify auth
        s3.list_buckets()
        
        # Check if specific bucket exists
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"SUCCESS (Bucket '{bucket_name}' found)")
            return True
        except Exception:
            print(f"WARNING: Auth OK, but bucket '{bucket_name}' not found or not accessible.")
            return True # Auth is still likely fine
            
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    print("=== Verifying External Connections ===")
    mistral_ok = check_mistral()
    s3_ok = check_s3()
    
    if mistral_ok and s3_ok:
        print("\nAll external connections look good! You can start the app.")
        sys.exit(0)
    else:
        print("\nSome checks failed. Please review your .env file.")
        sys.exit(1)

import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile
from app.core.config import get_settings
import uuid

settings = get_settings()

class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def upload_file(self, file: UploadFile) -> str:
        """
        Uploads a file to S3 and returns the S3 key.
        """
        file_extension = file.filename.split('.')[-1]
        s3_key = f"{uuid.uuid4()}.{file_extension}"
        
        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': file.content_type}
            )
            return s3_key
        except NoCredentialsError:
            raise Exception("S3 Credentials not available")
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def upload_bytes(self, file_content: bytes, s3_key: str, content_type: str = 'application/pdf'):
        """
        Uploads raw bytes to S3 with a specified key.
        """
        try:
            from io import BytesIO
            self.s3_client.upload_fileobj(
                BytesIO(file_content),
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
        except NoCredentialsError:
            raise Exception("S3 Credentials not available")
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def get_file_url(self, s3_key: str) -> str:
        """
        Generates a presigned URL for the file.
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=3600
            )
            return response
        except Exception as e:
            raise Exception(f"Failed to generate URL: {str(e)}")
    
    def generate_presigned_url(self, s3_key: str) -> str:
        """
        Alias for get_file_url for consistency.
        """
        return self.get_file_url(s3_key)
            
    def download_file(self, s3_key: str, local_path: str):
        """
        Downloads a file from S3 to a local path.
        """
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
        except Exception as e:
            raise Exception(f"Failed to download file: {str(e)}")

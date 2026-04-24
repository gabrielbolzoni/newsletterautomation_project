import logging
import boto3
from botocore.exceptions import ClientError
import os


def upload_file(credentials_file,path,bucket_name,object_name):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    aws_key = credentials_file["aws"]["key"]
    aws_secret = credentials_file["aws"]["secret"]
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(path)

    # Upload the file
    s3_client = boto3.client('s3', aws_access_key_id = aws_key,aws_secret_access_key = aws_secret)
    try:
        response = s3_client.upload_file(path, bucket_name, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
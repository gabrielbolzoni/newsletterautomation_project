import logging
import boto3
from botocore.exceptions import ClientError
import os
import json


def upload_file(file_name, bucket, object_name, aws_key, aws_secret):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3', aws_access_key_id = aws_key,aws_secret_access_key = aws_secret)
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


with open("config/credentials/api_keys.json","r") as f:
    credentials_file = json.load(f)

aws_key = credentials_file["aws"]["key"]
aws_secret = credentials_file["aws"]["secret"]
file_name = "data\\audio_files\Deschamps_2025_12_26.mp3"
object_name = "newsLetter_2025_12_26.mp3"
bucket_name = "amzn-s3-news-letter-audios"
upload_file(file_name,bucket_name,object_name,aws_key,aws_secret)
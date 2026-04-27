import logging
import boto3
from botocore.exceptions import ClientError
import os


def upload_file(credentials_file,path,bucket_name,object_name):
    """
    Uploads a local file to an S3 bucket using credentials from a config dict.

    Authenticates with AWS using keys from the credentials file and uploads
    the specified file to the given bucket. If no object name is provided,
    the local filename is used as the S3 key.

    Args:
        credentials_file:
            json file containing the bucket credentials
        path:
            path to the audio file that will be sent to the bucket
        bucket_name:
            name of the bucket the audio will be sent to
        object_name:
            name that the file will have in the bucket

    Returns:
        success: # TODO: describe

    Raises:
        ClientError: # TODO: describe
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
import boto3


def download_files():
    client = boto3.client('s3')
    print(client)

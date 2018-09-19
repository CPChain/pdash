import json
import boto3
from botocore import UNSIGNED
from botocore.config import Config

class Storage:
    data_type = 'file'

    def user_input_param(self):

        return {
            'bucket': 'cpchain-bucket',
            'aws_secret_access_key': 'TlLYyyb6avQvdf8BU0UzEj7P83tbVjSLyv9kTppd',
            'aws_access_key_id': 'AKIAI34GNTRZVNJ5ZMZA',
            'key': 'test'
        }

    def upload_data(self, src, dst):
        aws_access_key_id = dst['aws_access_key_id']
        aws_secret_access_key = dst['aws_secret_access_key']
        bucket = dst['bucket']
        key = dst['key']

        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
            )
        s3.upload_file(src, bucket, key, ExtraArgs={'ACL': 'public-read'})

        file_addr = {
            'bucket': bucket,
            'key': key
        }

        return json.dumps(file_addr)

    def download_data(self, src, dst):
        src = json.loads(src)
        bucket = src['bucket']
        key = src['key']

        s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
        s3.download_file(bucket, key, dst)

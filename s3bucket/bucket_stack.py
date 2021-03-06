from aws_cdk import (
    aws_s3 as s3,
    core as cdk,
)

class BucketStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Simple S3 Bucket
        s3.Bucket(self, 'S3Bucket')


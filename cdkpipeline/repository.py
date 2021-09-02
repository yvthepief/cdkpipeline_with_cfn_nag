
from aws_cdk import (
    aws_codecommit as codecommit,
    core as cdk
)

class RepositoryStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create codecommit repository to store files
        codecommit.Repository(
            self, 'Repository',
            repository_name='cdkpipeline_with_cfn_nag',
            description='Repository for CDK pipeline with CFN Nag'
        )
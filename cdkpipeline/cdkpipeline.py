# importing modules
from aws_cdk import (
    aws_codecommit as codecommit,
    pipelines,
    core as cdk
)
# import s3 bucket stack
from s3bucket.bucket_stack import BucketStack

# Class for creation of the S3Bucket Stage
class S3BucketStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the Bucket Stack, which uses the bucket_stack.py to create a S3 bucket
        s3_bucket = BucketStack(self, "S3BucketStack")

# Class for the CDK pipeline stack
class CdkPipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Use created repository by name, basically import the repository created via cdk deploy SourceRepository
        repository = codecommit.Repository.from_repository_name(self, 'pipeline_repository', 'cdkpipeline_with_cfn_nag')

        # Create CDK pipeline
        pipeline = pipelines.CodePipeline(
            self, "CDKPipeline", 
            pipeline_name="CDKPipeline",

            # Synthezise and check all templates within cdk.out directory with cfn_nag
            synth=pipelines.ShellStep("Synth",
                # Point source to codecommit repository
                input=pipelines.CodePipelineSource.code_commit(repository, "main"),

                # Actual commands used in the CodeBuild build.
                commands=[
                    "npm install -g aws-cdk",
                    "gem install cfn-nag",
                    "pip install -r requirements.txt",
                    "cdk synth",
                    "mkdir ./cfnnag_output",
                    "for template in $(find ./cdk.out -type f -maxdepth 2 -name '*.template.json'); do cp $template ./cfnnag_output; done",
                    "cfn_nag_scan --input-path ./cfnnag_output",
                ]
            )
        )

        # Deploy the S3 Bucket Stage
        s3Deplpoy = pipeline.add_stage(
            S3BucketStage(
                self, 'S3BucketStage',
                # env=cdk.Environment(
                #     account="290794210101", 
                #     region="eu-west-1"
                # )
            )
        )
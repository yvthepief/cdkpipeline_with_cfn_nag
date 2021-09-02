from aws_cdk import (
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    pipelines,
    core as cdk
)
from s3bucket.bucket_stack import BucketStack

class S3BucketStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_bucket = BucketStack(self, "S3BucketStack")

class CdkPipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Use created repository by name
        repository = codecommit.Repository.from_repository_name(self, 'pipeline_repository', 'cdkpipeline_with_cfn_nag')

        # Create artifacts
        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        # Configure cdk pipeline
        pipeline = pipelines.CodePipeline(
            self, "CDKPipeline", 
            pipeline_name="CDKPipeline",
            self_mutating=True,

            # Point source to codecommit repository
            source_action=codepipeline_actions.CodeCommitSourceAction(
                action_name='CodeCommit',
                branch='main',
                output=source_artifact,
                repository=repository
            ),

            # Synthezise and check all templates within cdk.out directory with cfn_nag
            synth_action=pipelines.SimpleSynthAction(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                install_command="npm install -g aws-cdk && gem install cfn-nag && pip install -r requirements.txt",
                synth_command="cdk synth && for template in $(find ./cdk.out -type f -maxdepth 2 -name '*.template.json'); do cfn_nag_scan --input-path $template; done",
                environment=codebuild.BuildEnvironment(
                    build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                ),
            ),
        ),

        # Creating DAAN Secure logging and scripts secure buckets
        deployS3 = pipeline.add_application_stage(
            S3BucketStage(
                self, 'TestAccount',
                removal_policy='RETAIN',
                env=cdk.Environment(account="111111111111", region="eu-west-1")
            )
        )


import pandas as pd

from zenml import pipelines
from zenml import steps
from zenml.annotations import External, Input, Step, Param
from zenml.artifacts import TextArtifact
from zenml.distributed.beam import BeamOutput
from zenml.steps import MultiOutput


class SplitStepOutput(MultiOutput):
    data: TextArtifact
    param: float


@steps.SimpleStep
def DistSplitStep(input_data: Input[TextArtifact],
                  param: Param[float] = 3.0,
                  ) -> SplitStepOutput:
    import apache_beam as beam

    with beam.Pipeline() as pipeline:
        data = input_data.read_with_beam(pipeline)
        result = data | beam.Map(lambda x: x)

    return SplitStepOutput(data=result, param=param)


@steps.SimpleStep
def InMemPreprocesserStep(input_data: Input[TextArtifact]
                          ) -> [pd.DataFrame]:
    data = input_data.read_with_pandas()
    return data


@pipelines.SimplePipeline
def SplitPipeline(input_artifact: External[TextArtifact],
                  split_step: Step[DistSplitStep],
                  preprocesser_step: Step[InMemPreprocesserStep]):
    split_data, param = split_step(input_data=input_artifact)
    _ = preprocesser_step(input_data=split_data)


# Pipeline
test_artifact = TextArtifact()
test_artifact.uri = "/home/baris/zenml/zenml/zenml/local_test/data/data.csv"

dist_split_pipeline = SplitPipeline(
    input_artifact=test_artifact,
    split_step=DistSplitStep(param=0.1),
    preprocesser_step=InMemPreprocesserStep()
)

dist_split_pipeline.run()

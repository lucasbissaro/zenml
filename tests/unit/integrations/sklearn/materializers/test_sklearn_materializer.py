#  Copyright (c) ZenML GmbH 2022. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
from contextlib import ExitStack as does_not_raise

from sklearn.base import ClassifierMixin
from sklearn.svm import SVC

from tests.unit.test_general import _test_materializer
from zenml.integrations.sklearn.materializers.sklearn_materializer import (
    SklearnMaterializer,
)


def test_sklearn_materializer(clean_client):
    """Tests whether the steps work for the Sklearn materializer."""

    with does_not_raise():
        _test_materializer(
            step_output=SVC(gamma="auto"),
            materializer=SklearnMaterializer,
        )

    last_run = clean_client.get_pipeline("test_pipeline").runs[-1]
    model = last_run.steps[-1].output.read()
    assert isinstance(model, ClassifierMixin)
    assert model.gamma == "auto"
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
"""Implementation of Neptune Experiment Tracker."""

from typing import TYPE_CHECKING, Any, Optional, Type, cast

from zenml.client import Client
from zenml.experiment_trackers.base_experiment_tracker import (
    BaseExperimentTracker,
)
from zenml.integrations.neptune.experiment_trackers.run_state import RunProvider
from zenml.integrations.neptune.flavors import (
    NeptuneExperimentTrackerConfig,
    NeptuneExperimentTrackerSettings,
)

if TYPE_CHECKING:
    from zenml.config.base_settings import BaseSettings
    from zenml.config.step_run_info import StepRunInfo


class NeptuneExperimentTracker(BaseExperimentTracker):
    """Track experiments using neptune.ai."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the experiment tracker.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.run_state: RunProvider = RunProvider()

    @staticmethod
    def _is_last_step(info: "StepRunInfo") -> bool:
        """Check whether the current step is the last step of the pipeline.

        Args:
            info: Info about the step that was executed.

        Returns:
            flag whether the current step is the last one in the pipeline
        """
        pipeline_name = info.pipeline.name
        step_name = info.config.name
        client = Client()

        current_pipeline = client.get_pipeline(pipeline_name)
        last_step = current_pipeline.spec.steps[-1]
        last_step_name = last_step.source.split(".")[-1]

        return step_name == last_step_name

    @property
    def config(self) -> NeptuneExperimentTrackerConfig:
        """Returns the `NeptuneExperimentTrackerConfig` config.

        Returns:
            The configuration.
        """
        return cast(NeptuneExperimentTrackerConfig, self._config)

    @property
    def settings_class(self) -> Optional[Type["BaseSettings"]]:
        """Settings class for the Neptune experiment tracker.

        Returns:
            The settings class.
        """
        return NeptuneExperimentTrackerSettings

    def prepare_step_run(self, info: "StepRunInfo") -> None:
        """Initializes a Neptune run and stores it in the run_state object.

        The run object can then be accessed later from other places, such as a step.

        Args:
            info: Info about the step that was executed.
        """
        settings = cast(
            NeptuneExperimentTrackerSettings, self.get_settings(info)
        )

        self.run_state.token = self.config.api_token
        self.run_state.project = self.config.project
        self.run_state.run_name = info.run_name
        self.run_state.tags = list(settings.tags)

    def cleanup_step_run(self, info: "StepRunInfo") -> None:
        """If the current step is the last step of the pipeline, stop the Neptune run.

        Args:
            info: Info about the step that was executed.
        """
        if self._is_last_step(info):
            self.run_state.active_run.sync()
            self.run_state.active_run.stop()
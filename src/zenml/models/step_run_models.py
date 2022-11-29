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
"""Models representing steps of pipeline runs."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from zenml.config.step_configurations import Step
from zenml.enums import ExecutionStatus
from zenml.models.base_models import (
    BaseRequestModel,
    BaseResponseModel,
    update_model,
)
from zenml.models.constants import MODEL_NAME_FIELD_MAX_LENGTH

# ---- #
# BASE #
# ---- #


class StepRunBaseModel(BaseModel):
    """Base model for step runs."""

    name: str = Field(
        title="The name of the pipeline run step.",
        max_length=MODEL_NAME_FIELD_MAX_LENGTH,
    )
    step: Step
    pipeline_run_id: UUID
    status: ExecutionStatus
    parent_step_ids: List[UUID] = []
    input_artifacts: Dict[str, UUID] = {}
    output_artifacts: Dict[str, UUID] = {}
    cache_key: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


# -------- #
# RESPONSE #
# -------- #


class StepRunResponseModel(StepRunBaseModel, BaseResponseModel):
    """Response model for step runs."""


# ------- #
# REQUEST #
# ------- #


class StepRunRequestModel(StepRunBaseModel, BaseRequestModel):
    """Request model for step runs."""


# ------ #
# UPDATE #
# ------ #
@update_model
class StepRunUpdateModel(StepRunRequestModel):
    """Update model for step runs."""
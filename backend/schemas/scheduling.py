from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ScheduleProposalRequest(BaseModel):
    scheduled_start: datetime
    scheduled_end: datetime

    timezone: str = Field(
        default="UTC",
        min_length=1,
        max_length=100,
    )

    @model_validator(mode="after")
    def validate_times(self):
        if self.scheduled_end <= self.scheduled_start:
            raise ValueError(
                "scheduled_end must be after scheduled_start."
            )

        return self


class ScheduleApprovalRequest(BaseModel):
    approved: bool
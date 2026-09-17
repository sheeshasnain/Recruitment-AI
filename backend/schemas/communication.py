from typing import Literal

from pydantic import BaseModel, Field


class CommunicationDraftRequest(BaseModel):
    communication_type: Literal[
        "interview_invitation",
        "interview_reminder",
        "follow_up",
    ]


class CommunicationApprovalRequest(BaseModel):
    approved: bool


class EmailDraft(BaseModel):
    subject: str = Field(
        ...,
        min_length=3,
        max_length=500,
    )

    body: str = Field(
        ...,
        min_length=10,
        max_length=10000,
    )
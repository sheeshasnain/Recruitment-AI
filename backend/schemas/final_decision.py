from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


class FinalDecisionRequest(
    BaseModel
):
    decision: Literal[
        "hire",
        "reject",
        "hold",
    ]

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )
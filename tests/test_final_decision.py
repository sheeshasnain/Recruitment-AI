import pytest
from pydantic import ValidationError

from backend.schemas.final_decision import (
    FinalDecisionRequest,
)


def test_valid_hire_decision():
    request = FinalDecisionRequest(
        decision="hire",
        notes="Approved.",
    )

    assert request.decision == "hire"


def test_valid_hold_decision():
    request = FinalDecisionRequest(
        decision="hold",
    )

    assert request.decision == "hold"


def test_invalid_final_decision():
    with pytest.raises(
        ValidationError
    ):
        FinalDecisionRequest(
            decision="maybe"
        )
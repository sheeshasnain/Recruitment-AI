from datetime import datetime, timezone

import pytest

from backend.schemas.scheduling import (
    ScheduleProposalRequest,
)


def test_valid_schedule():

    payload = ScheduleProposalRequest(
        scheduled_start=datetime(
            2026,
            9,
            20,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        scheduled_end=datetime(
            2026,
            9,
            20,
            11,
            0,
            tzinfo=timezone.utc,
        ),
        timezone="UTC",
    )

    assert (
        payload.scheduled_end
        > payload.scheduled_start
    )


def test_invalid_schedule():

    with pytest.raises(ValueError):

        ScheduleProposalRequest(
            scheduled_start=datetime(
                2026,
                9,
                20,
                11,
                0,
                tzinfo=timezone.utc,
            ),
            scheduled_end=datetime(
                2026,
                9,
                20,
                10,
                0,
                tzinfo=timezone.utc,
            ),
            timezone="UTC",
        )
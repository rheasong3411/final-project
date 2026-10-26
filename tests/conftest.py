"""Shared fixtures. All profiles in tests are SYNTHETIC (invented for testing, not real people)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.data import get_dataset  # noqa: E402
from backend.matching import assess  # noqa: E402
from backend.schemas import VolunteerProfile  # noqa: E402


@pytest.fixture(scope="session")
def ds():
    return get_dataset()


@pytest.fixture
def run(ds):
    def _run(opportunity_id, **profile):
        return assess(ds, ds.opportunities[opportunity_id], VolunteerProfile(**profile))
    return _run


def item(assessment, requirement):
    found = [r for r in assessment.requirements if r.requirement == requirement]
    return found[0] if found else None


"""Tests for the classifier. No git required."""

from mute.classify import classify_suppression
from mute.models import Suppression


def _supp(reason="", age_days=0):
    s = Suppression(file="x.py", line=1, test_name="t", kind="skip", reason=reason)
    s.age_days = age_days
    return s


def test_broken_no_reason():
    s = classify_suppression(_supp(reason="", age_days=5), cwd="/tmp/nonexistent_repo")
    assert s.verdict == "broken"


def test_broken_no_issue():
    s = classify_suppression(_supp(reason="flaky", age_days=5), cwd="/tmp/nonexistent_repo")
    assert s.verdict == "broken"


def test_healthy_with_reason_and_issue():
    s = classify_suppression(_supp(reason="flaky, see #1", age_days=5), cwd="/tmp/nonexistent_repo")
    assert s.verdict == "healthy"


def test_aging_30_to_90_days():
    s = classify_suppression(_supp(reason="flaky, see #1", age_days=45), cwd="/tmp/nonexistent_repo")
    assert s.verdict == "aging"


def test_ancient_over_90_days():
    s = classify_suppression(_supp(reason="flaky, see #1", age_days=120), cwd="/tmp/nonexistent_repo")
    assert s.verdict == "ancient"


def test_issue_extracted():
    s = classify_suppression(_supp(reason="see #1 and GH-2", age_days=5), cwd="/tmp/nonexistent_repo")
    assert "#1" in s.issue_refs
    assert "GH-2" in s.issue_refs

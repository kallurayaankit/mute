
"""Tests for issue extraction."""

from mute.issues import extract_issue_refs


def test_hash_number():
    assert extract_issue_refs("flaky, see #123") == ["#123"]


def test_gh_number():
    assert extract_issue_refs("tracking GH-456") == ["GH-456"]


def test_jira_number():
    assert extract_issue_refs("tracked in JIRA-12") == ["JIRA-12"]


def test_multiple_issues():
    refs = extract_issue_refs("see #1 and GH-2 for context")
    assert "#1" in refs
    assert "GH-2" in refs


def test_empty():
    assert extract_issue_refs("") == []


def test_no_issue():
    assert extract_issue_refs("flaky, investigate later") == []


def test_wrong_format():
    # 123 alone is not an issue reference
    assert extract_issue_refs("tried 123 times") == []


"""Demo tests showing every kind of suppression mute detects."""

import pytest


def test_normal():
    assert 1 + 1 == 2


@pytest.mark.skip(reason="flaky on CI, tracking in #123")
def test_skipped_with_reason():
    assert False


@pytest.mark.skip(reason="broken, see #999")
def test_skipped_with_issue():
    assert False


@pytest.mark.skip
def test_skipped_no_reason():
    assert False


@pytest.mark.xfail(reason="known bug #456")
def test_xfail_with_reason():
    assert False


@pytest.mark.xfail
def test_xfail_no_reason():
    assert False


@pytest.mark.skipif(True, reason="temporary, see #777")
def test_skipif_with_reason():
    assert False


@pytest.mark.xfail(strict=False, reason="inconsistent, tracking in JIRA-12")
def test_xfail_non_strict():
    assert False

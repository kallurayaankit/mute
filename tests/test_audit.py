
"""End-to-end audit test against the demo tests."""

from mute.classify import audit


def test_audit_demo():
    report = audit("examples/demo_tests", cwd=".")
    assert report.total == 7
    assert report.without_reason >= 2
    assert report.without_issue >= 2


def test_audit_broken_count():
    report = audit("examples/demo_tests", cwd=".")
    # 2 tests have no reason at all -> broken
    assert report.broken >= 2

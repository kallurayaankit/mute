
"""Tests for the AST parser. No git, no network."""

from mute.parser import parse_file, parse_directory


DEMO = "examples/demo_tests/test_demo.py"


def test_parse_file_finds_all():
    suppressions = parse_file(DEMO)
    # 7 marked suppressions (1 normal test has none)
    assert len(suppressions) == 7


def test_kinds_are_detected():
    kinds = {s.kind for s in parse_file(DEMO)}
    assert "skip" in kinds
    assert "skipif" in kinds
    assert "xfail" in kinds


def test_reason_extracted():
    suppressions = parse_file(DEMO)
    with_reason = [s for s in suppressions if s.has_reason]
    assert len(with_reason) >= 4


def test_no_reason_detected():
    suppressions = parse_file(DEMO)
    no_reason = [s for s in suppressions if not s.has_reason]
    assert len(no_reason) >= 2


def test_test_names_captured():
    names = {s.test_name for s in parse_file(DEMO)}
    assert "test_skipped_with_reason" in names
    assert "test_xfail_no_reason" in names


def test_line_numbers():
    suppressions = parse_file(DEMO)
    for s in suppressions:
        assert s.line > 0


def test_parse_directory():
    suppressions = parse_directory("examples/demo_tests")
    assert len(suppressions) == 7


def test_parse_missing_directory():
    try:
        parse_directory("does/not/exist")
        assert False, "should have raised"
    except FileNotFoundError:
        pass

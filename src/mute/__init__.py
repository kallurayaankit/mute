"""mute - find the tests your suite is quietly hiding."""

from mute.models import Suppression, Report, Kind, Verdict
from mute.parser import parse_file, parse_directory
from mute.issues import extract_issue_refs
from mute.gitblame import blame_line, is_repo, age_days
from mute.classify import audit, classify_all, classify_suppression
from mute.report import render_report

__version__ = "0.1.0"

__all__ = [
    "Suppression", "Report", "Kind", "Verdict",
    "parse_file", "parse_directory",
    "extract_issue_refs", "blame_line", "is_repo", "age_days",
    "audit", "classify_all", "classify_suppression", "render_report",
]

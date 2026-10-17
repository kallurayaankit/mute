
"""Classify each suppression by age, reason, and issue tracking."""

import os

from dotenv import load_dotenv

from mute.gitblame import age_days, blame_line, is_repo
from mute.issues import extract_issue_refs
from mute.models import Report, Suppression, Verdict
from mute.parser import parse_directory

load_dotenv()


def _max_age():
    return int(os.getenv("MUTE_MAX_AGE_DAYS", "90"))


def _aging_age():
    return int(os.getenv("MUTE_AGING_DAYS", "30"))


def classify_suppression(supp, cwd="."):
    """Enrich a Suppression with blame, issues, age, and verdict."""
    if is_repo(cwd):
        sha, author, date_iso = blame_line(supp.file, supp.line, cwd=cwd)
        supp.added_by = author or ""
        supp.added_date = date_iso or ""
        supp.age_days = age_days(date_iso)

    supp.issue_refs = extract_issue_refs(supp.reason)

    if not supp.has_reason or not supp.has_issue:
        supp.verdict = Verdict.BROKEN.value
    elif supp.age_days > _max_age():
        supp.verdict = Verdict.ANCIENT.value
    elif supp.age_days > _aging_age():
        supp.verdict = Verdict.AGING.value
    else:
        supp.verdict = Verdict.HEALTHY.value

    return supp


def classify_all(suppressions, cwd="."):
    """Classify every suppression and build a Report."""
    for s in suppressions:
        classify_suppression(s, cwd=cwd)

    report = Report()
    report.suppressions = suppressions
    report.total = len(suppressions)

    for s in suppressions:
        if s.verdict == Verdict.HEALTHY.value:
            report.healthy += 1
        elif s.verdict == Verdict.AGING.value:
            report.aging += 1
        elif s.verdict == Verdict.ANCIENT.value:
            report.ancient += 1
        else:
            report.broken += 1

        if not s.has_reason:
            report.without_reason += 1
        if not s.has_issue:
            report.without_issue += 1

    return report


def audit(tests_dir, cwd="."):
    suppressions = parse_directory(tests_dir)
    return classify_all(suppressions, cwd=cwd)

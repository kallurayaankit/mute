
"""Extract issue references from a reason string."""

import re


# Patterns for common trackers
PATTERNS = [
    re.compile(r"(?<![A-Za-z0-9])#(\d+)"),               # #123
    re.compile(r"(?<![A-Za-z0-9])GH-(\d+)", re.I),       # GH-123
    re.compile(r"(?<![A-Za-z0-9])JIRA-(\d+)", re.I),     # JIRA-123
    re.compile(r"(?<![A-Za-z0-9])ISSUE-(\d+)", re.I),    # ISSUE-123
    re.compile(r"(?<![A-Za-z0-9])BUG-(\d+)", re.I),      # BUG-123
]


def extract_issue_refs(reason):
    """Return a list of issue identifiers found in the reason string."""
    if not reason:
        return []
    refs = []
    for pat in PATTERNS:
        for m in pat.finditer(reason):
            match_text = m.group(0).strip()
            if match_text not in refs:
                refs.append(match_text)
    return refs

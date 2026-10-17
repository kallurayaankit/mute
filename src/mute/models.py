
"""Data model for mute."""

from dataclasses import dataclass, field, asdict
from enum import Enum


class Kind(str, Enum):
    SKIP = "skip"
    SKIPIF = "skipif"
    XFAIL = "xfail"
    FLAKY = "flaky"           # retry markers
    UNKNOWN = "unknown"


class Verdict(str, Enum):
    HEALTHY = "healthy"       # has reason + issue, < 30 days
    AGING = "aging"           # has reason + issue, 30-90 days
    ANCIENT = "ancient"       # has reason + issue, > 90 days
    BROKEN = "broken"         # missing reason or issue


@dataclass
class Suppression:
    file: str
    line: int
    test_name: str
    kind: str = Kind.UNKNOWN.value
    reason: str = ""
    issue_refs: list = field(default_factory=list)
    added_date: str = ""
    added_by: str = ""
    age_days: int = 0
    verdict: str = Verdict.BROKEN.value

    @property
    def has_reason(self):
        return bool(self.reason and self.reason.strip())

    @property
    def has_issue(self):
        return len(self.issue_refs) > 0

    def to_dict(self):
        d = asdict(self)
        d["has_reason"] = self.has_reason
        d["has_issue"] = self.has_issue
        return d


@dataclass
class Report:
    total: int = 0
    healthy: int = 0
    aging: int = 0
    ancient: int = 0
    broken: int = 0
    without_reason: int = 0
    without_issue: int = 0
    suppressions: list = field(default_factory=list)

    def to_dict(self):
        return {
            "total": self.total,
            "healthy": self.healthy,
            "aging": self.aging,
            "ancient": self.ancient,
            "broken": self.broken,
            "without_reason": self.without_reason,
            "without_issue": self.without_issue,
            "suppressions": [s.to_dict() for s in self.suppressions],
        }

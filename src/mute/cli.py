
"""CLI: mute audit <tests-dir>"""

import argparse
import json
import sys
from pathlib import Path

from mute import __version__
from mute.classify import audit
from mute.report import render_report


ORDER = ["broken", "ancient", "aging", "healthy"]


def cmd_audit(args):
    try:
        report = audit(args.tests_dir, cwd=args.cwd)
    except Exception as e:
        print("error: " + str(e), file=sys.stderr)
        sys.exit(2)

    if report.total == 0:
        print("No suppressions found in " + args.tests_dir)
        return

    print()
    print("Found " + str(report.total) + " suppressions in the test suite.")
    print()

    # Group by verdict, in priority order
    by_verdict = {}
    for s in report.suppressions:
        by_verdict.setdefault(s.verdict, []).append(s)

    for verdict in ORDER:
        items = by_verdict.get(verdict, [])
        if not items:
            continue
        print("=== " + verdict.upper() + " (" + str(len(items)) + ") ===")
        for s in items:
            print("  " + s.file + "::" + s.test_name)
            print("    kind:      " + s.kind)
            print("    reason:    " + (s.reason if s.reason else "(none)"))
            if s.issue_refs:
                print("    issues:    " + ", ".join(s.issue_refs))
            if s.added_by:
                print("    added:     " + s.added_date + " by " + s.added_by)
            if s.age_days > 0:
                print("    age:       " + str(s.age_days) + " days")
            print()

    print("=== STATS ===")
    print("  Total suppressions:     " + str(report.total))
    print("  Without a reason:       " + str(report.without_reason))
    print("  Without a linked issue: " + str(report.without_issue))
    print("  Broken:                 " + str(report.broken))
    print("  Ancient (>90 days):     " + str(report.ancient))
    print("  Aging (30-90 days):     " + str(report.aging))
    print("  Healthy (<30 days):     " + str(report.healthy))
    print()

    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        print("JSON: " + args.json)

    if args.html or args.open:
        html_path = render_report(report, args.html)
        print("HTML: " + html_path)
        if args.open:
            import webbrowser
            webbrowser.open("file:///" + str(Path(html_path).resolve()))

    if (report.broken + report.ancient) > 0 and args.fail_on_problems:
        sys.exit(1)


def cmd_version(args):
    print("mute " + __version__)


def main():
    parser = argparse.ArgumentParser(
        prog="mute",
        description="Find the tests your suite is quietly hiding",
    )
    parser.add_argument("--version", action="version", version="mute " + __version__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("audit", help="find every suppression in a test directory")
    p.add_argument("tests_dir", help="directory of test files to audit")
    p.add_argument("--cwd", default=".", help="path to git repo (default: current dir)")
    p.add_argument("--json", help="write JSON results here")
    p.add_argument("--html", help="write HTML report here")
    p.add_argument("--open", action="store_true", help="open HTML in browser")
    p.add_argument("--fail-on-problems", action="store_true",
                   help="exit 1 if any BROKEN or ANCIENT suppressions exist")
    p.set_defaults(func=cmd_audit)

    pv = sub.add_parser("version")
    pv.set_defaults(func=cmd_version)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

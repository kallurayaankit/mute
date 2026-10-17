
"""AST parser: find suppression decorators in Python test files."""

import ast
from pathlib import Path

from mute.models import Kind, Suppression


# Decorator name fragments we look for
SKIP_NAMES = {"skip"}
SKIPIF_NAMES = {"skipif"}
XFAIL_NAMES = {"xfail"}
FLAKY_NAMES = {"flaky", "retry", "rerun", "reruns"}


def _decorator_name(node):
    """Extract the short name of a decorator, e.g. 'skip' from 'pytest.mark.skip'."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return ""


def _kind_for(name):
    low = name.lower()
    if low in SKIPIF_NAMES:
        return Kind.SKIPIF.value
    if low in SKIP_NAMES:
        return Kind.SKIP.value
    if low in XFAIL_NAMES:
        return Kind.XFAIL.value
    if low in FLAKY_NAMES:
        return Kind.FLAKY.value
    return None


def _extract_reason(node):
    """Given a decorator node, extract the 'reason' string if present."""
    if not isinstance(node, ast.Call):
        return ""

    for kw in node.keywords:
        if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
            val = kw.value.value
            if isinstance(val, str):
                return val

    # Positional arg fallback (skip("my reason"))
    for arg in node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value

    return ""


def parse_file(path):
    """Return a list of Suppression objects found in one file."""
    path = Path(path)
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return []

    results = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        for dec in node.decorator_list:
            name = _decorator_name(dec)
            kind = _kind_for(name)
            if kind is None:
                continue

            reason = _extract_reason(dec)

            results.append(Suppression(
                file=str(path).replace("\\", "/"),
                line=node.lineno,
                test_name=node.name,
                kind=kind,
                reason=reason,
            ))

    return results


def parse_directory(directory):
    """Walk a directory and find all suppressions."""
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError("directory not found: " + str(directory))

    all_suppressions = []
    for py_file in sorted(directory.rglob("*.py")):
        all_suppressions.extend(parse_file(py_file))
    return all_suppressions

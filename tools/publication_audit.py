"""Deterministic, redacted audit for a proposed public dataset tree."""
import json
import re
import subprocess
import argparse
import hashlib

from tools.validate import ROOT

EXCLUDED_TOP_LEVEL = {".git", ".venv", "work", "dist", "__pycache__"}
TEXT_SUFFIXES = {".md", ".json", ".yml", ".yaml", ".py", ".txt", ".csv"}
RULES = {
    "private_absolute_path": re.compile(r"/(?:Users|Volumes|private)/"),
    "credential_token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|Bearer\\s+[A-Za-z0-9._-]{12,}|eyJ[A-Za-z0-9_-]{8,}\\.)", re.I),
    "private_key_material": re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
}


def _included(path):
    relative = path.relative_to(ROOT)
    return not any(part in EXCLUDED_TOP_LEVEL for part in relative.parts) and path.suffix in TEXT_SUFFIXES


def _content_scannable(relative):
    return relative in {"README.md", "CONTRIBUTING.md", "LICENSE", "LICENSE-DATA.md", ".gitignore"} or relative.startswith(("data/", "docs/", "fixtures/", "protocols/", "reports/", ".github/"))


def _status():
    rows = subprocess.run(["git", "status", "--porcelain=v1", "-uall"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    changed = {row[3:]: row[:2] for row in rows if len(row) >= 4}
    tracked = set(subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines())
    return tracked, changed


def audit(exclude_from_hash=()):
    tracked, changed = _status()
    paths = sorted(path for path in ROOT.rglob("*") if path.is_file() and _included(path))
    findings, missing_attribution, attributed_records = [], [], 0
    for path in paths:
        relative = str(path.relative_to(ROOT))
        text = path.read_text(errors="replace")
        if _content_scannable(relative):
            for rule, pattern in RULES.items():
                lines = [number for number, line in enumerate(text.splitlines(), 1) if pattern.search(line)]
                if lines:
                    findings.append({"path": relative, "rule": rule, "lines": lines, "redacted": True})
        if relative.startswith("data/") and path.suffix == ".json":
            record = json.loads(text)
            attributed_records += 1
            if "provenance" not in record and "source" not in record and "source_repository" not in record:
                missing_attribution.append(relative)
    candidate_files = {"tracked": sorted(path for path in tracked if (ROOT / path).is_file() and _included(ROOT / path)), "untracked": sorted(path for path in changed if changed[path] == "??" and (ROOT / path).is_file() and _included(ROOT / path)), "modified": sorted(path for path in changed if changed[path] != "??" and (ROOT / path).is_file() and _included(ROOT / path))}
    manifest = sorted(set().union(*candidate_files.values()))
    excluded = sorted(set(exclude_from_hash))
    return {"schema_version": 1, "report_type": "publication_audit", "candidate_files": candidate_files, "file_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in manifest if path not in excluded}, "dynamic_artifacts_excluded_from_hash": excluded, "excluded_patterns": [".venv/**", "work/**", "dist/**", "**/__pycache__/**", "*.log", "*.trace"], "findings": findings, "third_party_attribution": {"checked_data_records": attributed_records, "missing_provenance_or_source": missing_attribution}, "safe_for_review": not findings and not missing_attribution}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    payload = json.dumps(audit([args.output] if args.output else ()), indent=2) + "\n"
    if args.output:
        (ROOT / args.output).write_text(payload)
    print(payload)

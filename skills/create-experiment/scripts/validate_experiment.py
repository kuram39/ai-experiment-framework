#!/usr/bin/env python3
"""Validate durable experiment conventions without mutating the experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlsplit


NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_([a-z0-9]+(?:-[a-z0-9]+)*)$")
RUN_RE = re.compile(r"^\d{8}-\d{6}_[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_RE = re.compile(r"{{[^{}]+}}")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
QUESTION_RE = re.compile(r"^## Q\d+\b", re.MULTILINE)
SELF_CHECK_RE = re.compile(
    r"^### (?:Předpoklady a self-check|Assumptions and self-check)\s*$", re.MULTILINE
)
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".toml", ".txt"}
SKIP_WALK = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
FORBIDDEN_PATTERNS = (
    re.compile(r"-final(?:-|\.|$)"),
    re.compile(r"-final-v\d+"),
    re.compile(r"^latest-"),
    re.compile(r"^new-"),
    re.compile(r"-summary-2(?:\.|$)"),
)
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
STATE_ROLES = {"current_input", "canonical_output", "work_queue", "config", "code"}


@dataclass(frozen=True)
class Issue:
    level: str
    location: str
    message: str


def iter_tree(root: Path):
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        dirnames[:] = [
            name
            for name in dirnames
            if name not in SKIP_WALK and not (current_path / name).is_symlink()
        ]
        yield current_path, dirnames, filenames


def check_local_links(root: Path, source: Path, text: str) -> list[Issue]:
    issues: list[Issue] = []
    for raw_target in LINK_RE.findall(text):
        stripped = raw_target.strip()
        if stripped.startswith("<") and ">" in stripped:
            target_text = stripped[1 : stripped.index(">")]
        else:
            target_text = stripped.split(maxsplit=1)[0]
        if not target_text or target_text.startswith("#"):
            continue
        parsed = urlsplit(target_text)
        if parsed.scheme or parsed.netloc:
            continue
        relative = unquote(parsed.path)
        if not relative:
            continue
        target = Path(relative)
        resolved = target if target.is_absolute() else source.parent / target
        if not resolved.exists():
            issues.append(
                Issue("ERROR", str(source.relative_to(root)), f"broken local link: {relative}")
            )
    return issues


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def state_path(root: Path, raw: object, location: str) -> tuple[Path | None, list[Issue]]:
    issues: list[Issue] = []
    if not isinstance(raw, str) or not raw.strip():
        return None, [Issue("ERROR", location, "must be a non-empty experiment-relative path")]
    candidate = Path(raw)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None, [Issue("ERROR", location, "must not be absolute or escape the experiment")]
    normalized = Path(*[part for part in candidate.parts if part not in {"", "."}])
    if not normalized.parts:
        return None, [Issue("ERROR", location, "must identify a path inside the experiment")]
    return root / normalized, issues


def validate_state(root: Path, state_file: Path) -> list[Issue]:
    issues: list[Issue] = []
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [Issue("ERROR", "STATE.json", f"cannot parse JSON: {exc}")]

    if not isinstance(state, dict):
        return [Issue("ERROR", "STATE.json", "top level must be an object")]
    if state.get("schema_version") != 1:
        issues.append(Issue("ERROR", "STATE.json.schema_version", "must equal 1"))
    for field in ("updated_at", "phase", "next_action"):
        if not isinstance(state.get(field), str) or not state[field].strip():
            issues.append(Issue("ERROR", f"STATE.json.{field}", "must be a non-empty string"))

    blockers = state.get("blockers")
    if not isinstance(blockers, list) or any(
        not isinstance(item, str) or not item.strip() for item in blockers
    ):
        issues.append(
            Issue("ERROR", "STATE.json.blockers", "must be an array of non-empty strings")
        )

    if "current_run" not in state:
        issues.append(
            Issue("ERROR", "STATE.json.current_run", "must be present; use null when no run owns the state")
        )
    current_run = state.get("current_run")
    if current_run is not None:
        run_path, path_issues = state_path(root, current_run, "STATE.json.current_run")
        issues.extend(path_issues)
        if run_path is not None:
            try:
                relative = run_path.relative_to(root)
            except ValueError:
                relative = Path()
            if not relative.parts or relative.parts[0] != "runs":
                issues.append(
                    Issue("ERROR", "STATE.json.current_run", "must point under runs/")
                )
            elif not run_path.is_dir():
                issues.append(
                    Issue("ERROR", "STATE.json.current_run", f"run directory does not exist: {current_run}")
                )

    artifacts = state.get("current_artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        issues.append(
            Issue("ERROR", "STATE.json.current_artifacts", "must be a non-empty array")
        )
        return issues

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, artifact in enumerate(artifacts):
        label = f"STATE.json.current_artifacts[{index}]"
        if not isinstance(artifact, dict):
            issues.append(Issue("ERROR", label, "must be an object"))
            continue
        artifact_id = artifact.get("id")
        if not isinstance(artifact_id, str) or not ID_RE.fullmatch(artifact_id):
            issues.append(Issue("ERROR", f"{label}.id", "must be lowercase kebab-case"))
        elif artifact_id in seen_ids:
            issues.append(Issue("ERROR", f"{label}.id", f"duplicate id: {artifact_id}"))
        else:
            seen_ids.add(artifact_id)

        role = artifact.get("role")
        if role not in STATE_ROLES:
            issues.append(
                Issue("ERROR", f"{label}.role", f"must be one of {sorted(STATE_ROLES)}")
            )

        if "produced_by" not in artifact:
            issues.append(
                Issue(
                    "ERROR",
                    f"{label}.produced_by",
                    "must be present; use null for an externally supplied artifact",
                )
            )

        artifact_path, path_issues = state_path(root, artifact.get("path"), f"{label}.path")
        issues.extend(path_issues)
        if artifact_path is not None:
            raw_path = artifact.get("path")
            if isinstance(raw_path, str) and raw_path in seen_paths:
                issues.append(Issue("ERROR", f"{label}.path", f"duplicate path: {raw_path}"))
            elif isinstance(raw_path, str):
                seen_paths.add(raw_path)
            if not artifact_path.is_file():
                issues.append(
                    Issue("ERROR", f"{label}.path", f"current artifact does not exist: {raw_path}")
                )

        expected_sha = artifact.get("sha256")
        if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha):
            issues.append(Issue("ERROR", f"{label}.sha256", "must be lowercase SHA-256"))
        elif artifact_path is not None and artifact_path.is_file():
            actual_sha = sha256_file(artifact_path)
            if actual_sha != expected_sha:
                issues.append(
                    Issue(
                        "ERROR",
                        f"{label}.sha256",
                        f"hash drift for {artifact.get('path')}: expected {expected_sha}, got {actual_sha}",
                    )
                )

        produced_by = artifact.get("produced_by")
        if produced_by is not None:
            producer_path, producer_issues = state_path(
                root, produced_by, f"{label}.produced_by"
            )
            issues.extend(producer_issues)
            if producer_path is not None:
                try:
                    producer_relative = producer_path.relative_to(root)
                except ValueError:
                    producer_relative = Path()
                if not producer_relative.parts or producer_relative.parts[0] != "runs":
                    issues.append(
                        Issue("ERROR", f"{label}.produced_by", "must point under runs/")
                    )
                elif not producer_path.is_dir():
                    issues.append(
                        Issue(
                            "ERROR",
                            f"{label}.produced_by",
                            f"run directory does not exist: {produced_by}",
                        )
                    )
    return issues


def validate(root: Path) -> list[Issue]:
    issues: list[Issue] = []

    match = NAME_RE.fullmatch(root.name)
    if not match:
        issues.append(
            Issue(
                "ERROR",
                ".",
                "directory name must be YYYY-MM-DD_ascii-kebab-slug with exactly one date",
            )
        )
    else:
        try:
            date.fromisoformat(match.group(1))
        except ValueError:
            issues.append(Issue("ERROR", ".", f"invalid date in directory name: {match.group(1)}"))
        if re.search(r"\d{4}-\d{2}-\d{2}", match.group(2)):
            issues.append(Issue("ERROR", ".", "slug contains a second date"))

    for required in ("README.md", "OUTCOME.md", ".gitignore"):
        path = root / required
        if not path.is_file():
            issues.append(Issue("ERROR", required, "required file is missing"))
        elif path.stat().st_size == 0:
            issues.append(Issue("ERROR", required, "required file is empty"))

    for current, dirnames, filenames in iter_tree(root):
        visible_entries = [entry for entry in current.iterdir() if entry.name != ".DS_Store"]
        if current != root and not visible_entries:
            issues.append(
                Issue("ERROR", str(current.relative_to(root)), "empty directory has no semantic content")
            )

        for name in dirnames + filenames:
            if any(pattern.search(name) for pattern in FORBIDDEN_PATTERNS):
                issues.append(
                    Issue("ERROR", str((current / name).relative_to(root)), "forbidden duplicate-source name")
                )

        for name in filenames:
            path = current / name
            if path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > 2_000_000:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if PLACEHOLDER_RE.search(text):
                issues.append(
                    Issue("ERROR", str(path.relative_to(root)), "contains unresolved {{...}} placeholder")
                )
            if path.suffix.lower() == ".md":
                issues.extend(check_local_links(root, path, text))

    outcome = root / "OUTCOME.md"
    if outcome.is_file():
        text = outcome.read_text(encoding="utf-8")
        question_count = len(QUESTION_RE.findall(text))
        self_check_count = len(SELF_CHECK_RE.findall(text))
        if question_count == 0:
            issues.append(Issue("ERROR", "OUTCOME.md", "has no '## Qn' research-question section"))
        elif self_check_count < question_count:
            issues.append(
                Issue(
                    "ERROR",
                    "OUTCOME.md",
                    "each research-question section needs an assumptions and self-check heading",
                )
            )

    raw = root / "data" / "raw"
    if raw.is_dir() and any(path.is_file() for path in raw.rglob("*")):
        if not (raw / "MANIFEST.json").is_file():
            issues.append(
                Issue("ERROR", "data/raw", "non-empty active raw inputs need MANIFEST.json")
            )

    state_file = root / "STATE.json"
    if state_file.is_file():
        issues.extend(validate_state(root, state_file))
    else:
        processed = root / "data" / "processed"
        if processed.is_dir() and any(path.is_file() for path in processed.rglob("*")):
            issues.append(
                Issue(
                    "WARN",
                    "STATE.json",
                    "evolving canonical artifacts exist in data/processed; add the current-state index when next touched",
                )
            )

    runs = root / "runs"
    if runs.is_dir():
        run_dirs = [path for path in runs.iterdir() if path.is_dir() and not path.is_symlink()]
        index = runs / "INDEX.md"
        if run_dirs and not index.is_file():
            issues.append(Issue("ERROR", "runs", "run directories exist without runs/INDEX.md"))
        index_text = index.read_text(encoding="utf-8") if index.is_file() else ""
        for run_dir in run_dirs:
            if not RUN_RE.fullmatch(run_dir.name):
                issues.append(
                    Issue("ERROR", str(run_dir.relative_to(root)), "run name must be YYYYMMDD-HHMMSS_slug")
                )
            if index.is_file() and run_dir.name not in index_text:
                issues.append(
                    Issue("ERROR", "runs/INDEX.md", f"missing run entry: {run_dir.name}")
                )

    if (root / "HOW_TO_USE.md").exists():
        issues.append(
            Issue("ERROR", "HOW_TO_USE.md", "scaffolding instructions belong to the skill, not the experiment")
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an experiment without modifying it")
    parser.add_argument("experiment", help="Path to the experiment directory")
    args = parser.parse_args()
    root = Path(args.experiment).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    issues = validate(root)
    for issue in issues:
        print(f"{issue.level}: {issue.location}: {issue.message}")
    errors = [issue for issue in issues if issue.level == "ERROR"]
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print(f"OK: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

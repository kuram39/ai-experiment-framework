#!/usr/bin/env python3
"""Create a minimal, self-contained experiment workspace."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
import unicodedata
from datetime import date
from pathlib import Path


VERSION = "1.2.0"
SKILL_DIR = Path(__file__).resolve().parent.parent
SCAFFOLD_DIR = SKILL_DIR / "assets" / "scaffold"
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
PLACEHOLDER_RE = re.compile(r"{{[A-Z0-9_]+}}")
UNSET = "Neuzavřeno; doplnit před prvním autoritativním během."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create YYYY-MM-DD_slug with a meaningful README.md, OUTCOME.md, "
            "and .gitignore. Existing targets are never overwritten."
        )
    )
    parser.add_argument("--root", default=".", help="Existing parent directory (default: cwd)")
    parser.add_argument("--title", required=True, help="Human-readable experiment name")
    parser.add_argument(
        "--question",
        required=True,
        action="append",
        help="Research question; repeat for at most three closely related questions",
    )
    parser.add_argument("--in-scope", required=True, help="What the experiment examines")
    parser.add_argument(
        "--out-of-scope", required=True, help="What the result will not prove or change"
    )
    parser.add_argument(
        "--hypothesis",
        help="Testable hypothesis, or an explicit statement that the work is exploratory",
    )
    parser.add_argument("--slug", help="ASCII kebab-case slug; inferred from title by default")
    parser.add_argument("--date", help="Creation date YYYY-MM-DD (default: local today)")
    parser.add_argument("--next-step", help="One concrete action that can be taken next")
    parser.add_argument("--baseline", help="Baseline used for comparison")
    parser.add_argument("--primary-evaluation", help="Primary metric or judgment")
    parser.add_argument("--supporting-evaluation", help="Supporting metrics or guardrails")
    parser.add_argument("--support-criterion", help="Predeclared support threshold or criterion")
    parser.add_argument("--reject-criterion", help="Predeclared rejection threshold or criterion")
    parser.add_argument("--inconclusive-criterion", help="When evidence is insufficient")
    parser.add_argument(
        "--preregistered",
        action="store_true",
        help="Create a preregistered discovery skeleton; requires all registration fields",
    )
    parser.add_argument("--experiment-id", help="Stable preregistration ID")
    parser.add_argument("--area", help="Owning research or product area")
    parser.add_argument("--owner", help="Named owner")
    parser.add_argument("--publication-target", help="Intended publication destination")
    parser.add_argument("--dry-run", action="store_true", help="Report the target without writing")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable result")
    return parser


def fail(parser: argparse.ArgumentParser, message: str) -> None:
    parser.error(message)


def clean_text(parser: argparse.ArgumentParser, value: str | None, label: str) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        fail(parser, f"{label} must not be empty")
    if "{{" in cleaned or "}}" in cleaned:
        fail(parser, f"{label} must not contain template delimiters '{{{{' or '}}}}'")
    return cleaned


def clean_line(parser: argparse.ArgumentParser, value: str | None, label: str) -> str | None:
    cleaned = clean_text(parser, value, label)
    if cleaned is not None and ("\n" in cleaned or "\r" in cleaned):
        fail(parser, f"{label} must be a single line")
    return cleaned


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_value = ascii_value.replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")


def table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def render(template_name: str, values: dict[str, str]) -> str:
    path = SCAFFOLD_DIR / template_name
    template = path.read_text(encoding="utf-8")
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    leftovers = sorted(set(PLACEHOLDER_RE.findall(template)))
    if leftovers:
        raise RuntimeError(f"unresolved placeholders in {template_name}: {', '.join(leftovers)}")
    return template.rstrip() + "\n"


def render_questions(questions: list[str]) -> str:
    if len(questions) == 1:
        return questions[0]
    return "\n".join(f"{index}. {question}" for index, question in enumerate(questions, 1))


def render_outcome_sections(
    questions: list[str], in_scope: str, out_of_scope: str, next_step: str
) -> str:
    sections: list[str] = []
    for index, question in enumerate(questions, 1):
        sections.append(
            f"""## Q{index} — {question}

### Odpověď

Otevřeno — zatím nebyl proveden autoritativní běh ani získán důkaz potřebný k odpovědi.

### Důkazy

Žádné. První důkaz musí odkazovat na konkrétní vstup, běh nebo report.

### Jistota

Nízká — otázka dosud nebyla empiricky vyhodnocena.

### Rozsah platnosti a limity

Plánovaný rozsah: {in_scope}

Mimo rozsah: {out_of_scope}

### Předpoklady a self-check

- `jisté`: při založení neexistuje v tomto experimentu věcný výsledek ani autoritativní běh.
- Pracovní předpoklady zatím nejsou důkazem; musí být ověřeny nebo výslovně zamítnuty.
- Žádné další faktické tvrzení bez zdroje zde zatím není.

### Dopad

Zatím nelze určit; otázka je otevřená.

### Kanonické artefakty

- Zatím žádný výsledkový artefakt.

### Další krok

{next_step}
""".rstrip()
        )
    return "\n\n".join(sections) + "\n"


def registration_section(args: argparse.Namespace) -> str:
    if not args.preregistered:
        return ""
    return (
        "## Registrace\n\n"
        "Tato kostra je předem registrovaná ve fázi `discovery`; nejde o hotový výsledek.\n\n"
        "| položka | hodnota |\n"
        "|---|---|\n"
        f"| ID | {table_cell(args.experiment_id)} |\n"
        f"| oblast | {table_cell(args.area)} |\n"
        f"| vlastník | {table_cell(args.owner)} |\n"
        f"| cíl publikace | {table_cell(args.publication_target)} |\n\n"
    )


def parse_creation_date(parser: argparse.ArgumentParser, raw: str | None) -> date:
    if raw is None:
        return date.today()
    try:
        parsed = date.fromisoformat(raw)
    except ValueError:
        fail(parser, "--date must be a real ISO date in YYYY-MM-DD format")
        raise AssertionError("unreachable")
    if parsed.isoformat() != raw:
        fail(parser, "--date must use zero-padded YYYY-MM-DD format")
    return parsed


def emit_result(args: argparse.Namespace, target: Path, files: list[str], created: bool) -> None:
    payload = {
        "created": created,
        "target": str(target),
        "files": files,
        "generator": f"create-experiment {VERSION}",
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    verb = "Created" if created else "Would create"
    print(f"{verb}: {target}")
    for name in files:
        print(f"  - {name}")
    if created:
        print(f"Validate: python3 {SKILL_DIR / 'scripts' / 'validate_experiment.py'} {target}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    args.title = clean_line(parser, args.title, "--title")
    args.question = [clean_line(parser, q, "--question") for q in args.question]
    args.in_scope = clean_text(parser, args.in_scope, "--in-scope")
    args.out_of_scope = clean_text(parser, args.out_of_scope, "--out-of-scope")
    args.hypothesis = clean_text(parser, args.hypothesis, "--hypothesis")
    args.next_step = clean_line(parser, args.next_step, "--next-step")

    if len(args.question) > 3:
        fail(parser, "use at most three closely related questions; split broader work")

    registration_fields = ("experiment_id", "area", "owner", "publication_target")
    for field in registration_fields:
        setattr(args, field, clean_line(parser, getattr(args, field), "--" + field.replace("_", "-")))
    supplied_registration = [field for field in registration_fields if getattr(args, field)]
    if supplied_registration and not args.preregistered:
        fail(parser, "registration fields require --preregistered")
    if args.preregistered:
        missing = ["--" + field.replace("_", "-") for field in registration_fields if not getattr(args, field)]
        if missing:
            fail(parser, "--preregistered requires " + ", ".join(missing))

    creation_date = parse_creation_date(parser, args.date)
    slug = clean_line(parser, args.slug, "--slug") or slugify(args.title)
    if not slug or not SLUG_RE.fullmatch(slug):
        fail(parser, "--slug must be lowercase ASCII kebab-case")
    if DATE_RE.search(slug):
        fail(parser, "--slug must not contain another YYYY-MM-DD date")

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        fail(parser, f"--root must be an existing directory: {root}")
    folder_name = f"{creation_date.isoformat()}_{slug}"
    target = root / folder_name
    if target.exists() or target.is_symlink():
        fail(parser, f"target already exists and will not be overwritten: {target}")

    hypothesis = args.hypothesis or (
        "Pracovní hypotéza při založení nebyla stanovena. Experiment je explorativní; "
        "před prvním autoritativním během musí být hypotéza doplněna, nebo musí být "
        "explorativní režim zachován výslovně."
    )
    next_step = args.next_step or (
        "Uzavřít vyhodnocovací kontrakt a zaregistrovat první skutečný vstup."
        if args.hypothesis
        else "Rozhodnout hypotézu versus explorativní režim a uzavřít vyhodnocovací kontrakt."
    )

    values = {
        "TITLE": args.title,
        "DATE": creation_date.isoformat(),
        "REGISTRATION_SECTION": registration_section(args),
        "QUESTIONS": render_questions(args.question),
        "HYPOTHESIS": hypothesis,
        "IN_SCOPE": args.in_scope,
        "OUT_OF_SCOPE": args.out_of_scope,
        "BASELINE": table_cell(clean_text(parser, args.baseline, "--baseline") or UNSET),
        "PRIMARY_EVALUATION": table_cell(clean_text(parser, args.primary_evaluation, "--primary-evaluation") or UNSET),
        "SUPPORTING_EVALUATION": table_cell(clean_text(parser, args.supporting_evaluation, "--supporting-evaluation") or UNSET),
        "SUPPORT_CRITERION": table_cell(clean_text(parser, args.support_criterion, "--support-criterion") or UNSET),
        "REJECT_CRITERION": table_cell(clean_text(parser, args.reject_criterion, "--reject-criterion") or UNSET),
        "INCONCLUSIVE_CRITERION": table_cell(clean_text(parser, args.inconclusive_criterion, "--inconclusive-criterion") or UNSET),
        "NEXT_STEP": next_step,
        "GENERATOR_VERSION": VERSION,
    }
    files = {
        "README.md": render("README.md.tmpl", values),
        "OUTCOME.md": render(
            "OUTCOME.md.tmpl",
            {
                "TITLE": args.title,
                "DATE": creation_date.isoformat(),
                "QUESTION_SECTIONS": render_outcome_sections(
                    args.question, args.in_scope, args.out_of_scope, next_step
                ),
                "GENERATOR_VERSION": VERSION,
            },
        ),
        ".gitignore": (SCAFFOLD_DIR / "gitignore.tmpl").read_text(encoding="utf-8").rstrip() + "\n",
    }

    if args.dry_run:
        emit_result(args, target, list(files), created=False)
        return 0

    temp_path = Path(tempfile.mkdtemp(prefix=f".{folder_name}.tmp-", dir=root))
    try:
        for relative, content in files.items():
            (temp_path / relative).write_text(content, encoding="utf-8")
        if target.exists() or target.is_symlink():
            fail(parser, f"target appeared during creation and was not overwritten: {target}")
        os.rename(temp_path, target)
    except BaseException:
        if temp_path.exists():
            shutil.rmtree(temp_path)
        raise

    emit_result(args, target, list(files), created=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

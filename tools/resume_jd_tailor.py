#!/usr/bin/env python3
"""Generate a local, deterministic Resume/JD match report.

The tool intentionally does not call external services and never mutates the
job description or base resume inputs. Its rewrite guidance is framed as
evidence-based suggestions, not generated resume edits, to avoid fabricating
claims.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Iterable


DEFAULT_MAX_KEYWORDS = 30
DEFAULT_MAX_SUGGESTIONS = 6

SHORT_KEEP = {"ai", "qa", "ui", "ux", "ml", "nlp", "api", "sql", "sre"}

STOPWORDS = {
    "a",
    "about",
    "across",
    "after",
    "all",
    "also",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "automation",
    "be",
    "because",
    "been",
    "both",
    "build",
    "by",
    "can",
    "candidate",
    "candidates",
    "company",
    "could",
    "day",
    "deliver",
    "do",
    "each",
    "engineer",
    "engineering",
    "etc",
    "for",
    "from",
    "good",
    "great",
    "has",
    "have",
    "help",
    "high",
    "highly",
    "if",
    "in",
    "include",
    "including",
    "is",
    "it",
    "job",
    "lead",
    "like",
    "looking",
    "make",
    "many",
    "may",
    "more",
    "must",
    "need",
    "new",
    "of",
    "on",
    "or",
    "our",
    "own",
    "plus",
    "preferred",
    "quality",
    "required",
    "requirements",
    "responsibilities",
    "role",
    "should",
    "skills",
    "some",
    "strong",
    "team",
    "teams",
    "that",
    "the",
    "their",
    "this",
    "to",
    "using",
    "we",
    "with",
    "work",
    "working",
    "would",
    "you",
    "your",
}


TAXONOMY: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Python", ("python",)),
    ("Java", ("java",)),
    ("JavaScript", ("javascript", "typescript", "node.js", "nodejs")),
    ("SQL", ("sql", "postgres", "mysql", "database queries")),
    ("Docker", ("docker", "container", "containers", "containerization")),
    ("Kubernetes", ("kubernetes", "k8s")),
    ("Linux", ("linux", "unix")),
    ("Git", ("git", "github", "gitlab")),
    ("CI/CD", ("ci/cd", "cicd", "continuous integration", "continuous delivery")),
    ("API testing", ("api testing", "api tests", "rest api", "rest apis", "backend api")),
    ("Web UI testing", ("web ui", "ui testing", "frontend testing", "browser testing")),
    ("Test automation", ("test automation", "automated testing", "automation framework", "automated tests")),
    ("Regression testing", ("regression testing", "regression suite", "regression tests")),
    ("Test case design", ("test case", "test cases", "test design", "test plan", "test plans")),
    ("Quality assurance", ("quality assurance", "qa", "quality engineering")),
    ("SDET", ("sdet", "software development engineer in test")),
    ("Selenium", ("selenium",)),
    ("Pytest", ("pytest", "py test")),
    ("JUnit", ("junit",)),
    ("Playwright", ("playwright",)),
    ("Cypress", ("cypress",)),
    ("Monitoring", ("monitoring", "observability", "alerting")),
    ("Release management", ("release management", "release governance", "launch readiness")),
    ("Risk management", ("risk management", "risk control", "risk governance")),
    ("Security", ("security", "secure", "anti-abuse", "fraud", "abuse prevention")),
    ("Microservices", ("microservices", "distributed services", "service architecture")),
    ("Data analysis", ("data analysis", "analytics", "data-driven", "metrics analysis")),
    ("Machine learning", ("machine learning", "ml", "deep learning")),
    ("PyTorch", ("pytorch", "torch")),
    ("LLM", ("llm", "large language model", "large language models")),
    ("Prompt engineering", ("prompt engineering", "prompt design", "prompt templates")),
    ("AI agent", ("ai agent", "agents", "agentic")),
    ("RAG", ("rag", "retrieval augmented generation", "knowledge retrieval")),
    ("Knowledge base", ("knowledge base", "knowledge management", "knowledge repository")),
    ("Product management", ("product management", "product manager", "pm")),
    ("Roadmap", ("roadmap", "product roadmap")),
    ("PRD", ("prd", "product requirements document", "requirements document")),
    ("User research", ("user research", "customer research", "user interviews")),
    ("Stakeholder management", ("stakeholder management", "stakeholders", "cross-functional partners")),
    ("Cross-functional collaboration", ("cross-functional", "cross functional", "collaboration")),
    ("Agile", ("agile", "scrum", "sprint")),
    ("UX", ("ux", "user experience")),
    ("SaaS", ("saas",)),
    ("E-commerce", ("e-commerce", "ecommerce", "marketplace")),
    ("Leadership", ("leadership", "led", "owned", "ownership", "drove")),
)


@dataclass(frozen=True)
class Keyword:
    label: str
    aliases: tuple[str, ...]
    source: str
    first_position: int

    @property
    def weight(self) -> int:
        words = normalize_for_match(self.label).split()
        base = 1 + min(2, max(0, len(words) - 1))
        return base + (1 if self.source == "taxonomy" else 0)


@dataclass(frozen=True)
class EvidenceUnit:
    line_no: int
    text: str
    is_bullet: bool


@dataclass(frozen=True)
class KeywordMatch:
    keyword: Keyword
    matched_aliases: tuple[str, ...]
    evidence: tuple[EvidenceUnit, ...]

    @property
    def matched(self) -> bool:
        return bool(self.matched_aliases)


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^[>#*\-\s]+", " ", text, flags=re.MULTILINE)
    return text


def strip_latex_comments(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        output: list[str] = []
        backslashes = 0
        for char in line:
            if char == "%" and backslashes % 2 == 0:
                break
            output.append(char)
            if char == "\\":
                backslashes += 1
            else:
                backslashes = 0
        lines.append("".join(output))
    return "\n".join(lines)


def latex_to_text(text: str) -> str:
    text = strip_latex_comments(text)
    text = re.sub(r"\\kern\s*-?[0-9.]+(?:pt|em|ex|in|cm|mm|bp|pc|dd|cc|sp)", " ", text)
    text = re.sub(r"\\href\{[^{}]*\}\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\(?:experienceHeading|tightHeading)\{([^{}]*)\}\{([^{}]*)\}", r"\1 \2", text)

    one_arg_commands = (
        "textbf",
        "textit",
        "emph",
        "small",
        "section",
        "subsection",
        "subsubsection",
    )
    one_arg_pattern = r"\\(?:" + "|".join(one_arg_commands) + r")\*?\{([^{}]*)\}"
    for _ in range(8):
        updated = re.sub(one_arg_pattern, r"\1", text)
        if updated == text:
            break
        text = updated

    replacements = {
        r"\%": "%",
        r"\&": "&",
        r"\_": "_",
        r"\#": "#",
        r"\$": "$",
        r"\cdot": " ",
        r"\times": "x",
        r"\rightarrow": "->",
        r"\\": "\n",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\\begin\{[^{}]+\}(?:\[[^\]]*\])?", "\n", text)
    text = re.sub(r"\\end\{[^{}]+\}", "\n", text)
    text = re.sub(r"\\item\b", "\n", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}$]", " ", text)
    text = text.replace("~", " ").replace("--", " - ")
    return normalize_spaces(text)


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_for_match(text: str, latex: bool = True) -> str:
    plain_text = latex_to_text(strip_markdown(text)) if latex else strip_markdown(text)
    text = plain_text.lower()
    text = text.replace("c++", "cplusplus").replace("c#", "csharp")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return normalize_spaces(text)


def contains_phrase(normalized_text: str, phrase: str) -> bool:
    normalized_phrase = normalize_for_match(phrase)
    if not normalized_phrase:
        return False
    return f" {normalized_phrase} " in f" {normalized_text} "


def first_phrase_position(normalized_text: str, aliases: Iterable[str]) -> int:
    positions = []
    padded = f" {normalized_text} "
    for alias in aliases:
        normalized_alias = normalize_for_match(alias)
        if not normalized_alias:
            continue
        position = padded.find(f" {normalized_alias} ")
        if position >= 0:
            positions.append(position)
    return min(positions) if positions else sys.maxsize


def display_dynamic_label(label: str) -> str:
    upper = {
        "ai": "AI",
        "api": "API",
        "ci cd": "CI/CD",
        "llm": "LLM",
        "ml": "ML",
        "nlp": "NLP",
        "qa": "QA",
        "sdet": "SDET",
        "sql": "SQL",
        "ui": "UI",
        "ux": "UX",
    }
    return upper.get(label, label)


def dynamic_keyword_candidates(
    jd_text: str,
    existing_aliases: set[str],
    limit: int,
    include_single_occurrence: bool = False,
) -> list[Keyword]:
    normalized_chunks = [
        normalize_for_match(chunk, latex=False)
        for chunk in re.split(r"[\n.;:!?()]+", strip_markdown(jd_text))
    ]
    scores: dict[str, float] = {}
    first_positions: dict[str, int] = {}
    global_index = 0

    for chunk in normalized_chunks:
        tokens = chunk.split()
        for size in (3, 2, 1):
            for index in range(0, max(0, len(tokens) - size + 1)):
                window = tokens[index : index + size]
                if any(token in STOPWORDS for token in window):
                    continue
                if size == 1 and len(window[0]) < 4 and window[0] not in SHORT_KEEP:
                    continue
                label = " ".join(window)
                if label in existing_aliases:
                    continue
                if any(label in alias or alias in label for alias in existing_aliases if len(alias) > 3):
                    continue
                score = 1.0 + (size - 1) * 0.6
                if any(token in SHORT_KEEP or any(char.isdigit() for char in token) for token in window):
                    score += 0.5
                scores[label] = scores.get(label, 0.0) + score
                first_positions.setdefault(label, global_index + index)
        global_index += len(tokens)

    minimum_score = 1.0 if include_single_occurrence else 3.0
    scores = {label: score for label, score in scores.items() if score >= minimum_score}
    if not include_single_occurrence:
        for label in list(scores):
            label_tokens = label.split()
            if len(label_tokens) > 1:
                continue
            if sum(1 for chunk in normalized_chunks if f" {label} " in f" {chunk} ") < 2:
                scores.pop(label)

    ranked = sorted(scores, key=lambda item: (-scores[item], first_positions[item], item))
    keywords: list[Keyword] = []
    for label in ranked[:limit]:
        keywords.append(
            Keyword(
                label=display_dynamic_label(label),
                aliases=(label,),
                source="dynamic",
                first_position=first_positions[label],
            )
        )
    return keywords


def extract_jd_keywords(jd_text: str, max_keywords: int = DEFAULT_MAX_KEYWORDS) -> tuple[Keyword, ...]:
    normalized_jd = normalize_for_match(jd_text, latex=False)
    keywords: list[Keyword] = []
    existing_aliases: set[str] = set()

    for label, aliases in TAXONOMY:
        all_aliases = (label, *aliases)
        position = first_phrase_position(normalized_jd, all_aliases)
        if position == sys.maxsize:
            continue
        keyword = Keyword(label=label, aliases=tuple(dict.fromkeys(all_aliases)), source="taxonomy", first_position=position)
        keywords.append(keyword)
        existing_aliases.update(normalize_for_match(alias) for alias in keyword.aliases)

    remaining_slots = max(0, max_keywords - len(keywords))
    keywords.extend(
        dynamic_keyword_candidates(
            jd_text,
            existing_aliases,
            remaining_slots,
            include_single_occurrence=len(keywords) < 8,
        )
    )
    keywords = sorted(keywords, key=lambda item: (item.first_position, item.label.lower()))
    return tuple(keywords[:max_keywords])


def looks_sensitive_or_contact(raw_line: str, clean_line: str) -> bool:
    haystack = f"{raw_line} {clean_line}".lower()
    if "mailto:" in haystack or "tel:" in haystack or "website:" in haystack:
        return True
    if re.search(r"\bhttps?://", haystack):
        return True
    if re.search(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", haystack):
        return True
    if re.search(r"(?:\+?\d[\s().-]*){8,}", haystack):
        return True
    return False


def is_latex_scaffolding(raw_line: str) -> bool:
    stripped = raw_line.strip()
    if not stripped:
        return True
    scaffolding_prefixes = (
        r"\documentclass",
        r"\usepackage",
        r"\set",
        r"\pagestyle",
        r"\fancy",
        r"\renewcommand",
        r"\addtolength",
        r"\urlstyle",
        r"\ragged",
        r"\titleformat",
        r"\newcommand",
        r"\begin",
        r"\end",
        r"\noindent",
        r"\hspace",
        r"\vspace",
        r"\phantom",
    )
    return stripped.startswith(scaffolding_prefixes)


def extract_evidence_units(resume_tex: str) -> tuple[EvidenceUnit, ...]:
    units: list[EvidenceUnit] = []
    for line_no, raw_line in enumerate(resume_tex.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("%") or is_latex_scaffolding(raw_line):
            continue
        clean_line = latex_to_text(raw_line)
        if not clean_line or len(clean_line) < 8:
            continue
        if looks_sensitive_or_contact(raw_line, clean_line):
            continue
        if not re.search(r"[A-Za-z0-9\u4e00-\u9fff]", clean_line):
            continue
        units.append(EvidenceUnit(line_no=line_no, text=clean_line, is_bullet=r"\item" in raw_line))
    return tuple(units)


def match_keywords(jd_text: str, resume_tex: str, max_keywords: int = DEFAULT_MAX_KEYWORDS) -> tuple[KeywordMatch, ...]:
    keywords = extract_jd_keywords(jd_text, max_keywords=max_keywords)
    normalized_resume = normalize_for_match(resume_tex)
    evidence_units = extract_evidence_units(resume_tex)
    matches: list[KeywordMatch] = []

    for keyword in keywords:
        matched_aliases = tuple(
            alias for alias in keyword.aliases if contains_phrase(normalized_resume, alias)
        )
        evidence = tuple(
            unit
            for unit in evidence_units
            if any(contains_phrase(normalize_for_match(unit.text, latex=False), alias) for alias in keyword.aliases)
        )[:3]
        matches.append(KeywordMatch(keyword=keyword, matched_aliases=matched_aliases, evidence=evidence))

    return tuple(matches)


def compute_match_score(matches: Iterable[KeywordMatch]) -> int:
    materialized = tuple(matches)
    total = sum(match.keyword.weight for match in materialized)
    if total == 0:
        return 0
    covered = sum(match.keyword.weight for match in materialized if match.matched)
    return round((covered / total) * 100)


def unique_evidence_hits(matches: Iterable[KeywordMatch]) -> list[tuple[KeywordMatch, EvidenceUnit]]:
    hits: list[tuple[KeywordMatch, EvidenceUnit]] = []
    seen: set[tuple[str, int]] = set()
    for match in matches:
        if not match.matched:
            continue
        for unit in match.evidence:
            key = (match.keyword.label, unit.line_no)
            if key in seen:
                continue
            seen.add(key)
            hits.append((match, unit))
            break
    return hits


def suggestion_units(matches: Iterable[KeywordMatch], max_suggestions: int) -> list[tuple[EvidenceUnit, list[str]]]:
    by_line: dict[int, tuple[EvidenceUnit, list[str]]] = {}
    for match in matches:
        if not match.matched:
            continue
        for unit in match.evidence:
            if unit.line_no not in by_line:
                by_line[unit.line_no] = (unit, [])
            by_line[unit.line_no][1].append(match.keyword.label)

    ranked = sorted(
        by_line.values(),
        key=lambda item: (
            0 if item[0].is_bullet else 1,
            -len(set(item[1])),
            item[0].line_no,
        ),
    )
    return [(unit, sorted(set(labels))) for unit, labels in ranked[:max_suggestions]]


def render_markdown_report(
    jd_name: str,
    resume_name: str,
    matches: tuple[KeywordMatch, ...],
    max_suggestions: int = DEFAULT_MAX_SUGGESTIONS,
) -> str:
    score = compute_match_score(matches)
    matched = [match for match in matches if match.matched]
    missing = [match for match in matches if not match.matched]
    lines: list[str] = [
        "# Resume/JD Match Report",
        "",
        f"- JD: `{jd_name}`",
        f"- Base resume: `{resume_name}`",
        f"- Match score: **{score}/100**",
        f"- JD keywords analyzed: **{len(matches)}**",
        f"- Keywords with resume evidence: **{len(matched)}**",
        f"- Missing keywords: **{len(missing)}**",
        "",
        "This report was generated locally with deterministic text matching. It does not edit the base resume and does not call external services.",
        "",
        "## JD Keywords",
        "",
    ]

    if matches:
        for match in matches:
            state = "matched" if match.matched else "missing"
            aliases = ", ".join(match.matched_aliases[:3])
            suffix = f" - evidence aliases: {aliases}" if aliases else ""
            lines.append(f"- [{state}] {match.keyword.label}{suffix}")
    else:
        lines.append("- No JD keywords were extracted. Add more role requirements to the JD file.")

    lines.extend(["", "## Missing Keywords", ""])
    if missing:
        for match in missing:
            lines.append(f"- {match.keyword.label}")
    else:
        lines.append("- None from the extracted JD keyword set.")

    lines.extend(["", "## Evidence Hits", ""])
    hits = unique_evidence_hits(matches)
    if hits:
        for match, unit in hits:
            lines.append(f"- **{match.keyword.label}** - resume line {unit.line_no}: `{unit.text}`")
    else:
        lines.append("- No direct resume evidence found for the extracted JD keywords.")

    lines.extend(["", "## Bullet Rewrite Suggestions", ""])
    suggestions = suggestion_units(matches, max_suggestions=max_suggestions)
    if suggestions:
        for unit, labels in suggestions:
            keyword_text = ", ".join(labels[:5])
            lines.append(f"- Source line {unit.line_no}: `{unit.text}`")
            lines.append(f"  Covers: {keyword_text}.")
            lines.append(
                "  Suggestion: Reframe this existing evidence around the listed JD language while preserving only the facts, tools, scope, and metrics already present in the source line."
            )
    else:
        lines.append("- No rewrite suggestions. Add truthful resume evidence before tailoring bullets for this JD.")

    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- Treat missing keywords as gaps, not claims to add.",
            "- Add a missing keyword only when a real project, role, or artifact proves it and you can defend it in an interview.",
            "- Keep tailored variants and company-specific reports in private application folders.",
            "- Do not commit private JDs, generated PDFs, or application-specific analysis notes.",
            "",
        ]
    )
    return "\n".join(lines)


def build_report(
    jd_markdown: str,
    resume_tex: str,
    jd_name: str = "job_description.md",
    resume_name: str = "resume.tex",
    max_keywords: int = DEFAULT_MAX_KEYWORDS,
    max_suggestions: int = DEFAULT_MAX_SUGGESTIONS,
) -> str:
    matches = match_keywords(jd_markdown, resume_tex, max_keywords=max_keywords)
    return render_markdown_report(jd_name, resume_name, matches, max_suggestions=max_suggestions)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a local Resume/JD match report without modifying the base resume.",
    )
    parser.add_argument("job_description", type=Path, help="Path to a job description Markdown file.")
    parser.add_argument("base_resume", type=Path, help="Path to a base resume .tex file.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional Markdown report path. If omitted, the report is printed to stdout.",
    )
    parser.add_argument(
        "--max-keywords",
        type=int,
        default=DEFAULT_MAX_KEYWORDS,
        help=f"Maximum JD keywords to analyze (default: {DEFAULT_MAX_KEYWORDS}).",
    )
    parser.add_argument(
        "--max-suggestions",
        type=int,
        default=DEFAULT_MAX_SUGGESTIONS,
        help=f"Maximum bullet rewrite suggestions to include (default: {DEFAULT_MAX_SUGGESTIONS}).",
    )
    return parser.parse_args(argv)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"Input file not found: {path}") from exc
    except UnicodeDecodeError as exc:
        raise SystemExit(f"Input file is not valid UTF-8 text: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.max_keywords < 1:
        raise SystemExit("--max-keywords must be at least 1")
    if args.max_suggestions < 0:
        raise SystemExit("--max-suggestions must be 0 or greater")

    jd_text = read_text(args.job_description)
    resume_text = read_text(args.base_resume)
    report = build_report(
        jd_text,
        resume_text,
        jd_name=args.job_description.name,
        resume_name=args.base_resume.name,
        max_keywords=args.max_keywords,
        max_suggestions=args.max_suggestions,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import resume_jd_tailor


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class ResumeJdTailorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jd_path = FIXTURES / "sanitized_jd.md"
        self.resume_path = FIXTURES / "sanitized_resume.tex"
        self.jd_text = self.jd_path.read_text(encoding="utf-8")
        self.resume_text = self.resume_path.read_text(encoding="utf-8")

    def test_report_contains_required_sections_and_guardrails(self) -> None:
        report = resume_jd_tailor.build_report(
            self.jd_text,
            self.resume_text,
            jd_name=self.jd_path.name,
            resume_name=self.resume_path.name,
        )

        self.assertIn("# Resume/JD Match Report", report)
        self.assertIn("- Match score: **", report)
        self.assertIn("## JD Keywords", report)
        self.assertIn("## Missing Keywords", report)
        self.assertIn("## Evidence Hits", report)
        self.assertIn("## Bullet Rewrite Suggestions", report)
        self.assertIn("Treat missing keywords as gaps, not claims to add.", report)

    def test_keyword_matching_finds_evidence_and_missing_terms(self) -> None:
        matches = resume_jd_tailor.match_keywords(self.jd_text, self.resume_text)
        by_label = {match.keyword.label: match for match in matches}

        self.assertTrue(by_label["Python"].matched)
        self.assertTrue(by_label["Pytest"].matched)
        self.assertTrue(by_label["CI/CD"].matched)
        self.assertTrue(by_label["Docker"].matched)
        self.assertTrue(by_label["SQL"].matched)
        self.assertFalse(by_label["Kubernetes"].matched)
        self.assertGreaterEqual(resume_jd_tailor.compute_match_score(matches), 70)
        self.assertLess(resume_jd_tailor.compute_match_score(matches), 100)

    def test_latex_cleaning_preserves_metrics_and_compact_commands(self) -> None:
        text = resume_jd_tailor.latex_to_text(
            r"\item Improved CI\kern0.5ptCD coverage from 62\% to 91\% with \textbf{Python}."
        )

        self.assertIn("CI CD", text)
        self.assertIn("62%", text)
        self.assertIn("91%", text)
        self.assertIn("Python", text)

    def test_markdown_percent_does_not_truncate_jd_keywords(self) -> None:
        normalized = resume_jd_tailor.normalize_for_match(
            "Improve 95% coverage with GraphQL and incident response.",
            latex=False,
        )

        self.assertIn("graphql", normalized)
        self.assertIn("incident response", normalized)

    def test_cli_writes_report_without_modifying_inputs(self) -> None:
        original_resume = self.resume_path.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "resume_jd_tailor.py"),
                    str(self.jd_path),
                    str(self.resume_path),
                    "--output",
                    str(output_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = output_path.read_text(encoding="utf-8")
            self.assertIn("Kubernetes", report)
            self.assertIn("This report was generated locally", report)
            self.assertEqual(original_resume, self.resume_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

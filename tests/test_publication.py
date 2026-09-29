import unittest

from tools.publication_audit import audit
from tools.validate import ROOT


class PublicationTests(unittest.TestCase):
    def test_public_docs_link_to_real_local_paths_not_a_fake_remote(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("MacSiem/vacuum-consumption-data", readme)
        self.assertNotIn("github.com/MacSiem/vacuum-consumption-data", readme)
        self.assertTrue((ROOT / ".github" / "ISSUE_TEMPLATE" / "evidence-intake.yml").is_file())
        self.assertTrue((ROOT / "docs" / "model-support-matrix.md").is_file())
        self.assertIn("zero physically approved profiles", readme)

    def test_publication_audit_is_redacted_and_reports_file_manifest(self):
        report = audit()
        self.assertIn("tracked", report["candidate_files"])
        self.assertIn("untracked", report["candidate_files"])
        self.assertTrue(all(set(finding) == {"path", "rule", "lines", "redacted"} for finding in report["findings"]))
        self.assertFalse(report["findings"])
        self.assertTrue(report["safe_for_review"])
        # The prep note was committed on 2026-09-05; a clean CI checkout has no untracked files.
        candidates = report["candidate_files"]["tracked"] + report["candidate_files"]["untracked"]
        self.assertIn("docs/publication-prep-2026-09-05.md", candidates)

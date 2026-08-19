import unittest
from pathlib import Path


class RevisionHistoryTableTests(unittest.TestCase):
    def setUp(self):
        project_root = Path(__file__).resolve().parent.parent
        self.template = (project_root / "templates" / "revision_history.html").read_text(
            encoding="utf-8"
        )
        self.styles = (project_root / "static" / "css" / "app.css").read_text(
            encoding="utf-8"
        )

    def test_revision_history_does_not_require_horizontal_scrolling(self):
        for label in (
            "Date",
            "File Name",
            "Revision",
            "Revised By",
            "Plant",
            "Department",
            "Change Summary",
            "Previous Version",
        ):
            self.assertIn(f'data-label="{label}"', self.template)

        self.assertIn(
            ".revision-history-table {\n  width: 100%;\n  min-width: 0;",
            self.styles,
        )
        self.assertIn("@container revision-history (max-width: 820px)", self.styles)
        self.assertIn("container: revision-history / inline-size", self.styles)


if __name__ == "__main__":
    unittest.main()

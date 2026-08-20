import re
import unittest
from pathlib import Path


class DocumentViewDetailsTests(unittest.TestCase):
    def setUp(self):
        project_root = Path(__file__).resolve().parent.parent
        self.template = (project_root / "templates" / "document_view.html").read_text(
            encoding="utf-8"
        )

    def test_document_details_are_full_width_and_horizontal(self):
        details_match = re.search(
            r'<section class="review-card review-document-details-card">(.*?)</section>',
            self.template,
            re.DOTALL,
        )
        self.assertIsNotNone(details_match)
        details = details_match.group(1)

        self.assertLess(
            self.template.index("review-document-details-card"),
            self.template.index("document-view-preview-layout"),
        )
        self.assertIn("review-document-details-grid", details)
        self.assertEqual(details.count('class="review-meta-item"'), 5)

        for label in (
            "Document Number",
            "Revision Number",
            "Category",
            "Requested by",
            "Date of upload",
        ):
            self.assertIn(f"<span>{label}</span>", details)

        self.assertNotIn('<aside class="review-side">', self.template)


if __name__ == "__main__":
    unittest.main()

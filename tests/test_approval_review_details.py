import re
import unittest
from pathlib import Path


class ApprovalReviewDetailsTests(unittest.TestCase):
    def test_document_details_are_horizontal_and_contain_only_requested_fields(self):
        project_root = Path(__file__).resolve().parent.parent
        template = (project_root / "templates" / "approval_review.html").read_text(
            encoding="utf-8"
        )
        details = re.search(
            r'<section class="review-card review-document-details-card">(.*?)</section>',
            template,
            re.DOTALL,
        ).group(1)

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

        for removed_label in (
            "Plant",
            "Department",
            "Customer",
            "Current status",
            "Updated at",
        ):
            self.assertNotIn(f"<span>{removed_label}</span>", details)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


class ApprovalRecordsTableTests(unittest.TestCase):
    def test_document_number_replaces_customer_column(self):
        project_root = Path(__file__).resolve().parent.parent
        template = (project_root / "templates" / "approvals.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("<th>Document Number</th>", template)
        self.assertIn("approval-col-document-number", template)
        self.assertIn("{{ r.document_number or '—' }}", template)
        self.assertNotIn("<th>Customer</th>", template)
        self.assertNotIn("approval-col-customer", template)
        self.assertNotIn("badge(r.customer", template)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


class DocumentLibraryDepartmentCardTests(unittest.TestCase):
    def setUp(self):
        project_root = Path(__file__).resolve().parent.parent
        self.script = (
            project_root / "static" / "js" / "document_library.js"
        ).read_text(encoding="utf-8")

    def test_department_cards_have_label_and_initial_fallbacks(self):
        self.assertIn("function departmentCardLabel", self.script)
        self.assertIn("function departmentCardInitials", self.script)
        self.assertIn("const departmentLabel = departmentCardLabel", self.script)
        self.assertIn("<strong>${departmentLabel}</strong>", self.script)
        self.assertNotIn("<strong>${departmentData.label}</strong>", self.script)


if __name__ == "__main__":
    unittest.main()

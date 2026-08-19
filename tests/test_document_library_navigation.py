import unittest
from pathlib import Path


class DocumentLibraryNavigationTests(unittest.TestCase):
    def setUp(self):
        project_root = Path(__file__).resolve().parent.parent
        self.script = (
            project_root / "static" / "js" / "document_library.js"
        ).read_text(encoding="utf-8")

    def test_folder_navigation_does_not_reload_the_page(self):
        navigation_start = self.script.index("function navigateToCurrentSelection()")
        navigation_end = self.script.index("function runAndNavigate", navigation_start)
        navigation = self.script[navigation_start:navigation_end]

        self.assertIn("window.history.pushState", navigation)
        self.assertNotIn("window.location.assign", navigation)
        self.assertIn("function restoreSelectionFromUrl", self.script)
        self.assertIn("window.addEventListener('popstate'", self.script)


if __name__ == "__main__":
    unittest.main()

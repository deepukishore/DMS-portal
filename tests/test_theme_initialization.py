import unittest
from pathlib import Path


class ThemeInitializationTests(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parent.parent
        self.template_paths = [
            self.project_root / "templates" / "layout.html",
            self.project_root / "templates" / "approval_review.html",
            self.project_root / "templates" / "document_view.html",
            self.project_root / "templates" / "auth" / "login.html",
            self.project_root / "templates" / "auth" / "register.html",
            self.project_root / "templates" / "auth" / "reset_password.html",
        ]

    def test_theme_is_initialized_before_the_stylesheet(self):
        for path in self.template_paths:
            template = path.read_text(encoding="utf-8")
            with self.subTest(template=path.name):
                self.assertIn('<html lang="en" data-theme="light">', template)
                self.assertLess(
                    template.index("components/theme_init.html"),
                    template.index("css/app.css"),
                )

    def test_inline_initializer_preserves_dark_mode_without_delaying_light_mode(self):
        initializer = (
            self.project_root / "templates" / "components" / "theme_init.html"
        ).read_text(encoding="utf-8")
        self.assertIn("localStorage.getItem('theme') === 'dark'", initializer)
        self.assertIn("removeAttribute('data-theme')", initializer)
        self.assertIn("catch (error)", initializer)


if __name__ == "__main__":
    unittest.main()

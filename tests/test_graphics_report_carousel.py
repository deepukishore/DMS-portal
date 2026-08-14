from pathlib import Path
import unittest


class GraphicsReportCarouselTests(unittest.TestCase):
    def test_carousel_has_persistent_pause_control(self):
        project_root = Path(__file__).resolve().parents[1]
        template = (project_root / "templates" / "graphics_report.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("data-carousel-pause", template)
        self.assertIn('aria-pressed="false"', template)
        self.assertIn("let isPausedByUser = false", template)
        self.assertIn("if (isPausedByUser || document.hidden) return", template)
        self.assertIn("isPausedByUser = !isPausedByUser", template)
        self.assertNotIn("data-pause-label", template)


if __name__ == "__main__":
    unittest.main()

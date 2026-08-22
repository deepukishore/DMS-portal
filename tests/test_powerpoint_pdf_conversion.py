import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services import pdf_conversion_service


class PowerPointPdfConversionTests(unittest.TestCase):
    @patch.object(pdf_conversion_service, "_pptx_to_text_pdf")
    @patch.object(pdf_conversion_service, "_pptx_to_pdf_with_powerpoint")
    def test_windows_prefers_native_powerpoint_rendering(self, native_renderer, text_renderer):
        with patch.object(pdf_conversion_service.os, "name", "nt"):
            result = pdf_conversion_service._pptx_to_pdf("source.pptx", "preview.pdf")

        self.assertEqual(result, ("preview.pdf", None))
        native_renderer.assert_called_once_with("source.pptx", "preview.pdf")
        text_renderer.assert_not_called()

    @patch.object(pdf_conversion_service, "_pptx_to_text_pdf")
    @patch.object(pdf_conversion_service, "_pptx_to_pdf_with_powerpoint")
    def test_text_preview_remains_available_without_powerpoint(self, native_renderer, text_renderer):
        native_renderer.side_effect = RuntimeError("PowerPoint is unavailable")
        text_renderer.return_value = ("preview.pdf", None)

        with patch.object(pdf_conversion_service.os, "name", "nt"):
            result = pdf_conversion_service._pptx_to_pdf("source.pptx", "preview.pdf")

        self.assertEqual(result, ("preview.pdf", None))
        text_renderer.assert_called_once_with("source.pptx", "preview.pdf")


if __name__ == "__main__":
    unittest.main()

import os
import tempfile
import unittest

from pypdf import PdfWriter

from services.document_preview_service import DocumentPreviewService
from services.document_service import DocumentService


class DocumentPreviewPathTests(unittest.TestCase):
    def test_prefers_generated_pdf_for_office_document(self):
        with tempfile.TemporaryDirectory() as upload_folder:
            source_name = "example.pptx"
            preview_name = "example.pdf"
            open(os.path.join(upload_folder, source_name), "wb").close()
            open(os.path.join(upload_folder, preview_name), "wb").close()

            record = {
                "file_name": source_name,
                "pdf_file_name": preview_name,
            }

            preview_path = DocumentService.get_preview_file_path(record, upload_folder)

            self.assertEqual(preview_path, os.path.join(upload_folder, preview_name))
            self.assertEqual(
                DocumentPreviewService.build_preview(preview_path, "/file"),
                {"mode": "pdf", "url": "/file"},
            )

    def test_falls_back_to_source_when_generated_preview_is_missing(self):
        with tempfile.TemporaryDirectory() as upload_folder:
            source_name = "example.docx"
            open(os.path.join(upload_folder, source_name), "wb").close()

            record = {
                "file_name": source_name,
                "pdf_file_name": "missing.pdf",
            }

            preview_path = DocumentService.get_preview_file_path(record, upload_folder)

            self.assertEqual(preview_path, os.path.join(upload_folder, source_name))

    def test_pdf_preview_includes_the_total_page_count(self):
        with tempfile.TemporaryDirectory() as upload_folder:
            pdf_path = os.path.join(upload_folder, "three-pages.pdf")
            writer = PdfWriter()
            for _ in range(3):
                writer.add_blank_page(width=612, height=792)
            with open(pdf_path, "wb") as pdf_file:
                writer.write(pdf_file)

            self.assertEqual(
                DocumentPreviewService.build_preview(pdf_path, "/file"),
                {"mode": "pdf", "url": "/file", "page_count": 3},
            )

            second_page = DocumentPreviewService.render_pdf_page(pdf_path, 2)
            self.assertIsNotNone(second_page)
            self.assertTrue(second_page.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertIsNone(DocumentPreviewService.render_pdf_page(pdf_path, 4))


if __name__ == "__main__":
    unittest.main()

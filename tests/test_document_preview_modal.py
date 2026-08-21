import unittest
from pathlib import Path


class DocumentPreviewModalTests(unittest.TestCase):
    def setUp(self):
        project_root = Path(__file__).resolve().parent.parent
        self.template = (project_root / "templates" / "document_view.html").read_text(
            encoding="utf-8"
        )
        self.script = (
            project_root / "static" / "js" / "document_view.js"
        ).read_text(encoding="utf-8")
        self.styles = (project_root / "static" / "css" / "app.css").read_text(
            encoding="utf-8"
        )

    def test_preview_offers_expanded_and_new_tab_controls(self):
        self.assertGreaterEqual(self.template.count("data-open-document-preview"), 3)
        self.assertIn("Open in new tab", self.template)
        self.assertIn('target="_blank"', self.template)
        self.assertIn('rel="noopener noreferrer"', self.template)
        self.assertIn('href="{{ preview.url }}"', self.template)

    def test_expanded_view_uses_an_accessible_modal_layer(self):
        self.assertIn('id="document-preview-modal"', self.template)
        self.assertIn('role="dialog"', self.template)
        self.assertIn('aria-modal="true"', self.template)
        self.assertIn('id="document-preview-modal-close"', self.template)
        self.assertIn("document_view.js", self.template)
        self.assertIn("background: rgba(3, 12, 22, .78)", self.styles)

    def test_modal_clones_the_safe_preview_and_supports_escape(self):
        self.assertIn("sourcePreview.cloneNode(true)", self.script)
        self.assertIn("modalBody.replaceChildren(previewClone)", self.script)
        self.assertIn("event.key === 'Escape'", self.script)
        self.assertIn("event.target === modal", self.script)

    def test_pdf_modal_has_page_number_navigation(self):
        self.assertIn('id="document-preview-pagination"', self.template)
        self.assertIn('id="document-preview-page-number"', self.template)
        self.assertIn('id="document-preview-page-previous"', self.template)
        self.assertIn('id="document-preview-page-next"', self.template)
        self.assertIn("showPage(currentPage - 1)", self.script)
        self.assertIn("showPage(currentPage + 1)", self.script)
        self.assertIn("data-page-image-url", self.template)
        self.assertIn("document-preview-page-image", self.script)
        self.assertIn("?page=${page}", self.script)


if __name__ == "__main__":
    unittest.main()

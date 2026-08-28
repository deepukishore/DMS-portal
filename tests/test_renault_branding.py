import unittest
from pathlib import Path

from data.customers import CUSTOMER_BRANDS


class RenaultBrandingTests(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[1]
        self.styles = (self.project_root / "static" / "css" / "app.css").read_text(
            encoding="utf-8"
        )

    def test_renault_uses_the_supplied_jpeg_asset(self):
        asset = CUSTOMER_BRANDS["Renault Nissan"]["logo"]
        supplied_asset = self.project_root / "Images" / "Renault.jpg"
        deployed_asset = self.project_root / "static" / asset

        self.assertEqual(asset, "images/customers/Renault.jpg")
        self.assertTrue(deployed_asset.is_file())
        self.assertEqual(supplied_asset.read_bytes(), deployed_asset.read_bytes())

    def test_renault_card_uses_the_black_logo_without_blending_or_masking(self):
        card_selector = (
            '.customer-card[data-customer-name="Renault Nissan"] '
            ".customer-logo-card"
        )
        card_rule = self.styles.split(card_selector, 1)[1].split("}", 1)[0]
        image_rule = self.styles.split(f"{card_selector} img", 1)[1].split("}", 1)[0]

        self.assertIn("background: #000", card_rule)
        self.assertNotIn("background-blend-mode", card_rule)
        self.assertIn("inset: 0 0 61px", card_rule)
        self.assertIn("height: auto", card_rule)
        self.assertIn("object-fit: contain", image_rule)
        self.assertIn("transform: scale(1.02)", image_rule)
        self.assertNotIn("mask-image", image_rule)


if __name__ == "__main__":
    unittest.main()

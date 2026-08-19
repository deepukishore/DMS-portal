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

        self.assertEqual(asset, "images/customers/Renault.jpg")
        self.assertTrue((self.project_root / "static" / asset).is_file())

    def test_renault_card_blends_the_square_logo_into_the_wide_card(self):
        card_selector = (
            '.customer-card[data-customer-name="Renault Nissan"] '
            ".customer-logo-card"
        )
        card_rule = self.styles.split(card_selector, 1)[1].split("}", 1)[0]
        image_rule = self.styles.split(f"{card_selector} img", 1)[1].split("}", 1)[0]

        self.assertIn('url("../images/customers/Renault.jpg")', card_rule)
        self.assertIn("background-blend-mode: multiply", card_rule)
        self.assertIn("inset: 0 0 61px", card_rule)
        self.assertIn("height: auto", card_rule)
        self.assertIn("mask-image: linear-gradient", image_rule)
        self.assertIn("transform: translateX(-50%)", image_rule)


if __name__ == "__main__":
    unittest.main()

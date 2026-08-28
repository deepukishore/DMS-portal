import unittest
from pathlib import Path

from data.customers import CUSTOMER_BRANDS


class MahindraBrandingTests(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[1]

    def test_mahindra_uses_the_supplied_jpeg_asset(self):
        asset = CUSTOMER_BRANDS["M&M - Mahindra and Mahindra"]["logo"]
        supplied_asset = self.project_root / "Images" / "Mahindra-Logo.jpg"
        deployed_asset = self.project_root / "static" / asset

        self.assertEqual(asset, "images/customers/Mahindra-Logo.jpg")
        self.assertTrue(deployed_asset.is_file())
        self.assertEqual(supplied_asset.read_bytes(), deployed_asset.read_bytes())


if __name__ == "__main__":
    unittest.main()

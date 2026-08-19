import unittest
from pathlib import Path

from data.customers import CUSTOMER_BRANDS


class RenaultBrandingTests(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[1]

    def test_renault_uses_the_supplied_jpeg_asset(self):
        asset = CUSTOMER_BRANDS["Renault Nissan"]["logo"]

        self.assertEqual(asset, "images/customers/Renault.jpg")
        self.assertTrue((self.project_root / "static" / asset).is_file())


if __name__ == "__main__":
    unittest.main()

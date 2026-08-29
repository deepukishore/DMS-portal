import unittest
from pathlib import Path

from data.customers import CUSTOMER_BRANDS


class VecvBrandingTests(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[1]

    def test_vecv_uses_the_supplied_png_asset(self):
        asset = CUSTOMER_BRANDS["VECV - Volvo Eicher Commercial Vehicles"]["logo"]
        supplied_asset = self.project_root / "Images" / "Vecv.png"
        deployed_asset = self.project_root / "static" / asset

        self.assertEqual(asset, "images/customers/VECV-Logo.png")
        self.assertTrue(deployed_asset.is_file())
        self.assertEqual(supplied_asset.read_bytes(), deployed_asset.read_bytes())


if __name__ == "__main__":
    unittest.main()

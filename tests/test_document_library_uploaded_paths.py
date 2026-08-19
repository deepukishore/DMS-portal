import unittest
from copy import deepcopy
from unittest.mock import patch

from data.document_library_data import LIBRARY_DATA
from services.document_library_service import DocumentLibraryService


class DocumentLibraryUploadedPathTests(unittest.TestCase):
    def test_qms_department_is_not_promoted_to_plant(self):
        uploaded_record = {
            "file_name": "uploaded_quality_sop.pdf",
            "sub_category": (
                "L1:sops:P2 - Guduvanchery Plant:"
                "QAD - Quality Assurance Department"
            ),
            "plant": "P2 - Guduvanchery Plant",
            "department": "QAD - Quality Assurance Department",
        }

        def records_for(category, **_kwargs):
            return [uploaded_record] if category == "qms" else []

        with patch(
            "services.document_library_service."
            "CategoryDocumentService.get_file_records_for_category",
            side_effect=records_for,
        ):
            result = DocumentLibraryService._merge_uploaded_files(
                "qms",
                deepcopy(LIBRARY_DATA["qms"]),
            )

        plants = result["document_groups"]["sops"]["plant_departments"]
        self.assertEqual(
            set(plants),
            {
                "P1 - Trichy Plant",
                "P2 - Guduvanchery Plant",
                "P3 - Guduvanchery Plant",
                "P4 - Uttarakhand Plant",
            },
        )
        self.assertNotIn("QAD - Quality Assurance Department", plants)
        self.assertIn(
            "uploaded_quality_sop.pdf",
            plants["P2 - Guduvanchery Plant"]["departments"]
            ["QAD - Quality Assurance Department"]["files"],
        )


if __name__ == "__main__":
    unittest.main()

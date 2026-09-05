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

    def test_legacy_flat_iatf_audit_upload_is_moved_to_new_hierarchy(self):
        uploaded_record = {
            "file_name": "uploaded_internal_nc.pdf",
            "sub_category": "L1:iatf_audit:internal_audit_ncs:P1 - Trichy Plant",
            "plant": "P1 - Trichy Plant",
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

        files = (
            result["document_groups"]["iatf_audit"]["secondary_options"]
            ["internal_audit"]["secondary_options"]["audit_ncs"]["plants"]
            ["P1 - Trichy Plant"]
        )
        self.assertIn("uploaded_internal_nc.pdf", files)

    def test_legacy_auditor_list_upload_is_kept_in_internal_audit(self):
        uploaded_record = {
            "file_name": "uploaded_auditor_list.pdf",
            "sub_category": (
                "L1:iatf_audit:auditors_list:internal_auditor_list:"
                "P2 - Guduvanchery Plant"
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

        files = (
            result["document_groups"]["iatf_audit"]["secondary_options"]
            ["internal_audit"]["secondary_options"]["auditors_list"]["plants"]
            ["P2 - Guduvanchery Plant"]
        )
        self.assertIn("uploaded_auditor_list.pdf", files)


if __name__ == "__main__":
    unittest.main()

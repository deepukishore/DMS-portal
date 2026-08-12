from services.document_library_service import DocumentLibraryService


def test_plant_wise_category_removed_from_library_navigation():
    categories = DocumentLibraryService.get_categories()
    assert all(category["key"] != "plant_wise_records" for category in categories)


def test_qms_sops_and_records_use_plant_and_department_structure():
    data = DocumentLibraryService.get_client_category_data("qms")
    groups = data.get("document_groups", {})

    for key in ["sops", "checklists"]:
        group = groups.get(key, {})
        assert group.get("plant_departments"), f"{key} should define plant-by-department folders"
        assert len(group["plant_departments"]) == 4, f"{key} should expose 4 plants"
        for plant, plant_data in group["plant_departments"].items():
            assert plant_data.get("departments"), f"{key} should define departments for {plant}"
            assert plant_data.get("files"), f"{key} should define files for {plant}"


def test_iatf_manual_is_under_qms_not_core_tools():
    qms_data = DocumentLibraryService.get_client_category_data("qms", qms_level="L1")
    core_tools_data = DocumentLibraryService.get_client_category_data("core_tools_manuals")

    assert qms_data["document_groups"]["iatf_manual"]["label"] == "IATF Manual"
    assert "iatf_manual" not in core_tools_data["primary_options"]

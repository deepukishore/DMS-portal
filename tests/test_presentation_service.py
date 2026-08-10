from services.presentation_service import plant_code


def test_plant_code_extracts_compact_identifiers():
    assert plant_code("P1 - Trichy Plant") == "P1"
    assert plant_code("P2 - Guduvanchery Plant") == "P2"
    assert plant_code("P3 - Guduvanchery Plant") == "P3"
    assert plant_code("P4 - Uttarakhand Plant") == "P4"
    assert plant_code("P2&3 - Guduvanchery Plants") == "P2&3"


def test_plant_code_preserves_unknown_or_empty_values():
    assert plant_code("Head Office") == "Head Office"
    assert plant_code("") == ""
    assert plant_code(None) == ""

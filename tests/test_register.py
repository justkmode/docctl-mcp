from docctl_mcp.register import compare_folder_to_register

REGISTER = {
    "NVN-JKR-ZZ-00-DR-A-0001": {"title": "Ground floor plan", "revision": "P01", "status": "S2"},
    "NVN-JKR-ZZ-01-DR-A-0002": {"title": "First floor plan", "revision": "P01", "status": "S2"},
    "NVN-JKR-ZZ-RF-DR-A-0003": {"title": "Roof plan", "revision": "P01", "status": "S2"},
}

ALL_GOOD = [
    "NVN-JKR-ZZ-00-DR-A-0001_P01.pdf",
    "NVN-JKR-ZZ-01-DR-A-0002_P01.pdf",
    "NVN-JKR-ZZ-RF-DR-A-0003_P01.pdf",
]

EMPTY = {"not_in_register": [], "missing_files": [], "revision_mismatch": []}


def test_everything_matches():
    assert compare_folder_to_register(ALL_GOOD, REGISTER) == EMPTY


def test_file_not_in_register():
    files = ALL_GOOD + ["NVN-JKR-ZZ-02-DR-A-0099_P01.pdf"]
    result = compare_folder_to_register(files, REGISTER)
    assert result["not_in_register"] == ["NVN-JKR-ZZ-02-DR-A-0099_P01.pdf"]


def test_register_entry_without_file():
    result = compare_folder_to_register(ALL_GOOD[:2], REGISTER)
    assert result["missing_files"] == ["NVN-JKR-ZZ-RF-DR-A-0003"]


def test_revision_mismatch():
    files = ["NVN-JKR-ZZ-00-DR-A-0001_P02.pdf"] + ALL_GOOD[1:]
    result = compare_folder_to_register(files, REGISTER)
    assert result["revision_mismatch"] == [
        {"doc_number": "NVN-JKR-ZZ-00-DR-A-0001", "register": "P01", "folder": "P02"}
    ]


def test_badly_named_file_is_ignored():
    files = ALL_GOOD + ["scan_final_v2.pdf"]
    assert compare_folder_to_register(files, REGISTER) == EMPTY
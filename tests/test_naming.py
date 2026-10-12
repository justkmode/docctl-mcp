from docctl_mcp.naming import parse_filename, check_naming

VALID = "NVN-JKR-ZZ-00-DR-A-0001_P01.pdf"


def test_parse_valid_filename():
    doc = parse_filename(VALID)
    assert doc.project == "NVN"
    assert doc.originator == "JKR"
    assert doc.volume == "ZZ"
    assert doc.level == "00"
    assert doc.doc_type == "DR"
    assert doc.role == "A"
    assert doc.number == "0001"
    assert doc.revision == "P01"
    assert doc.extension == "pdf"
    assert doc.doc_number == "NVN-JKR-ZZ-00-DR-A-0001"


def test_valid_filename_has_no_errors():
    assert check_naming(VALID) == []


def test_wrong_number_of_fields():
    errors = check_naming("NVN-JKR-00-DR-A-0001_P01.pdf")
    assert any("fields" in e.lower() for e in errors)


def test_unknown_doc_type():
    errors = check_naming("NVN-JKR-ZZ-00-XY-A-0001_P01.pdf")
    assert any("type" in e.lower() for e in errors)


def test_bad_revision():
    errors = check_naming("NVN-JKR-ZZ-00-DR-A-0001_R1.pdf")
    assert any("revision" in e.lower() for e in errors)


def test_lowercase_is_invalid():
    assert check_naming("nvn-jkr-zz-00-dr-a-0001_P01.pdf") != []


def test_number_must_be_4_digits():
    errors = check_naming("NVN-JKR-ZZ-00-DR-A-01_P01.pdf")
    assert any("number" in e.lower() for e in errors)
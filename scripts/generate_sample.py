"""Generate a fake construction project folder for docctl-mcp demos."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "sample_project"
DOCS = ROOT / "documents"

# Correct documents: (type, role, level, title, extension, revision)
GOOD = [
    ("DR", "A", "00", "Ground floor plan", "pdf", "P02"),
    ("DR", "A", "01", "First floor plan", "pdf", "P01"),
    ("DR", "A", "RF", "Roof plan", "pdf", "P01"),
    ("DR", "A", "ZZ", "Section A-A", "dwg", "P03"),
    ("DR", "A", "ZZ", "North elevation", "pdf", "C01"),
    ("DR", "S", "B1", "Foundation layout", "pdf", "P02"),
    ("DR", "S", "01", "Steel frame level 01", "dwg", "P01"),
    ("DR", "M", "00", "Ventilation layout level 00", "pdf", "P01"),
    ("DR", "E", "00", "Lighting layout level 00", "pdf", "P01"),
    ("SP", "A", "ZZ", "Architectural specification", "docx", "P01"),
    ("RP", "S", "ZZ", "Structural calculation report", "pdf", "C02"),
    ("M3", "A", "ZZ", "Architectural model", "ifc", "P04"),
    ("SH", "E", "ZZ", "Cable schedule", "xlsx", "P01"),
    ("CA", "C", "ZZ", "Drainage calculation", "pdf", "P01"),
]

# Badly named files: the kind of mess real projects have
BROKEN_NAMES = [
    "nvn-jkr-zz-00-dr-a-0101_P01.pdf",   # lowercase
    "NVN-JKR-ZZ-00-XY-A-0102_P01.pdf",   # unknown document type
    "NVN-JKR-00-DR-A-0103_P01.pdf",      # missing a field
    "NVN-JKR-ZZ-00-DR-A-0104_R1.pdf",    # bad revision
    "NVN-JKR-ZZ-00-DR-A-0105_P01.exe",   # forbidden extension
    "Ground floor plan FINAL v2.pdf",    # the classic
]


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    for old in DOCS.iterdir():  # start clean on every run
        old.unlink()

    register = []
    for i, (doc_type, role, level, title, ext, rev) in enumerate(GOOD, start=1):
        doc_number = f"NVN-JKR-ZZ-{level}-{doc_type}-{role}-{i:04d}"
        (DOCS / f"{doc_number}_{rev}.{ext}").touch()
        register.append({"doc_number": doc_number, "title": title, "revision": rev, "status": "S2"})

    # Register problems, on purpose:
    register[0]["revision"] = "P01"  # file is P02, register says P01 -> mismatch
    register.append({"doc_number": "NVN-JKR-ZZ-03-DR-A-0202", "title": "Third floor plan",
                     "revision": "P01", "status": "S2"})  # in register, but no file
    (DOCS / "NVN-JKR-ZZ-02-DR-A-0201_P01.pdf").touch()  # file exists, but not registered

    for name in BROKEN_NAMES:
        (DOCS / name).touch()

    with open(ROOT / "register.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["doc_number", "title", "revision", "status"])
        writer.writeheader()
        writer.writerows(register)

    print(f"Created {len(list(DOCS.iterdir()))} files and {len(register)} register rows in {ROOT}")


if __name__ == "__main__":
    main()
import re
from dataclasses import dataclass

DOC_TYPES = {"DR", "M3", "SP", "RP", "SH", "CA", "MI"}
ROLES = {"A", "C", "E", "M", "S", "W", "Z"}
EXTENSIONS = {"pdf", "dwg", "rvt", "ifc", "docx", "xlsx"}

@dataclass
class DocName:
    project: str
    originator: str
    volume: str
    level: str
    doc_type: str
    role: str
    number: str
    revision: str
    extension: str

    @property
    def doc_number(self) -> str:
         return f"{self.project}-{self.originator}-{self.volume}-{self.level}-{self.doc_type}-{self.role}-{self.number}"

def parse_filename(filename: str) -> DocName:
    # Step 1: split off the extension -> "NVN-JKR-ZZ-00-DR-A-0001_P01" and "pdf"
    stem, extension = filename.rsplit(".", 1)

    # Step 2: split off the revision -> "NVN-JKR-ZZ-00-DR-A-0001" and "P01"
    doc_part, revision = stem.split("_")

    # Step 3: split into the 7 fields -> ["NVN", "JKR", "ZZ", "00", "DR", "A", "0001"]
    fields = doc_part.split("-")

    # Step 4 (YOUR TURN): if fields does not have exactly 7 items,
    # raise ValueError("Expected 7 fields")
    if len(fields) != 7:
        raise ValueError("Expected 7 fields")

    # Step 5 (YOUR TURN): return DocName(...) with all 9 values
    return DocName(
        project=fields[0],
        originator=fields[1],
        volume=fields[2],
        level=fields[3],
        doc_type=fields[4],
        role=fields[5],
        number=fields[6],
        revision=revision,
        extension=extension
    )

# The naming standard as configuration: field -> rule
PATTERNS = {
    "project": r"[A-Z0-9]{3,6}",
    "originator": r"[A-Z0-9]{3,6}",
    "volume": r"[A-Z0-9]{2}",
    "level": r"[A-Z0-9]{2}",
    "number": r"\d{4}",
    "revision": r"[PC]\d{2}",
}
ALLOWED = {"doc_type": DOC_TYPES, "role": ROLES, "extension": EXTENSIONS}


def check_naming(filename: str) -> list[str]:
    # 1. Try to take the name apart. Garbage -> one friendly error, no crash.
    try:
        doc = parse_filename(filename)
    except ValueError as exc:
        return [f"Wrong structure ({exc}). Expected 7 fields like NVN-JKR-ZZ-00-DR-A-0001_P01.pdf"]

    # 2. Check every field against its rule, collect ALL problems.
    errors = []
    for field, pattern in PATTERNS.items():
        value = getattr(doc, field)
        if not re.fullmatch(pattern, value):
            errors.append(f"{field} '{value}' does not match rule {pattern}")
    for field, allowed in ALLOWED.items():
        value = getattr(doc, field)
        if value not in allowed:
            errors.append(f"{field} '{value}' is not allowed (allowed: {sorted(allowed)})")
    return errors


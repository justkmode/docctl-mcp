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
        raise NotImplementedError

def parse_filename(filename: str) -> DocName:
    raise NotImplementedError

def check_naming(filename: str) -> list[str]:
    raise NotImplementedError


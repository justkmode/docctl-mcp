from pathlib import Path

from docctl_mcp.naming import check_naming

for f in Path("sample_project/documents").iterdir():
    print(f.name, check_naming(f.name))
    
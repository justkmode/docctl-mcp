import csv  
from docctl_mcp.naming import parse_filename

def load_register(path):  
    register = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            register[row["doc_number"]] = row
    return register

def compare_folder_to_register(filenames, register):
    # 1. Go through each file in the folder
    folder = {}  # doc_number -> revision, like a mini register of the folder
    not_in_register = []

    for filename in filenames:
        try:
            doc = parse_filename(filename)  # your own function from yesterday!
        except ValueError:
            continue  # badly named -> check_naming's job, skip it

        folder[doc.doc_number] = doc.revision
        if doc.doc_number not in register:
            not_in_register.append(filename)

    # 2. Register entries with no file  (YOUR TURN)
    missing_files = []
    for doc_number in register: # finger down the register column
        if doc_number not in folder: # did I see it in the folder?
            missing_files.append(doc_number) # no -> missing

    # 3. Revision mismatch  (YOUR TURN)
    revision_mismatch = []
    for doc_number, folder_rev in folder.items():
        if doc_number in register:
            register_rev = register[doc_number] 
            if folder_rev != register_rev["revision"]:
                revision_mismatch.append(
                    {"doc_number": doc_number, "register": register_rev["revision"], "folder": folder_rev}
                )

    return {
        "not_in_register": sorted(not_in_register),
        "missing_files": sorted(missing_files),
        "revision_mismatch": revision_mismatch,
    }
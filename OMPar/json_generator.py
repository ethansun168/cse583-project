import os
import json
import re

template_json = "database_template.json"
database_root = "database"
output_json = "database.json"

reduction_reg = re.compile(r'reduction\s*\(')
private_reg = re.compile(r'private\s*\(')

with open(template_json, "r") as f:
    template_data = json.load(f)

database_dict = {}

for folder_name, meta in template_data.items():
    folder_path = os.path.join(database_root, folder_name)
    if not os.path.isdir(folder_path):
        print(f"Skipping: Folder not found -> {folder_path}")
        continue

    static_path = os.path.join(folder_path, "static.txt")
    # Version 1
    extracted_dynamic_path = os.path.join(folder_path, "dynamic.txt")
    # Version 2
    # extracted_dynamic_path = os.path.join(folder_path, "extracted_dynamic.txt")
    memory_access_count_path = os.path.join(folder_path, "memory_access_count.txt")

    if not (os.path.exists(extracted_dynamic_path) and os.path.exists(memory_access_count_path)):
        print(f"Skipping: Missing analysis file(s) in {folder_name}")
        continue

    original_str = meta["original"]
    if ":" not in original_str:
        print(f"Skipping: Invalid original format -> {original_str}")
        continue
    original_c_path, line_info = original_str.split(":", 1)
    original_c_filename = os.path.basename(original_c_path)
    expected_c_path = os.path.join(folder_path, original_c_filename)

    if not os.path.isfile(expected_c_path):
        print(f"Skipping: original .c file '{original_c_filename}' not found in {folder_name}")
        continue

    pragma_path = os.path.join(folder_path, "pragma.c")
    exist = os.path.exists(pragma_path)
    is_reduction = False
    is_private = False

    if exist:
        with open(pragma_path, "r") as f:
            pragma_content = f.read()
            is_reduction = bool(reduction_reg.search(pragma_content))
            is_private = bool(private_reg.search(pragma_content))

    item = {
        "code": os.path.abspath(os.path.join(folder_path, "code.c")),
        "pragma": os.path.abspath(pragma_path) if exist else "",
        "static_analysis": os.path.abspath(static_path),
        "dynamic_analysis": os.path.abspath(extracted_dynamic_path),
        "memory_access_count": os.path.abspath(memory_access_count_path),
        "original": f"{os.path.abspath(expected_c_path)}:{line_info}",
        "id": len(database_dict),
        "exist": int(exist),
        "private": int(is_private),
        "reduction": int(is_reduction)
    }

    database_dict[folder_name] = item

with open(output_json, "w") as f:
    json.dump(database_dict, f, indent=4)

print(f"\nDone. Valid entries written to {output_json}")

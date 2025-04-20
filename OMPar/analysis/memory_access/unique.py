# import os
# import re

# def process_memory_access_file(input_path, output_path):
#     """
#     Processes a memory_access.txt file to count occurrences of each unique (address, loopID)
#     combination and writes the result to an output file.
#     Each output line is in the format: <address>, <count>, <loopID>
#     """
#     # This regex expects lines in the format: "LOG: 0x7fffa06635c8 ID: 0"
#     log_pattern = re.compile(r"LOG\s*:\s*(0x[\da-fA-F]+)\s+ID\s*:\s*(\d+)")
    
#     # Dictionary to hold counts for each (address, loopID)
#     count_dict = {}

#     with open(input_path, "r") as infile:
#         for line_num, line in enumerate(infile, start=1):
#             line = line.strip()
#             match = log_pattern.match(line)
#             if match:
#                 address, loop_id = match.groups()
#                 key = (address, loop_id)
#                 count_dict[key] = count_dict.get(key, 0) + 1
#             else:
#                 # Optional: Output debug info if the line doesn't match the expected format.
#                 print(f"[{input_path}] Line {line_num} did not match: {line}")

#     # Sort keys by loopID (numeric) then by address (numeric interpretation of hex)
#     sorted_keys = sorted(count_dict.keys(), key=lambda x: (int(x[1]), int(x[0], 16)))
    
#     with open(output_path, "w") as outfile:
#         for address, loop_id in sorted_keys:
#             count = count_dict[(address, loop_id)]
#             outfile.write(f"{address}, {count}, {loop_id}\n")
    
#     print(f"Processed '{input_path}' -> '{output_path}'")

# def process_all_memory_access_files(database_dir):
#     """
#     Loops through all subdirectories in the database_dir.
#     For each subdirectory that has a 'memory_access.txt' file,
#     process it to create 'memory_access_count.txt'.
#     """
#     # Loop through all entries in the database_dir
#     for entry in os.listdir(database_dir):
#         subfolder = os.path.join(database_dir, entry)
#         if os.path.isdir(subfolder):
#             input_path = os.path.join(subfolder, "memory_access.txt")
#             if os.path.exists(input_path):
#                 output_path = os.path.join(subfolder, "memory_access_count.txt")
#                 process_memory_access_file(input_path, output_path)
#             else:
#                 print(f"Skipping '{subfolder}': 'memory_access.txt' not found.")

# def main():
#     # Determine the directory where this script resides.
#     script_dir = os.path.dirname(os.path.abspath(__file__))
    
#     # Construct the path to the database directory relative to the script.
#     # The expected structure is:
#     # test/
#     # ├── Dynamic/
#     # │   └── unique.py        <-- this script
#     # └── database/
#     #     ├── test1/
#     #     │    └── memory_access.txt
#     #     ├── test2/
#     #     │    └── memory_access.txt
#     #     └── ... etc.
#     database_dir = os.path.join(script_dir, "..", "database")

#     if not os.path.isdir(database_dir):
#         print(f"Database folder not found: {database_dir}")
#         return

#     process_all_memory_access_files(database_dir)

# if __name__ == "__main__":
#     main()


# copy the memory_access_count.txt to the folder haveing the same memory_access.txt and delete the memory_access.txt
import os
import re
import hashlib
import shutil

def hash_file(path):
    """Generate a hash for the file contents using MD5."""
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def process_memory_access_file(input_path, output_path):
    """
    Process a memory_access.txt file to count the occurrences of each unique (address, loopID)
    pair and write the result to memory_access_count.txt.
    Then delete the original memory_access.txt.
    """
    log_pattern = re.compile(r"LOG\s*:\s*(0x[\da-fA-F]+)\s+ID\s*:\s*(\d+)")
    count_dict = {}

    with open(input_path, "r") as infile:
        for line_num, line in enumerate(infile, start=1):
            line = line.strip()
            match = log_pattern.match(line)
            if match:
                address, loop_id = match.groups()
                key = (address, loop_id)
                count_dict[key] = count_dict.get(key, 0) + 1
            else:
                print(f"[{input_path}] Line {line_num} did not match: {line}")

    # Sort first by loop ID (as integer), then by address (as hex)
    sorted_keys = sorted(count_dict.keys(), key=lambda x: (int(x[1]), int(x[0], 16)))

    with open(output_path, "w") as outfile:
        for address, loop_id in sorted_keys:
            count = count_dict[(address, loop_id)]
            outfile.write(f"{address}, {count}, {loop_id}\n")

    print(f"Processed '{input_path}' -> '{output_path}'")

    # Delete the original memory_access.txt after processing
    try:
        os.remove(input_path)
        print(f"Deleted original: {input_path}")
    except Exception as e:
        print(f"[Error] Could not delete '{input_path}': {e}")

def process_all_memory_access_files(database_dir):
    """
    Go through all folders in the database directory.
    If two memory_access.txt files are identical (by hash), only process the first
    and copy its result to the others.
    Delete memory_access.txt after processing or copying.
    """
    hash_map = {}  # Maps file hash to the path of the generated count file

    for entry in os.listdir(database_dir):
        subfolder = os.path.join(database_dir, entry)
        if not os.path.isdir(subfolder):
            continue

        input_path = os.path.join(subfolder, "memory_access.txt")
        output_path = os.path.join(subfolder, "memory_access_count.txt")

        if not os.path.exists(input_path):
            print(f"Skipping '{subfolder}': 'memory_access.txt' not found.")
            continue

        if os.path.exists(output_path):
            print(f"Skipping '{subfolder}': 'memory_access_count.txt' already exists.")
            continue

        file_hash = hash_file(input_path)

        if file_hash in hash_map:
            # Copy result from existing identical file
            existing_output = hash_map[file_hash]
            shutil.copy(existing_output, output_path)
            print(f"Copied result for duplicate '{entry}' -> '{output_path}'")

            # Delete the duplicate memory_access.txt
            try:
                os.remove(input_path)
                print(f"Deleted original: {input_path}")
            except Exception as e:
                print(f"[Error] Could not delete '{input_path}': {e}")

        else:
            # First time seeing this unique file content
            process_memory_access_file(input_path, output_path)
            hash_map[file_hash] = output_path

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    database_dir = os.path.join(script_dir, "..", "database_test")

    if not os.path.isdir(database_dir):
        print(f"Database folder not found: {database_dir}")
        return

    process_all_memory_access_files(database_dir)

if __name__ == "__main__":
    main()




## copy only when memory_access.txt && ID are the same
# import os
# import re
# import hashlib
# import shutil
# from typing import List, Set, Tuple, Dict

# # ---------- helpers ---------------------------------------------------------- #
# def md5_of_file(path: str) -> str:
#     """Return the MD5 hash (hex) of the file contents."""
#     h = hashlib.md5()
#     with open(path, "rb") as f:
#         h.update(f.read())
#     return h.hexdigest()


# def load_loop_ids(id_file: str) -> Set[str]:
#     """
#     Parse ID.txt and return a set of loop‑id strings that should be kept.
#     Accepts lines like:
#         LoopID = 0
#         LoopID = 7  # low confidence ...
#     """
#     ids: Set[str] = set()
#     id_re = re.compile(r"LoopID\s*=\s*(\d+)")
#     if not os.path.isfile(id_file):
#         return ids          # empty ⇒ 代表沒有指定，要保留全部
#     with open(id_file, "r") as f:
#         for line in f:
#             m = id_re.search(line)
#             if m:
#                 ids.add(m.group(1))
#     return ids


# # ---------- core ------------------------------------------------------------- #
# def process_memory_access_file(
#     input_path: str,
#     output_path: str,
#     id_set: Set[str]
# ) -> None:
#     """
#     Build memory_access_count.txt **filtered by id_set** and **replace address
#     with the hex difference from previous address inside the same loop‑id**.
#     First address of each id → diff = 0.
#     """
#     log_re = re.compile(r"LOG\s*:\s*(0x[\da-fA-F]+)\s+ID\s*:\s*(\d+)")
#     raw_counts: Dict[Tuple[str, str], int] = {}

#     # 1) read & count
#     with open(input_path, "r") as f:
#         for idx, line in enumerate(f, start=1):
#             m = log_re.match(line.strip())
#             if not m:
#                 print(f"[warn] {input_path}:{idx} - unmatched line: {line.strip()}")
#                 continue
#             addr, loop_id = m.groups()
#             if id_set and loop_id not in id_set:
#                 continue                      # filter out unwanted loop ids
#             key = (addr, loop_id)
#             raw_counts[key] = raw_counts.get(key, 0) + 1

#     # 2) regroup by loop‑id so we can compute diffs
#     groups: Dict[str, List[Tuple[str, int]]] = {}
#     for (addr, loop_id), count in raw_counts.items():
#         groups.setdefault(loop_id, []).append((addr, count))

#     # 3) write output
#     with open(output_path, "w") as out:
#         for loop_id in sorted(groups, key=int):
#             # sort addresses in ascending order
#             entries = sorted(groups[loop_id], key=lambda x: int(x[0], 16))
#             prev_addr_int: int | None = None
#             for addr_hex, cnt in entries:
#                 curr_int = int(addr_hex, 16)
#                 diff_int = 0 if prev_addr_int is None else curr_int - prev_addr_int
#                 diff_hex = hex(diff_int)
#                 out.write(f"{diff_hex}, {cnt}, {loop_id}\n")
#                 prev_addr_int = curr_int

#     print(f"[ok] {input_path} → {output_path}")
#     os.remove(input_path)       # remove original after processing


# def hash_key(mem_hash: str, ids: Set[str]) -> str:
#     """
#     Combine memory_access.txt hash with the selected id list so that folders
#     that share the same mem file but keep **different** id sets will *not*
#     be treated as duplicates.
#     """
#     ids_part = ",".join(sorted(ids)) if ids else "ALL"
#     return hashlib.md5(f"{mem_hash}:{ids_part}".encode()).hexdigest()


# def process_all_memory_access(database_dir: str) -> None:
#     """
#     Iterate every sub‑folder under <database_dir> and convert memory_access.txt.
#     Handles duplicate detection by (file‑hash + id‑set).
#     """
#     processed_cache: Dict[str, str] = {}   # composite‑hash → output path

#     for sub in os.listdir(database_dir):
#         sub_path = os.path.join(database_dir, sub)
#         if not os.path.isdir(sub_path):
#             continue

#         mem_file = os.path.join(sub_path, "memory_access.txt")
#         id_file  = os.path.join(sub_path, "ID.txt")
#         out_file = os.path.join(sub_path, "memory_access_count.txt")

#         if not os.path.isfile(mem_file):
#             print(f"[skip] {sub}: memory_access.txt not found")
#             continue
#         if os.path.isfile(out_file):
#             print(f"[skip] {sub}: already processed")
#             continue

#         ids = load_loop_ids(id_file)   # may be empty
#         comp_hash = hash_key(md5_of_file(mem_file), ids)

#         if comp_hash in processed_cache:
#             # identical content & id‑set ⇒ just copy
#             shutil.copy(processed_cache[comp_hash], out_file)
#             os.remove(mem_file)        # still remove the duplicate raw file
#             print(f"[dup] copied result → {out_file}")
#             continue

#         # first time seeing this combination
#         process_memory_access_file(mem_file, out_file, ids)
#         processed_cache[comp_hash] = out_file


# # ---------- entry ------------------------------------------------------------ #
# def main() -> None:
#     here = os.path.dirname(os.path.abspath(__file__))
#     db_dir = os.path.join(here, "..", "database_test")
#     if not os.path.isdir(db_dir):
#         print(f"[error] database dir not found: {db_dir}")
#         return
#     process_all_memory_access(db_dir)


# if __name__ == "__main__":
#     main()








# ## for database_test

# # import os
# # import re
# # import hashlib
# # import shutil

# # def hash_file(path):
# #     """產生檔案內容的 MD5 雜湊值（目前此函式在單一檔案處理情境下未使用）。"""
# #     hasher = hashlib.md5()
# #     with open(path, "rb") as f:
# #         hasher.update(f.read())
# #     return hasher.hexdigest()

# # def process_memory_access_file(input_path, output_path):
# #     """
# #     處理 memory_access.txt 檔案，統計每個 (address, loopID) 之組合出現次數，
# #     並將結果寫入 memory_access_count.txt。
# #     最後刪除原始的 memory_access.txt。
# #     """
# #     log_pattern = re.compile(r"LOG\s*:\s*(0x[\da-fA-F]+)\s+ID\s*:\s*(\d+)")
# #     count_dict = {}

# #     with open(input_path, "r") as infile:
# #         for line_num, line in enumerate(infile, start=1):
# #             line = line.strip()
# #             match = log_pattern.match(line)
# #             if match:
# #                 address, loop_id = match.groups()
# #                 key = (address, loop_id)
# #                 count_dict[key] = count_dict.get(key, 0) + 1
# #             else:
# #                 print(f"[{input_path}] 第 {line_num} 行格式不符: {line}")

# #     # 先以 loopID（轉成整數）排序，再以 address（轉為十六進位整數）排序
# #     sorted_keys = sorted(count_dict.keys(), key=lambda x: (int(x[1]), int(x[0], 16)))

# #     with open(output_path, "w") as outfile:
# #         for address, loop_id in sorted_keys:
# #             count = count_dict[(address, loop_id)]
# #             outfile.write(f"{address}, {count}, {loop_id}\n")

# #     print(f"已處理 '{input_path}' -> '{output_path}'")

# #     # 處理完後刪除原始的 memory_access.txt
# #     try:
# #         os.remove(input_path)
# #         print(f"已刪除原始檔案: {input_path}")
# #     except Exception as e:
# #         print(f"[Error] 刪除 '{input_path}' 時發生錯誤: {e}")

# # def process_all_memory_access_files(database_dir):
# #     """
# #     處理 database 資料夾下的 memory_access.txt 檔案，
# #     若存在則產生相應的 memory_access_count.txt，
# #     處理完成後刪除 memory_access.txt。
# #     """
# #     input_path = os.path.join(database_dir, "memory_access.txt")
# #     output_path = os.path.join(database_dir, "memory_access_count.txt")

# #     if not os.path.exists(input_path):
# #         print(f"跳過處理：找不到 '{input_path}'")
# #         return

# #     if os.path.exists(output_path):
# #         print(f"跳過處理：'{output_path}' 已存在")
# #         return

# #     process_memory_access_file(input_path, output_path)

# # def main():
# #     # 取得目前程式所在路徑，再設定 database 資料夾路徑
# #     script_dir = os.path.dirname(os.path.abspath(__file__))
# #     database_dir = os.path.join(script_dir, "..", "database_test")

# #     if not os.path.isdir(database_dir):
# #         print(f"找不到 database 資料夾: {database_dir}")
# #         return

# #     process_all_memory_access_files(database_dir)

# # if __name__ == "__main__":
# #     main()

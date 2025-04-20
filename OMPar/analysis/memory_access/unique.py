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


import os
import re
import glob

# Regular expression that matches lines like:
# LOG: 0x7fffa06635c8 ID: 0
# - It captures the hex address (starting with 0x and digits/letters) and the ID (digits)
log_pattern = re.compile(r"LOG\s*:\s*(0x[\da-fA-F]+)\s+ID\s*:\s*(\d+)")

def process_file(filename):
    # Dictionary mapping each ID to a list of addresses (order preserved)
    addresses_by_id = {}

    with open(filename, "r") as file:
        for line_num, line in enumerate(file, start=1):
            line = line.strip()
            match = log_pattern.match(line)
            if match:
                address, id_str = match.groups()
                addresses_by_id.setdefault(id_str, []).append(address)
            else:
                # Uncomment the line below for debug info on unmatched lines.
                # print(f"File '{filename}', line {line_num} did not match: {line}")
                continue

    # Create the output file name: originalname_diff.txt
    base, ext = os.path.splitext(filename)
    output_filename = f"{base}_diff.txt"

    with open(output_filename, "w") as outfile:
        # Process each unique ID (sorted numerically)
        for id_str in sorted(addresses_by_id, key=lambda x: int(x)):
            addresses = addresses_by_id[id_str]
            diffs = []
            if len(addresses) > 1:
                # Convert the first address from hex to integer and use as baseline.
                previous = int(addresses[0], 16)
                # For each subsequent address, compute the difference (in decimal).
                for addr in addresses[1:]:
                    current = int(addr, 16)
                    diff = current - previous
                    diffs.append(str(diff))
                    previous = current
            # Build output: start with the ID and, if available, append the differences.
            line_out = id_str
            if diffs:
                line_out += " " + " ".join(diffs)
            outfile.write(line_out + "\n")

    print(f"Processed '{filename}' -> '{output_filename}'")

def main():
    # Process all .txt files in the current directory, excluding those already ending with _diff.txt.
    for filename in glob.glob("*.txt"):
        if filename.endswith("_diff.txt"):
            continue
        process_file(filename)

if __name__ == "__main__":
    main()

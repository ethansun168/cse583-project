import os
import re
import glob

# Updated regex: 
# Allows some optional spaces around "ID:" and uses non-greedy capture for the address.
log_pattern = re.compile(r"LOG\s*:\s*(.*?)\s+ID\s*:\s*(\d+)")

def process_file(filename):
    id_addresses = {}
    
    with open(filename, "r") as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            match = log_pattern.match(line)
            if match:
                address, id_num = match.groups()
                # Use setdefault for cleaner code.
                id_addresses.setdefault(id_num, set()).add(address)
            else:
                # Print debug info for unmatched lines.
                print(f"File '{filename}' line {line_num}: No match for: {line}")
    
    # Write results to a new file named with _unique before the .txt extension.
    base, ext = os.path.splitext(filename)
    output_filename = f"{base}_unique.txt"
    
    with open(output_filename, "w") as outfile:
        # Sorting IDs numerically for clarity.
        for id_num in sorted(id_addresses, key=lambda x: int(x)):
            for address in sorted(id_addresses[id_num]):  # Sorting addresses if desired.
                outfile.write(f"LOG : {address} ID:{id_num}\n")
    
    print(f"Processed '{filename}' -> '{output_filename}'")

def main():
    # Process all .txt files in the current directory,
    # skipping files that are output files.
    for filename in glob.glob("*.txt"):
        if filename.endswith("_unique.txt"):
            continue
        process_file(filename)

if __name__ == "__main__":
    main()

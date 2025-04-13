import json
import re
from collections import defaultdict
database = "database.jsonl"

def static(file):
    text = file.read()
    # Regex pattern to match each loop analysis section
    pattern = re.compile(
        r"=== Loop Analysis \(ID: (\d+), Header: [^)]+\) ===.*?"
        r"NumInstructions: (\d+).*?"
        r"- Loads:\s+(\d+).*?"
        r"- Stores:\s+(\d+).*?"
        r"- Branches:\s+(\d+)",
        re.DOTALL
    )

    # Extract all matches
    results = pattern.findall(text)

    # Convert to structured data
    loops = [
        {
            "Loop ID": int(loop_id),
            "NumInstructions": int(instr),
            "Loads": int(loads),
            "Stores": int(stores),
            "Branches": int(branches)
        }
        for loop_id, instr, loads, stores, branches in results
    ]
    return loops

def dynamic(file):

    text = file.read()
    loop_data = defaultdict(lambda: defaultdict(dict))
    current_loop_id = None
    current_depth = None
    in_data_access = False

    for line in text.splitlines():
        loop_header = re.match(r"^\s*=== Loop \(ID:\s*(\d+)\):\s*%(\d+)\s*\(Depth\s*=\s*(\d+)\)\s*===$", line)
        if loop_header:
            current_loop_id = int(loop_header.group(1))
            current_depth = int(loop_header.group(3))
            loop_data[current_loop_id]['depth'] = current_depth
            loop_data[current_loop_id]['data_access'] = {}
            in_data_access = False
            continue

        if "--- Branch Counts ---" in line:
            in_data_access = False
            continue
        elif "--- Data Access Count ---" in line:
            in_data_access = True
            continue

        # Parse data access
        if in_data_access:
            instr_match = re.match(r"\s*Instr count: (\d+) x \d+ = (\d+)", line)

            if instr_match:
                if 'instr_count' not in loop_data[current_loop_id]['data_access']:
                    loop_data[current_loop_id]['data_access']['instr_count'] = 0
                loop_data[current_loop_id]['data_access']['instr_count'] += int(instr_match.group(1))
            load_match = re.match(r"\s*Load count: (\d+) x \d+ = (\d+)", line)
            if load_match:
                if 'load_count' not in loop_data[current_loop_id]['data_access']:
                    loop_data[current_loop_id]['data_access']['load_count'] = 0
                loop_data[current_loop_id]['data_access']['load_count'] += int(load_match.group(1))
            store_match = re.match(r"\s*Store count: (\d+) x \d+ = (\d+)", line)
            if store_match:
                if 'store_count' not in loop_data[current_loop_id]['data_access']:
                    loop_data[current_loop_id]['data_access']['store_count'] = 0
                loop_data[current_loop_id]['data_access']['store_count'] += int(store_match.group(1))
    return loop_data

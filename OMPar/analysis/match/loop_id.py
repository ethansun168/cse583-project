import os
import re
import difflib

def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def simplify_for_condition(line):
    """
    將 for(...) 中的第二欄條件（如 j < SIZE）替換成 _
    e.g. for(j=0; j<SIZE; j++) → for(j=0; _; j++)
    """
    match = re.match(r'(.*for\s*\(.*?;)(.*?)(;.*?\))', line)
    if match:
        return match.group(1) + ' _ ' + match.group(3)
    return line


def normalize(code):
    """簡化程式碼：移除空白、tab、換行與多餘括號空格"""
    lines = code.split('\n')
    lines = [simplify_for_condition(line) for line in lines]  # ✅ 把 for 的中間條件換成 "_"
    code = '\n'.join(lines)
    code = re.sub(r'[\s{}]+', '', code)           # 移除空白、縮排、大括號
    code = re.sub(r'\(\s*', '(', code)
    code = re.sub(r'\s*\)', ')', code)
    code = re.sub(r'[()]', '', code)              # 💡 新增：移除所有括號
    return code

def extract_loops(loop_file_path, n_lines):
    """提取 loop_analysis_output.txt 中每個 loop 的前 n_lines 行 snippet"""
    loops = {}
    current_id = None
    snippet_lines = []
    with open(loop_file_path, 'r') as f:
        for line in f:
            if line.startswith("LoopID"):
                if current_id is not None:
                    loops[current_id] = normalize('\n'.join(snippet_lines[:n_lines]))
                match = re.match(r"LoopID\s+(\d+)", line)
                current_id = int(match.group(1))
                snippet_lines = [line.split(',', 1)[1]]
            else:
                snippet_lines.append(line)
        if current_id is not None:
            loops[current_id] = normalize('\n'.join(snippet_lines[:n_lines]))
    return loops

def extract_first_loop(code_file_path):
    """從 code.c 中抓取第一個 for loop 的前 N 行（N = min(3, available lines))"""
    with open(code_file_path, 'r') as f:
        lines = f.readlines()

    collecting = False
    snippet = []

    for line in lines:
        if not collecting and 'for' in line:
            collecting = True
        if collecting:
            snippet.append(line)
            if len(snippet) == 3:  # 最多三行
                break

    return normalize(''.join(snippet)), len(snippet)

def process_directory(dir_path, threshold=0.85):
    loop_path = os.path.join(dir_path, 'loop_analysis_output.txt')
    code_path = os.path.join(dir_path, 'code.c')
    output_path = os.path.join(dir_path, 'ID.txt')

    if not os.path.exists(loop_path) or not os.path.exists(code_path):
        print(f"⚠️  Skipping {dir_path}: missing code.c or loop_analysis_output.txt")
        return "skip"

    code_snippet, code_line_count = extract_first_loop(code_path)

    current_id = None
    snippet_lines = []
    best_score = 0
    best_id = None
    best_candidate = ""

    with open(loop_path, 'r') as f:
        for line in f:
            if line.startswith("LoopID"):
                if current_id is not None:
                    candidate = normalize('\n'.join(snippet_lines[:code_line_count]))
                    if candidate == code_snippet:
                        with open(output_path, 'w') as out:
                            out.write(f"LoopID = {current_id}\n")
                        print(f"\n✅ Exact match: LoopID {current_id}")
                        return "pass"

                    score = similarity(candidate, code_snippet)
                    if score > best_score:
                        best_score = score
                        best_id = current_id
                        best_candidate = candidate

                match = re.match(r"LoopID\s+(\d+)", line)
                current_id = int(match.group(1))
                snippet_lines = [line.split(',', 1)[1]]
            else:
                snippet_lines.append(line)

        # 處理最後一段 loop
        if current_id is not None:
            candidate = normalize('\n'.join(snippet_lines[:code_line_count]))
            if candidate == code_snippet:
                with open(output_path, 'w') as out:
                    out.write(f"LoopID = {current_id}\n")
                print(f"\n✅ Exact match: LoopID {current_id}")
                return "pass"

            score = similarity(candidate, code_snippet)
            if score > best_score:
                best_score = score
                best_id = current_id
                best_candidate = candidate

    # 即使低於 threshold，也強制選出最佳 match
    with open(output_path, 'w') as f:
        match_type = "fuzzy match" if best_score >= threshold else "low confidence"
        f.write(f"LoopID = {best_id}  # {match_type} (score={best_score:.2f})\n")

    if best_score >= threshold:
        print(f"\n🟡 Fuzzy match: LoopID {best_id} (score={best_score:.2f})")
    else:
        print(f"\n🔴 Low-confidence match: LoopID {best_id} (score={best_score:.2f})")

    print("----- Normalized code.c -----")
    print(code_snippet)
    print("----- Best matched loop -----")
    print(best_candidate)

    return "pass"


def main():
    base_dir = "../database_test"
    passed = 0
    failed = 0
    skipped = 0

    for folder in os.listdir(base_dir):
        full_path = os.path.join(base_dir, folder)
        if os.path.isdir(full_path):
            result = process_directory(full_path, threshold=0.95)
            if result == "pass":
                passed += 1
            elif result == "fail":
                failed += 1
            elif result == "skip":
                skipped += 1

    print("\n=== Summary ===")
    print(f"Passed  : {passed}")
    print(f"Failed  : {failed}")
    print(f"Skipped : {skipped}")


if __name__ == "__main__":
    main()

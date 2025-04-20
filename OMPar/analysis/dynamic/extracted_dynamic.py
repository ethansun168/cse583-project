#!/usr/bin/env python3
import os
import re

# 根目錄：請根據實際情況修改
ROOT_DIR = "../database_test"

# 解析 ID.txt，回傳第一個找到的 LoopID（整數）
def read_loop_id(id_path):
    with open(id_path, 'r', encoding='utf-8') as f:
        text = f.read()
    m = re.search(r'LoopID\s*=\s*(\d+)', text)
    return int(m.group(1)) if m else None

# 處理 single dynamic.txt，根據目標 loop_id 計算三個統計值
def extract_metrics(dynamic_path, loop_id):
    # print(f"loop_id: {loop_id}")
    data_access = 0
    instr_count = 0
    branch_count = 0

    in_target = False
    in_branch = False
    in_data = False

    # 用來檢查是否進入下一個 loop 或結束
    loop_header_re = re.compile(r'^\s*===\s*Loop\s*\(\s*ID\s*:\s*(\d+)\s*\)\s*:')

    with open(dynamic_path, 'r', encoding='utf-8') as f:
        for line in f:
            # print(f"line: {line}")
            # 檢查是否是新的 Loop header
            m = loop_header_re.match(line)
            if m:
                # print(f"m: {m}")
                curr_id = int(m.group(1))
                if curr_id == loop_id:
                    # print(f"find id: {loop_id}\n")
                    in_target = True
                else:
                    # 如果已經在目標區塊內，碰到新的 Loop 就結束
                    if in_target:
                        break
                    in_target = False

            if not in_target:
                continue

            # 檢查 Section 標頭
            if line.strip() == '--- Branch Counts ---':
                in_branch = True
                in_data = False
                continue
            if line.strip() == '--- Data Access Count ---':
                in_data = True
                in_branch = False
                continue

            # 如果在 branch section，累加所有 Frequency
            if in_branch:
                m_freq = re.search(r'Frequency\s*=\s*(\d+)', line)
                if m_freq:
                    # print(f"branch: {int(m_freq.group(1))}\n")
                    branch_count += int(m_freq.group(1))
                continue

            # 如果在 data access section，分別抓 Instr / Load / Store
            if in_data:
                m_instr = re.search(r'Instr count:.*=\s*(\d+)', line)
                if m_instr:
                    # print(f"instr_count: {int(m_instr.group(1))}\n")
                    instr_count += int(m_instr.group(1))
                    continue
                m_load = re.search(r'Load count:.*=\s*(\d+)', line)
                if m_load:
                    # print(f"data_access_load: {int(m_load.group(1))}\n")
                    data_access += int(m_load.group(1))
                    continue
                m_store = re.search(r'Store count:.*=\s*(\d+)', line)
                if m_store:
                    # print(f"data_access_store: {int(m_store.group(1))}\n")
                    data_access += int(m_store.group(1))
                    continue

    return data_access, instr_count, branch_count

def main():
    for folder in os.listdir(ROOT_DIR):
        dir_path = os.path.join(ROOT_DIR, folder)
        if not os.path.isdir(dir_path):
            continue

        id_path = os.path.join(dir_path, 'ID.txt')
        dyn_path = os.path.join(dir_path, 'dynamic.txt')
        out_path = os.path.join(dir_path, 'extracted_dynamic.txt')

        if not os.path.isfile(id_path) or not os.path.isfile(dyn_path):
            print(f"[WARN] skip {folder}: missing ID.txt or dynamic.txt")
            continue

        loop_id = read_loop_id(id_path)
        if loop_id is None:
            print(f"[WARN] cannot find LoopID in {id_path}")
            continue

        data_access, instr_count, branch_count = extract_metrics(dyn_path, loop_id)

        # 如果三個指標都為 0，就印出資料夾名稱
        if data_access == 0 and instr_count == 0 and branch_count == 0:
            print(f"[ZERO] all zero in folder: {folder}")

        # 輸出結果
        with open(out_path, 'w', encoding='utf-8') as fout:
            fout.write(f"DataAccessCount: {data_access}\n")
            fout.write(f"InstructionCount: {instr_count}\n")
            fout.write(f"BranchCount: {branch_count}\n")



# def main():
#     TARGET = 'adriacabeza_PAR_mandel-omp-for-dynamic.c_3'

#     for folder in os.listdir(ROOT_DIR):
#         # 只處理名稱符合 TARGET 的資料夾
#         if folder != TARGET:
#             continue

#         dir_path = os.path.join(ROOT_DIR, folder)
#         if not os.path.isdir(dir_path):
#             continue

#         id_path = os.path.join(dir_path, 'ID.txt')
#         dyn_path = os.path.join(dir_path, 'dynamic.txt')
#         out_path = os.path.join(dir_path, 'extracted_dynamic.txt')

#         if not os.path.isfile(id_path) or not os.path.isfile(dyn_path):
#             print(f"[WARN] skip {folder}: missing ID.txt or dynamic.txt")
#             continue

#         loop_id = read_loop_id(id_path)
#         if loop_id is None:
#             print(f"[WARN] cannot find LoopID in {id_path}")
#             continue

#         data_access, instr_count, branch_count = extract_metrics(dyn_path, loop_id)

#         # 輸出結果
#         with open(out_path, 'w', encoding='utf-8') as fout:
#             fout.write(f"DataAccessCount: {data_access}\n")
#             fout.write(f"InstructionCount: {instr_count}\n")
#             fout.write(f"BranchCount: {branch_count}\n")

#         print(f"[OK] {folder} → extracted_dynamic.txt")


if __name__ == "__main__":
    main()

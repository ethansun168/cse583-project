import json
import os
import torch
from .model import OMPify
from torch.utils.data import Dataset, random_split

# def parse_dynamic(dynamic_text):
#     """
#     Parse the dynamic analysis text (dynamic.txt) and return a fixed-length feature vector.
#     
#     Updated to extract 9 features:
#       1) Number of branch entries
#       2) Average branch frequency
#       3) Maximum branch frequency
#       4) Total branch frequency
#       5) Ratio of max branch freq to average branch freq
#       6) Number of basic blocks
#       7) Average instruction count per basic block
#       8) Average load count per basic block
#       9) Average store count per basic block
#     """
#     branch_freqs = []
#     
#     # Containers for data access count metrics.
#     bb_instr_counts = []
#     bb_load_counts = []
#     bb_store_counts = []
#     
#     lines = dynamic_text.splitlines()
#     current_block_instr = None
#     current_block_load = None
#     current_block_store = None
#     
#     in_branch_section = False
#     in_data_access_section = False
#     
#     for line in lines:
#         line = line.strip()
#         # Check for the beginning of sections.
#         if line.startswith("--- Branch Counts ---"):
#             in_branch_section = True
#             in_data_access_section = False
#             continue
#         if line.startswith("--- Data Access Count ---"):
#             in_branch_section = False
#             in_data_access_section = True
#             continue
#         if line.startswith("==="):
#             in_branch_section = False
#             in_data_access_section = False
#             continue
#         
#         # Process Branch Counts section.
#         if in_branch_section and "Frequency =" in line:
#             try:
#                 freq = float(line.split("Frequency =")[1].split()[0])
#                 branch_freqs.append(freq)
#             except Exception:
#                 pass
#
#         # Process Data Access Count section.
#         if in_data_access_section:
#             # When encountering a new basic block line:
#             if line.startswith("BasicBlock"):
#                 # If there is already data for a block, save it.
#                 if current_block_instr is not None:
#                     bb_instr_counts.append(current_block_instr)
#                     bb_load_counts.append(current_block_load)
#                     bb_store_counts.append(current_block_store)
#                 # Reset current block counts.
#                 current_block_instr = None
#                 current_block_load = None
#                 current_block_store = None
#             elif line.startswith("Instr count:"):
#                 try:
#                     parts = line.split("=")[-1].split()
#                     current_block_instr = float(parts[0])
#                 except Exception:
#                     current_block_instr = 0.0
#             elif line.startswith("Load count:"):
#                 try:
#                     parts = line.split("=")[-1].split()
#                     current_block_load = float(parts[0])
#                 except Exception:
#                     current_block_load = 0.0
#             elif line.startswith("Store count:"):
#                 try:
#                     parts = line.split("=")[-1].split()
#                     current_block_store = float(parts[0])
#                 except Exception:
#                     current_block_store = 0.0
#     
#     # After the loop, add the last block if it exists.
#     if in_data_access_section and current_block_instr is not None:
#         bb_instr_counts.append(current_block_instr)
#         bb_load_counts.append(current_block_load)
#         bb_store_counts.append(current_block_store)
#     
#     # Compute branch features.
#     num_branches = len(branch_freqs)
#     avg_branch = sum(branch_freqs) / num_branches if num_branches > 0 else 0.0
#     max_branch = max(branch_freqs) if branch_freqs else 0.0
#     total_branch_freq = sum(branch_freqs) if branch_freqs else 0.0
#     ratio_max_avg_branch = max_branch / avg_branch if avg_branch != 0 else 0.0
#
#     # Compute basic block features.
#     num_blocks = len(bb_instr_counts)
#     avg_instr = sum(bb_instr_counts) / num_blocks if num_blocks > 0 else 0.0
#     avg_load = sum(bb_load_counts) / num_blocks if num_blocks > 0 else 0.0
#     avg_store = sum(bb_store_counts) / num_blocks if num_blocks > 0 else 0.0
#
#     # Build the final feature vector (now 9-dimensional)
#     features = [
#         num_branches,             # 1
#         avg_branch,               # 2
#         max_branch,               # 3
#         total_branch_freq,        # 4
#         ratio_max_avg_branch,     # 5
#         num_blocks,               # 6
#         avg_instr,                # 7
#         avg_load,                 # 8
#         avg_store                 # 9
#     ]
#     
#     return features
#
#
#
# def parse_memory(memory_text):
#     """
#     Parse the memory access count file (memory_access_count.txt) and return a fixed-length vector.
#     Instead of simply accumulating access counts, we extract:
#       - The number of unique memory access records.
#       - The maximum access count among the records.
#       - The average (mean) access count.
#       - The variance of the access counts.
#     These features can help indicate how intensive the memory accesses are in the loop.
#     """
#     if not memory_text:
#         return [0.0, 0.0, 0.0, 0.0]
#     lines = memory_text.splitlines()
#     access_counts = []
#     for line in lines:
#         parts = line.split(',')
#         if len(parts) >= 2:
#             try:
#                 # parts[1] is the access count; strip any whitespace and convert to float
#                 count = float(parts[1].strip())
#                 access_counts.append(count)
#             except Exception:
#                 continue
#     if len(access_counts) == 0:
#         return [0.0, 0.0, 0.0, 0.0]
#     num_records = float(len(access_counts))
#     max_access = max(access_counts)
#     mean_access = sum(access_counts) / num_records
#     variance = sum((x - mean_access) ** 2 for x in access_counts) / num_records
#     return [num_records, max_access, mean_access, variance]
#
#
#
# class InputFeatures(object):
#     """A single training/test features for a sample."""
#     def __init__(self,
#                  input_tokens_1,
#                  input_ids_1,
#                  position_idx_1,
#                  dfg_to_code_1,
#                  dfg_to_dfg_1,
#                  pragma_label, private_label, reduction_label,
#                  dynamic_features=None,
#                  memory_features=None
#     ):
#         # The first code function representation.
#         self.input_tokens_1 = input_tokens_1
#         self.input_ids_1 = input_ids_1
#         self.position_idx_1 = position_idx_1
#         self.dfg_to_code_1 = dfg_to_code_1
#         self.dfg_to_dfg_1 = dfg_to_dfg_1
#         
#         # Labels
#         self.pragma_label = pragma_label
#         self.private_label = private_label
#         self.reduction_label = reduction_label
#         
#         # Additional features from dynamic and memory analysis.
#         self.dynamic_features = dynamic_features  # e.g., a fixed-length vector (list of numbers)
#         self.memory_features = memory_features

import numpy as np

def parse_dynamic(dynamic_text):
    """
    Parse dynamic.txt and return a 5-length feature vector:
      0) avg_branch_freq: average frequency of branch entries.
      1) std_branch_freq: standard deviation of branch frequencies. (delete)
      2) avg_instr: average instruction count per basic block.
      3) avg_load: average load count per basic block.
      4) avg_store: average store count per basic block.
      total 
    """
    branch_freqs = []
    bb_instr_counts = []
    bb_load_counts = []
    bb_store_counts = []
    
    lines = dynamic_text.splitlines()
    current_block_instr = None
    current_block_load = None
    current_block_store = None
    
    in_branch_section = False
    in_data_access_section = False
    
    for line in lines:
        line = line.strip()
        if line.startswith("--- Branch Counts ---"):
            in_branch_section = True
            in_data_access_section = False
            continue
        if line.startswith("--- Data Access Count ---"):
            in_branch_section = False
            in_data_access_section = True
            continue
        if line.startswith("==="):
            in_branch_section = False
            in_data_access_section = False
            continue
        
        # Get frequency from the Branch Counts section
        if in_branch_section and "Frequency =" in line:
            try:
                freq = float(line.split("Frequency =")[1].split()[0])
                branch_freqs.append(freq)
            except Exception:
                pass
        
        # Get basic block information from the Data Access Count section
        if in_data_access_section:
            if line.startswith("BasicBlock"):
                if current_block_instr is not None:
                    bb_instr_counts.append(current_block_instr)
                    bb_load_counts.append(current_block_load)
                    bb_store_counts.append(current_block_store)
                current_block_instr = None
                current_block_load = None
                current_block_store = None
            elif line.startswith("Instr count:"):
                try:
                    parts = line.split("=")[-1].split()
                    current_block_instr = float(parts[0])
                except Exception:
                    current_block_instr = 0.0
            elif line.startswith("Load count:"):
                try:
                    parts = line.split("=")[-1].split()
                    current_block_load = float(parts[0])
                except Exception:
                    current_block_load = 0.0
            elif line.startswith("Store count:"):
                try:
                    parts = line.split("=")[-1].split()
                    current_block_store = float(parts[0])
                except Exception:
                    current_block_store = 0.0
                    
    if in_data_access_section and current_block_instr is not None:
        bb_instr_counts.append(current_block_instr)
        bb_load_counts.append(current_block_load)
        bb_store_counts.append(current_block_store)
    
    if branch_freqs:
        avg_branch_freq = float(np.mean(branch_freqs))
        std_branch_freq = float(np.std(branch_freqs))
    else:
        avg_branch_freq = 0.0
        std_branch_freq = 0.0
    
    num_blocks = len(bb_instr_counts)
    if num_blocks > 0:
        avg_instr = float(np.mean(bb_instr_counts))
        avg_load = float(np.mean(bb_load_counts))
        avg_store = float(np.mean(bb_store_counts))
    else:
        avg_instr = 0.0
        avg_load = 0.0
        avg_store = 0.0
    
    return [avg_branch_freq, std_branch_freq, avg_instr, avg_load, avg_store]


def parse_memory(memory_text):
    """
    Return a 2-length vector:
      0) mean_access: average memory access count.
      1) max_access: maximum memory access count.
    """
    if not memory_text:
        return [0.0, 0.0]
    lines = memory_text.splitlines()
    access_counts = []
    for line in lines:
        parts = line.split(',')
        if len(parts) >= 2:
            try:
                count = float(parts[1].strip())
                access_counts.append(count)
            except Exception:
                pass
    if len(access_counts) == 0:
        return [0.0, 0.0]
    mean_access = float(sum(access_counts) / len(access_counts))
    max_access = float(max(access_counts))
    return [mean_access, max_access]



class OMPifyDataset(Dataset):
    def __init__(self, json_path, tokenizer, ompfy):
        """
        json_path: Path to the dataset JSON file.
        tokenizer: The tokenizer used (e.g., RobertaTokenizer).
        ompfy: An initialized OMPify model (or an object with a convert_code method).
        """
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        self.samples = list(self.data.values())
        self.tokenizer = tokenizer
        self.ompfy = ompfy

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        code_path = sample["code"]
        # Load the code
        with open(code_path, 'r', errors='ignore') as f:
            code = f.read()
        
        # Load dynamic analysis info (if exists)
        dynamic_path = sample.get("dynamic_analysis", "")
        if dynamic_path and os.path.exists(dynamic_path):
            with open(dynamic_path, 'r', errors='ignore') as f:
                dynamic_text = f.read()
        else:
            dynamic_text = ""
        
        # Load memory access count info (if exists)
        memory_path = sample.get("memory_access_count", "")
        if memory_path and os.path.exists(memory_path):
            with open(memory_path, 'r', errors='ignore') as f:
                memory_text = f.read()
        else:
            memory_text = ""
        
        # Get the main code features using convert_code.
        (input_ids, position_idx, attn_mask,
         pragma_label, private_label, reduction_label) = self.ompfy.convert_code(code)
        
        # Parse the dynamic and memory files into feature vectors.
        dyn_features = torch.tensor(parse_dynamic(dynamic_text), dtype=torch.float)
        mem_features = torch.tensor(parse_memory(memory_text), dtype=torch.float)
        
        # Create the target tensor using your labels (defaulting to 0 if missing).
        target = torch.tensor([
            sample.get("exist", 0),
            sample.get("private", 0),
            sample.get("reduction", 0)
        ], dtype=torch.float)
        
        # You may choose to integrate the dynamic and memory features into the InputFeatures
        # For now, we return them as additional fields in the features dictionary.
        features = {
            "input_ids": input_ids,
            "position_idx": position_idx,
            "attn_mask": attn_mask,
            "dynamic_features": dyn_features,
            "memory_features": mem_features
        }
        return features, target

def group_split_dataset(dataset, train_ratio=0.8):
    """
    Splits the dataset into training and validation subsets such that all samples 
    from the same folder (i.e., having the same folder base) go into the same split.
    
    We assume that the folder name is in the file path (sample["code"]), and that the
    folder names have a trailing numeric suffix (e.g. 'kernelA_0', 'kernelA_1'). 
    This function groups samples by the common prefix (e.g., 'kernelA') and then splits
    the groups randomly according to train_ratio.
    
    Returns:
        (train_indices, val_indices): A tuple of lists of sample indices for training and validation.
    """
    groups = {}
    for i, sample in enumerate(dataset.samples):
        folder_full = os.path.basename(os.path.dirname(sample["code"]))
        group = folder_full.rsplit('_', 1)[0]  # Remove trailing numeric suffix.
        if group not in groups:
            groups[group] = []
        groups[group].append(i)
    
    group_keys = list(groups.keys())
    import random
    random.shuffle(group_keys)
    
    num_train_groups = int(train_ratio * len(group_keys))
    train_groups = group_keys[:num_train_groups]
    val_groups = group_keys[num_train_groups:]
    
    train_indices = []
    for key in train_groups:
        train_indices.extend(groups[key])
        
    val_indices = []
    for key in val_groups:
        val_indices.extend(groups[key])
    
    return train_indices, val_indices

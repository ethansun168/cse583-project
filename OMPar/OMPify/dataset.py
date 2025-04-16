import json
import os
import torch
from .model import OMPify
from torch.utils.data import Dataset, random_split

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
        
        # 取 Branch Counts 中的頻率
        if in_branch_section and "Frequency =" in line:
            try:
                freq = float(line.split("Frequency =")[1].split()[0])
                branch_freqs.append(freq)
            except Exception:
                pass
        
        # 取 Data Access Count 中的基本區塊資訊
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

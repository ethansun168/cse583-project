import json
import os
import torch
from .model import OMPify
from torch.utils.data import Dataset, random_split
import numpy as np
import re

import re

def parse_static(static_text: str):
    """
    return [ total_instr_cnt, total_load+store_cnt, total_branch_cnt ]
    """
    instr_total  = 0
    load_total   = 0
    store_total  = 0
    branch_total = 0

    # Branches
    regex = re.compile(
        r"NumInstructions:\s*(\d+).*?"
        r"-\s*Loads:\s*(\d+).*?"
        r"-\s*Stores:\s*(\d+).*?"
        r"-\s*Branches:\s*(\d+)",
        re.S
    )

    for m in regex.finditer(static_text):
        instr_total  += int(m.group(1))
        load_total   += int(m.group(2))
        store_total  += int(m.group(3))
        branch_total += int(m.group(4))

    return [
        float(instr_total),
        float(load_total + store_total),
        float(branch_total)
    ]


def parse_dynamic(dynamic_text):
    """
    Parse dynamic.txt and return a 3-length feature vector:
      0) avg_branch_freq: average frequency of branch entries.
      1) avg_instr: average instruction count per basic block.
      2) avg_data_access: average data-access count per basic block (avg_load + avg_store).
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

        # Branch frequencies
        if in_branch_section and "Frequency =" in line:
            try:
                freq = float(line.split("Frequency =")[1].split()[0])
                branch_freqs.append(freq)
            except Exception:
                pass

        # Basic-block data-access info
        if in_data_access_section:
            if line.startswith("BasicBlock"):
                # finish previous block
                if current_block_instr is not None:
                    bb_instr_counts.append(current_block_instr)
                    bb_load_counts.append(current_block_load)
                    bb_store_counts.append(current_block_store)
                current_block_instr = None
                current_block_load = None
                current_block_store = None
            elif line.startswith("Instr count:"):
                try:
                    current_block_instr = float(line.split("=", 1)[1].split()[0])
                except Exception:
                    current_block_instr = 0.0
            elif line.startswith("Load count:"):
                try:
                    current_block_load = float(line.split("=", 1)[1].split()[0])
                except Exception:
                    current_block_load = 0.0
            elif line.startswith("Store count:"):
                try:
                    current_block_store = float(line.split("=", 1)[1].split()[0])
                except Exception:
                    current_block_store = 0.0

    # append last block if any
    if in_data_access_section and current_block_instr is not None:
        bb_instr_counts.append(current_block_instr)
        bb_load_counts.append(current_block_load)
        bb_store_counts.append(current_block_store)

    # compute averages
    avg_branch_freq = float(np.mean(branch_freqs)) if branch_freqs else 0.0
    num_blocks = len(bb_instr_counts)
    if num_blocks > 0:
        avg_instr = float(np.mean(bb_instr_counts))
        avg_load = float(np.mean(bb_load_counts))
        avg_store = float(np.mean(bb_store_counts))
        avg_data_access = avg_load + avg_store
    else:
        avg_instr = 0.0
        avg_data_access = 0.0

    return [avg_branch_freq, avg_instr, avg_data_access]



def parse_memory(memory_text):
    
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

        static_path = sample.get("static_analysis", "")
        static_text = open(static_path, 'r', errors='ignore').read() if static_path and os.path.exists(static_path) else ""
        static_features = parse_static(static_text)    
        
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

        # combine
        static_list = parse_static(static_text) 
        dyn_list    = parse_dynamic(dynamic_text) 
        mem_list    = parse_memory(memory_text) 

        feat_list = static_list + dyn_list  
        numeric_feats  = torch.tensor(feat_list, dtype=torch.float)
        mem_feats      = torch.tensor(mem_list, dtype=torch.float)    
        
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
            "dynamic_features": numeric_feats,
            "memory_features": mem_feats
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

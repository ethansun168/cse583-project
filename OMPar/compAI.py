
import torch
import argparse
import numpy as np
from OMPify.model import OMPify
from transformers import GPTNeoXForCausalLM, GPT2Tokenizer


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

    if in_data_access_section and current_block_instr is not None:
        bb_instr_counts.append(current_block_instr)
        bb_load_counts.append(current_block_load)
        bb_store_counts.append(current_block_store)

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


def load_dynamic_feats(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return parse_dynamic(text)


def load_memory_feats(path, K: int = None):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return parse_memory(text)


class OMPAR:

    def __init__(self, model_path, device, args):
        self.device = device
        self.model_cls = OMPify(model_path, device)

        self.tokenizer_gen = GPT2Tokenizer(vocab_file=args.vocab_file,
                                          merges_file=args.merge_file,
                                          model_input_names=['input_ids'])
        self.model_gen = GPTNeoXForCausalLM.from_pretrained('MonoCoder/MonoCoder_OMP').to(device)
        self.model_gen.eval()

    def cls_par(self, loop, dynamic_feats=None, memory_feats=None) -> bool:
        """
        Return True if a parallel pragma should be inserted.
        """
        # Convert code-only inputs
        inputs_ids, position_idx, attn_mask, _, _, _ = self.model_cls.convert_code(loop)
        # print(f"inputs_ids: {inputs_ids}, position_idx: {position_idx}, attn_mask: {attn_mask}")
        inputs_ids = inputs_ids.unsqueeze(0).to(self.device)
        position_idx = position_idx.unsqueeze(0).to(self.device)
        attn_mask = attn_mask.unsqueeze(0).to(self.device)

        # Prepare dynamic and memory tensors
        if dynamic_feats is not None:
            dyn = torch.tensor(dynamic_feats, dtype=torch.float, device=self.device).unsqueeze(0)
        else:
            dyn = None
        if memory_feats is not None:
            mem = torch.tensor(memory_feats, dtype=torch.float, device=self.device).unsqueeze(0)
        else:
            mem = None

        # Get probability from classifier
        prob = self.model_cls.model(inputs_ids, position_idx, attn_mask,
                                    dynamic_feats=dyn, memory_feats=mem)
        pred = prob > 0.5
        pragma_pred = pred.squeeze()[0].cpu().item()
        return bool(pragma_pred)

    def pragma_format(self, pragma):
        clauses = pragma.split('||')
        private_vars = None
        reduction_op, reduction_vars = None, None

        for clause in clauses:
            cl = clause.strip()
            if private_vars is None and cl.startswith('private'):
                private_vars = cl[len('private'):].split()
            if reduction_vars is None and cl.startswith('reduction'):
                parts = cl[len('reduction'):].split(':')
                if len(parts) >= 2:
                    reduction_op = parts[0]
                    reduction_vars = parts[1].split()

        pragma_str = 'omp parallel for'
        if private_vars:
            pragma_str += f" private({', '.join(private_vars)})"
        if reduction_vars:
            pragma_str += f" reduction({reduction_op}:{', '.join(reduction_vars)})"
        return pragma_str

    def gen_par(self, loop) -> str:
        inputs = self.tokenizer_gen(loop, return_tensors="pt").to(self.device)
        outputs = self.model_gen.generate(inputs['input_ids'], max_length=256)
        gen = self.tokenizer_gen.decode(outputs[0], skip_special_tokens=True)
        return gen[len(loop):]

    def auto_comp(self, loop, dynamic_feats=None, memory_feats=None) -> str or None:
        if self.cls_par(loop, dynamic_feats=dynamic_feats, memory_feats=memory_feats):
            return self.pragma_format(self.gen_par(loop))
        return None

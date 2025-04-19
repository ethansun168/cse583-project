
import argparse
import json
import torch
from compAI import OMPAR, load_dynamic_feats, load_memory_feats

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.register('type', 'bool', lambda v: v.lower() in ['yes', 'true', 't', '1', 'y'])

    parser.add_argument('--vocab_file', default='tokenizer/gpt/gpt_vocab/gpt2-vocab.json')
    parser.add_argument('--merge_file', default='tokenizer/gpt/gpt_vocab/gpt2-merges.txt')
    # parser.add_argument('--model_weights', help='Path to the OMPify model weights', required=True)
    parser.add_argument('--source_file', type=str, default=None,
                        help='Optional path to a .c or .cpp file you want to analyze.')
    parser.add_argument('--dynamic_file', type=str, default=None,
                        help='Path to a dynamic features file (e.g., extracted_dynamic.txt)')
    parser.add_argument('--memory_file', type=str, default=None,
                        help='Path to a memory features file (e.g., memory_access_count.txt)')

    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    weight_path = 'OMPify'

    ompar = OMPAR(model_path=weight_path, device=device, args=args)

    def run_instance(code, dyn_file=None, mem_file=None):
        # Load dynamic and memory features if available
        dyn_feats = load_dynamic_feats(dyn_file) if dyn_file else None
        mem_feats = load_memory_feats(mem_file) if mem_file else None
        pred = ompar.auto_comp(code, dynamic_feats=dyn_feats, memory_feats=mem_feats)
        return pred

    if args.source_file:
        with open(args.source_file, 'r') as f:
            code = f.read()
        pred = run_instance(code, args.dynamic_file, args.memory_file)
        print(f'Code:\n{code}')
        print(f"Pred pragma: {'' if not pred else '#pragma '+pred}")
    else:
        with open('use_cases.jsonl', 'r') as f:
            for line in f:
                sample = json.loads(line.strip())
                code = sample['code']
                dyn_file = sample.get('dynamic_file')
                mem_file = sample.get('memory_file')
                pred = run_instance(code, dyn_file, mem_file)
                print(f'Code:\n{code}')
                print(f"GT pragma: {sample.get('pragma')}")
                print(f"Pred pragma: {'' if not pred else '#pragma '+pred}")
                print('-'*20)
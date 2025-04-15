import torch
import argparse
from OMPify.model import OMPify
from transformers import GPTNeoXForCausalLM, GPT2Tokenizer


class OMPAR:

    def __init__(self, model_path, device, args):
        self.device = device
        self.model_cls = OMPify(model_path, device)

        self.tokenizer_gen = GPT2Tokenizer(vocab_file=args.vocab_file, merges_file=args.merge_file, model_input_names=['input_ids'])
        self.model_gen = GPTNeoXForCausalLM.from_pretrained('MonoCoder/MonoCoder_OMP').to(device)
        self.model_gen.eval()

    def cls_par(self, loop) -> bool:
        """
        Return if a parallelization is aplicable/neccessary
        """
        pragma_cls, _, _ = self.model_cls.predict(loop)
        return pragma_cls
    
    def pragma_format(self, pragma):
        clauses = pragma.split('||')        
        private_vars = None
        reduction_op, reduction_vars = None, None

        for clause in clauses:
            cl = clause.strip()

            if private_vars is None and cl.startswith('private'):
                private_vars = cl[len('private'):].split()
                
            if reduction_vars is None and cl.startswith('reduction'):
                reduction = cl[len('reduction'):].split(':')
                
                if len(reduction) >=2:
                    reduction_op = reduction[0]
                    reduction_vars = reduction[1].split()

        pragma = 'omp parallel for'
        if private_vars is not None and len(private_vars) > 0:
            pragma += f" private({', '.join(private_vars)})"
        if reduction_vars is not None and len(reduction_vars) > 0:
            pragma += f" reduction({reduction_op}:{', '.join(reduction_vars)})"

        return pragma        

    def gen_par(self, loop) -> str:
        """
        Generate OMP pragma
        """
        inputs = self.tokenizer_gen(loop, return_tensors="pt").to(self.device)

        # outputs = self.model_gen.generate(inputs["input_ids"], max_length=64)
        outputs = self.model_gen.generate(inputs["input_ids"], max_length=256)
        generated_pragma = self.tokenizer_gen.decode(outputs[0], skip_special_tokens=True)

        return generated_pragma[len(loop):]


    def auto_comp(self, loop) -> str or None:
        """
        Return an omp pragma if neccessary
        """
        if self.cls_par(loop):
            return self.pragma_format(self.gen_par(loop))

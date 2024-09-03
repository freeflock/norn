import torch
from ratatosk_errands.model import ChatInstructions
from transformers import AutoTokenizer, LlamaForCausalLM, BitsAndBytesConfig


class Hermes3Chat:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "NousResearch/Hermes-3-Llama-3.1-70B",
            trust_remote_code=True)
        self.model = LlamaForCausalLM.from_pretrained(
            "NousResearch/Hermes-3-Llama-3.1-70B",
            torch_dtype=torch.float16,
            device_map="auto",
            quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16),
            attn_implementation="flash_attention_2"
        )

    def chat(self, instructions: ChatInstructions) -> str:
        system_instructions = "" if instructions.system_instructions is None else instructions.system_instructions
        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": instructions.prompt}
        ]
        input_ids = self.tokenizer.apply_chat_template(messages, return_tensors="pt").to("cuda")
        generated_ids = self.model.generate(
            input_ids,
            max_new_tokens=750 if instructions.max_new_tokens is None else instructions.max_new_tokens,
            temperature=0.8 if instructions.temperature is None else instructions.temperature,
            do_sample=True,
            repetition_penalty=1.1 if instructions.repetition_penalty is None else instructions.repetition_penalty,
            eos_token_id=self.tokenizer.eos_token_id)
        response = self.tokenizer.decode(
            generated_ids[0][input_ids.shape[-1]:],
            skip_special_tokens=True,
            clean_up_tokenization_space=True)
        return response

import torch
from ratatosk_errands.model import ChatInstructions
from transformers import AutoTokenizer, LlamaForCausalLM, BitsAndBytesConfig


class Hermes3Chat:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "NousResearch/Hermes-3-Llama-3.1-8B",
            trust_remote_code=True)
        self.model = LlamaForCausalLM.from_pretrained(
            "NousResearch/Hermes-3-Llama-3.1-8B",
            torch_dtype=torch.float16,
            device_map="auto",
            quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16),
            attn_implementation="flash_attention_2"
        )

    def chat(self, instructions: ChatInstructions) -> str:
        messages = [
            {"role": "system", "content": instructions.system_instructions},
            {"role": "user", "content": instructions.prompt}
        ]
        input_ids = self.tokenizer.apply_chat_template(messages, return_tensors="pt").to("cuda")
        generated_ids = self.model.generate(
            input_ids,
            max_new_tokens=instructions.max_new_tokens,
            temperature=instructions.temperature,
            do_sample=True,
            repetition_penalty=instructions.repetition_penalty,
            eos_token_id=self.tokenizer.eos_token_id)
        response = self.tokenizer.decode(
            generated_ids[0][input_ids.shape[-1]:],
            skip_special_tokens=True,
            clean_up_tokenization_space=True)
        return response

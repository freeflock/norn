import torch
from ratatosk_errands.model import ChatInstructions
from transformers import AutoTokenizer, BitsAndBytesConfig, LlamaForCausalLM


class Hermes3Chat:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "NousResearch/Hermes-3-Llama-3.1-70B",
            trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"
        quantization = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True)
        self.model = LlamaForCausalLM.from_pretrained(
            "NousResearch/Hermes-3-Llama-3.1-70B",
            torch_dtype=torch.float16,
            return_dict=True,
            device_map="auto",
            quantization_config=quantization,
            attn_implementation="flash_attention_2"
        )

    def chat(self, instructions: ChatInstructions) -> str:
        inputs = self.tokenizer(instructions.prompt, return_tensors="pt").input_ids
        tokens = self.model.generate(
            inputs.to("cuda"),
            max_new_tokens=1500 if instructions.max_new_tokens is None else instructions.max_new_tokens,
            temperature=0.8 if instructions.temperature is None else instructions.temperature,
            do_sample=True,
            repetition_penalty=1.1 if instructions.repetition_penalty is None else instructions.repetition_penalty,
            eos_token_id=self.tokenizer.eos_token_id
        )
        response = self.tokenizer.decode(
            tokens[0][inputs.shape[-1]:],
            skip_special_tokens=True,
            clean_up_tokenization_space=True)
        return response


class ReflectionChat:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("mattshumer/Reflection-Llama-3.1-70B")
        quantization = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True)
        self.model = LlamaForCausalLM.from_pretrained(
            "mattshumer/Reflection-Llama-3.1-70B",
            torch_dtype=torch.float16,
            return_dict=True,
            device_map="auto",
            quantization_config=quantization
        )

    def chat(self, instructions: ChatInstructions) -> str:
        inputs = self.tokenizer(instructions.prompt, return_tensors="pt").input_ids
        tokens = self.model.generate(
            inputs.to("cuda"),
            max_new_tokens=1500 if instructions.max_new_tokens is None else instructions.max_new_tokens,
            temperature=0.7 if instructions.temperature is None else instructions.temperature,
            do_sample=True
        )
        response = self.tokenizer.decode(
            tokens[0][inputs.shape[-1]:],
            skip_special_tokens=True,
            clean_up_tokenization_space=True)
        return response

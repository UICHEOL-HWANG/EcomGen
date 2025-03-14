from transformers import AutoTokenizer, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("./kanana_lora_finetuned/checkpoint-1000")
tokenizer  = AutoTokenizer.from_pretrained("kakaocorp/kanana-nano-2.1b-instruct")

if __name__ == "__main__":
    model.save_pretrained("./save_kanana")
    tokenizer.save_pretrained("./save_kanana")
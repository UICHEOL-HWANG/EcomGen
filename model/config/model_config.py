from unsloth import FastModel
from unsloth.chat_templates import get_chat_template

def load_model(model_name: str, chat_template: str, use_4bit: bool = True):
    model, tokenizer = FastModel.from_pretrained(
        model_name=model_name,
        max_seq_length=2048,
        load_in_4bit=use_4bit,
        load_in_8bit=not use_4bit,
        full_finetuning=False,
    )
    model = FastModel.get_peft_model(
        model,
        finetune_vision_layers=False,
        finetune_language_layers=True,
        finetune_attention_modules=True,
        finetune_mlp_modules=True,
        r=8, lora_alpha=8, lora_dropout=0, bias="none", random_state=3407,
    )
    tokenizer = get_chat_template(tokenizer, chat_template)
    return model, tokenizer
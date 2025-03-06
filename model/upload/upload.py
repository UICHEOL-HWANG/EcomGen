from transformers import AutoTokenizer, AutoModelForCausalLM

def upload_to_model(upload_path, model_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)

    model.push_to_hub(upload_path)
    tokenizer.push_to_hub(upload_path)


if __name__ == "__main__":
    upload_to_model("UICHEOL-HWANG/EcomGen-0.0.1v", "../Polyglot-ko-1.3b/merged_polyglot")


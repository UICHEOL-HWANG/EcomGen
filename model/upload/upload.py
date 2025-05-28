from transformers import AutoTokenizer, AutoModelForCausalLM
import argparse

def upload_to_model(upload_path, model_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)

    model.push_to_hub(upload_path)
    tokenizer.push_to_hub(upload_path)


def parse_arguments():
    parser = argparse.ArgumentParser(description='모델이 너무 많아서 이렇게 올릴랭')
    
    parser.add_argument('--upload_path', type=str, required=True,
                        help='허브에 업로드할 경로')
    parser.add_argument('--model_path', type=str, required=True,
                        help='업로드할 로컬 모델의 경로')
    
    return parser.parse_args()
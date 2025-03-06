import pandas as pd
import random
import torch
from transformers import AutoTokenizer
from torch.utils.data import Dataset, DataLoader

# ✅ CustomDataset 클래스 정의
class CustomDataset(Dataset):
    def __init__(self, file_path, tokenizer, max_length=512):
        self.data = pd.read_csv(file_path, encoding="utf-8-sig")
        self.eos_token = tokenizer.eos_token
        self.tokenizer = tokenizer.padding_side = 'left'
        self.tokenizer = tokenizer
        self.max_length = max_length


    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        example = self.data.iloc[idx]

        instruction_templates = [
            "주어진 상품명을 기반으로 설명을 작성하세요.",
            "다음 상품에 대한 설명을 작성하세요.",
            "다음과 같은 상품의 특장점을 설명해주세요.",
            "주어진 상품명과 연관된 상세 설명을 생성하세요."
        ]
        instruction = random.choice(instruction_templates)

        prompt = f"{instruction}\n상품명: {example['name']}\n상품 설명: {self.eos_token}"
        response = example["words"]

        encodings = self.tokenizer(
            prompt + response,  # 모델이 정답을 예측할 수 있도록 Response까지 포함
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )

        input_ids = encodings["input_ids"].squeeze()
        attention_mask = encodings["attention_mask"].squeeze()
        labels = input_ids.clone()
        labels[labels == self.tokenizer.pad_token_id] = -100  # 패딩 제외

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }
import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer


class CustomDataset(Dataset):
    def __init__(self, file_path, tokenizer, max_length=512):
        """
        Gemma-2B-IT 전용 데이터셋 (검색 결과 [3][6] 반영)
        - 동적 길이 조정
        - 라벨 마스킹 최적화
        """
        # 데이터 로드 및 전처리
        raw_data = pd.read_csv(file_path, encoding="utf-8-sig")
        raw_data = raw_data.dropna().sample(frac=1.0)  # 결측치 제거 + 셔플링 [4]

        # ✅ Gemma 채팅 템플릿 구조 [6]
        self.samples = []
        for _, row in raw_data.iterrows():
            self.samples.append({
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "다음 상품명을 기반으로 고객이 관심을 가질 만한 "
                            f"매력적인 제품 설명을 작성하세요:\n상품명: {row['name']}"
                        )
                    },
                    {"role": "model", "content": row['words']}
                ]
            })

        # 토크나이저 설정
        self.tokenizer = tokenizer
        self.tokenizer.padding_side = "right"  # 필수 [6]
        self.max_length = max_length

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        example = self.samples[idx]

        # ✅ 채팅 템플릿 적용 (검색 결과 [6] 방식)
        encodings = self.tokenizer.apply_chat_template(
            example["messages"],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
            add_generation_prompt=True
        )

        # ✅ 동적 라벨 마스킹 (검색 결과 [4] 방식)
        labels = encodings.clone()
        prompt_len = len(self.tokenizer.apply_chat_template(
            example["messages"][:1],  # user 메시지만 포함
            return_tensors="pt"
        ))
        labels[:, :prompt_len] = -100  # 사용자 입력 부분 무시

        return {
            "input_ids": encodings.squeeze(),
            "attention_mask": (encodings != self.tokenizer.pad_token_id).squeeze(),
            "labels": labels.squeeze()
        }

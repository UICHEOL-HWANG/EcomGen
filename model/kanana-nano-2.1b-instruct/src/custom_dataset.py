from transformers import AutoTokenizer
from datasets import Dataset
import pandas as pd
from typing import List, Dict, Any


class DatasetPreprocessor:
    def __init__(self,
                 model_name: str,
                 system_prompt: str = None,
                 instruction: str = None,
                 max_length: int = 512):
        """
        Dataset Preprocessor for Chat-based Fine-tuning

        Args:
            model_name (str): 사전학습된 모델 이름
            system_prompt (str): 시스템 프롬프트
            instruction (str): 사용자 프롬프트 (질문 역할)
            max_length (int): 최대 길이 (default: 512)
        """
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            padding_side='left',
            trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token  # padding token 설정
        self.system_prompt = system_prompt or "당신은 상품명을 바탕으로 상세하고 매력적인 상품 설명을 생성하는 AI입니다."
        self.instruction = instruction or "주어진 상품명을 기반으로 매력적인 상품설명을 작성하세요."
        self.max_length = max_length

    def _format_and_tokenize(self, example: Dict[str, str]) -> Dict[str, Any]:
        """
        메시지 포맷 구성 및 토크나이징
        Args:
            example (dict): {'input': 상품명, 'output': 상품설명}
        Returns:
            dict: {'input_ids': tensor, 'labels': tensor}
        """
        # 메시지 구성
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"{self.instruction}\n상품명: {example['input']}"},
            {"role": "assistant", "content": example['output']}
        ]

        # 토크나이징
        tokenized = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=False,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=self.max_length
        )[0]



        return {
            "input_ids": tokenized,
            "labels": tokenized.clone()  # labels 동일하게 복사
        }

    def load_dataset_from_csv(self, csv_path: str) -> Dataset:
        """
        CSV 파일에서 데이터셋 로드 및 컬럼 통일
        Args:
            csv_path (str): CSV 파일 경로
        Returns:
            Dataset: HF Dataset 객체
        """
        df = pd.read_csv(csv_path)
        df = df.rename(columns={"name": "input", "words": "output"})  # 이름 매핑
        dataset = Dataset.from_pandas(df)
        return dataset

    def preprocess_dataset(self, dataset: Dataset, remove_columns: List[str] = None) -> Dataset:
        """
        데이터셋 전처리 (메시지 포맷 + 토크나이징)
        Args:
            dataset (Dataset): HF Dataset 객체
            remove_columns (list): 제거할 컬럼명 리스트 (예: ['input', 'output', 'no', 'image'])
        Returns:
            Dataset: 전처리된 Dataset
        """
        dataset = dataset.map(self._format_and_tokenize, batched=False)

        if remove_columns:
            dataset = dataset.remove_columns(remove_columns)

        return dataset

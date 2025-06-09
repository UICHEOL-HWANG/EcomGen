import pandas as pd
from datasets import Dataset

class DataLoader:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)

    def to_chat_dataset(self):
        def format(row):
            instruction = f"""다음 상품에 대한 매력적인 설명을 작성해주세요.
            상품명: {row['name_cleaned']}
            카테고리: {row['main_category_name']} > {row['sub_category_name']}
            가격: {row['price']:,}원
            핵심 키워드: {row['top_keywords']}
            작성 톤: {row['tone']} ({row['tone_description']})
            위 정보를 바탕으로 고객에게 매력적인 상품 설명을 작성해주세요.
            """
            return {
                "conversations": [
                    {"role": "user", "content": instruction},
                    {"role": "assistant", "content": row["generated_description"]}
                ]
            }

        chat_data = [format(row) for _, row in self.df.iterrows()]
        return Dataset.from_list(chat_data)

    def apply_template(self, dataset, tokenizer):
        def apply(examples):
            texts = []
            for conv in examples["conversations"]:
                text = tokenizer.apply_chat_template(
                    conv, tokenize=False, add_generation_prompt=False
                ).removeprefix("<bos>")
                texts.append(text)
            return {"text": texts}

        return dataset.map(apply, batched=True, remove_columns=["conversations"])
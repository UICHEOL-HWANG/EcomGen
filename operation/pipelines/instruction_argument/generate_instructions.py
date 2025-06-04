from cleansing.category_piepelines import TONE_MAPPING, TONE_DESCRIPTIONS
import pandas as pd


class InstructionGenerator:
    def __init__(self):
        self.tone_mapping = TONE_MAPPING
        self.tone_descriptions = TONE_DESCRIPTIONS

    def get_suitable_tones(self, main_category, sub_category):
        if main_category in self.tone_mapping:
            category_mapping = self.tone_mapping[main_category]
            if sub_category in category_mapping:
                return category_mapping[sub_category]
            elif "default" in category_mapping:
                return category_mapping["default"]
        return ["따뜻하고_신뢰감있는", "담백하고_직관적인"]

    def create_instruction_with_tone(self, row, tone):
        if pd.isna(row['top_keywords']) or row['top_keywords'] == '':
            keywords = [row['name_cleaned'][:10]]
        else:
            keywords = [k.strip() for k in str(row['top_keywords']).split(',')[:5]]
        keywords_str = ", ".join(keywords)
        tone_name = tone.replace("_", " ")
        tone_desc = self.tone_descriptions[tone]
        instruction = (
            f"다음 키워드를 포함하여 고객에게 매력적인 상품 설명을 작성하세요. "
            f"톤은 '{tone_name}'로 ({tone_desc}): {keywords_str}"
        )
        return instruction

    def augment_dataset_with_tones(self, df):
        augmented_data = []
        for idx, row in df.iterrows():
            main_cat = row['main_category_name']
            sub_cat = row['sub_category_name']
            suitable_tones = self.get_suitable_tones(main_cat, sub_cat)
            for tone in suitable_tones:
                augmented_item = {
                    "original_id": idx,
                    "name_cleaned": row['name_cleaned'],
                    "main_category_name": main_cat,
                    "sub_category_name": sub_cat,
                    "price": row['price'],
                    "top_keywords": row['top_keywords'],
                    "tone": tone,
                    "tone_description": self.tone_descriptions[tone],
                    "instruction": self.create_instruction_with_tone(row, tone),
                }
                augmented_data.append(augmented_item)
        return augmented_data


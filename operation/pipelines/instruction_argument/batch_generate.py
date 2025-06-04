import json
import openai


class BatchGenerator:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-4.1-nano-2025-04-14"

    def create_batch(self, json_file: str) -> str:
        """JSON 파일로 배치 생성하고 batch_id 반환"""
        # 1. 데이터 로드
        with open(json_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        print(f"Loaded {len(products)} products")

        # 2. 배치 요청 생성
        requests = []
        for i, product in enumerate(products):  # enumerate로 고유 인덱스 사용
            keywords = product.get('top_keywords', '')
            if isinstance(keywords, list):
                keywords = ', '.join(keywords)

            input_text = f"상품명: {product['name_cleaned']}, 카테고리: {product['main_category_name']} > {product['sub_category_name']}, 가격: {product['price']}원, 키워드: {keywords}"
            instruction = f"다음 상품에 대해 '{product['tone']}' 톤으로 매력적인 상품 설명을 작성하세요. 톤 설명: {product['tone_description']}"

            request = {
                "custom_id": f"product_{i}",  # enumerate 인덱스 사용 (항상 고유)
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": instruction},
                        {"role": "user", "content": input_text}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            }
            requests.append(request)

        # 3. JSONL 파일 저장
        with open("batch_requests.jsonl", 'w', encoding='utf-8') as f:
            for req in requests:
                f.write(json.dumps(req, ensure_ascii=False) + '\n')

        # 4. 파일 업로드
        with open("batch_requests.jsonl", 'rb') as f:
            file_response = self.client.files.create(file=f, purpose='batch')

        # 5. 배치 생성
        batch = self.client.batches.create(
            input_file_id=file_response.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )

        print(f"Batch created: {batch.id}")
        return batch.id

    def check_status(self, batch_id: str) -> str:
        """배치 상태 확인"""
        batch = self.client.batches.retrieve(batch_id)
        return batch.status

    def download_results(self, batch_id: str) -> str:
        """결과 다운로드 (완료된 경우만)"""
        batch = self.client.batches.retrieve(batch_id)

        if batch.status != "completed":
            print(f"Not completed. Status: {batch.status}")
            return None

        # 결과 다운로드
        result_content = self.client.files.content(batch.output_file_id)

        with open("results.jsonl", "wb") as f:
            f.write(result_content.content)

        print("Results saved to results.jsonl")
        return "results.jsonl"

    def create_training_data(self, original_json: str, results_file: str = "results.jsonl"):
        """원본 데이터와 결과를 합쳐서 학습용 데이터 생성"""
        # 1. 원본 데이터 로드
        with open(original_json, 'r', encoding='utf-8') as f:
            original_data = json.load(f)

        # 2. 결과 파싱
        results = {}
        with open(results_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    result = json.loads(line)
                    if result.get('response') and result['response'].get('body'):
                        product_id = result['custom_id'].replace('product_', '')
                        content = result['response']['body']['choices'][0]['message']['content']
                        results[product_id] = content.strip()

        # 3. 학습용 데이터 생성
        training_data = []
        for product in original_data:
            product_id = str(product['original_id'])
            if product_id in results:
                # instruction-input-output 형태
                keywords = product.get('top_keywords', '')
                if isinstance(keywords, list):
                    keywords = ', '.join(keywords)

                training_item = {
                    "instruction": f"다음 상품에 대해 '{product['tone']}' 톤으로 매력적인 상품 설명을 작성하세요. 톤 설명: {product['tone_description']}",
                    "input": f"상품명: {product['name_cleaned']}, 카테고리: {product['main_category_name']} > {product['sub_category_name']}, 가격: {product['price']}원, 키워드: {keywords}",
                    "output": results[product_id]
                }
                training_data.append(training_item)

        # 4. 저장
        with open("training_data.json", 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)

        print(f"Training data created: {len(training_data)} items -> training_data.json")
        return training_data



if __name__ == "__main__":
    main()
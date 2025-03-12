import argparse
from src.custom_dataset import DatasetPreprocessor
from src.train import Train

def main():
    parser = argparse.ArgumentParser(description="LoRA를 통한 kanana 파인튜닝")

    # 하이퍼파라미터
    parser.add_argument("--data_path", type=str, default="../data/train.csv")
    parser.add_argument("--model_name", type=str, default="kakaocorp/kanana-nano-2.1b-instruct")
    parser.add_argument("--output_dir", type=str, default="./kanana_lora_finetuned")
    parser.add_argument("--system_prompt", type=str, default="당신은 상품명을 바탕으로 상세하고 매력적인 상품 설명을 생성하는 AI입니다.")
    parser.add_argument("--instruction", type=str, default="주어진 상품명을 기반으로 매력적인 상품설명을 작성하세요.")
    parser.add_argument("--max_length", type=int, default=512)
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--grad_accum_steps", type=int, default=8)
    parser.add_argument("--num_train_epochs", type=int, default=3)
    parser.add_argument("--learning_rate", type=float, default=2e-5)
    parser.add_argument("--logging_steps", type=int, default=10)
    parser.add_argument("--save_steps", type=int, default=500)
    parser.add_argument("--lora_r", type=int, default=8)
    parser.add_argument("--lora_alpha", type=int, default=32)
    parser.add_argument("--lora_dropout", type=float, default=0.1)

    args = parser.parse_args()

    # 데이터 전처리 메인 클래스 선언
    preprocessor = DatasetPreprocessor(
        model_name=args.model_name,
        system_prompt=args.system_prompt,
        instruction=args.instruction,
        max_length=args.max_length
    )

    # 조금 하드코딩 된거 같긴한데... 일단 전처리 후에 데이터셋으로 매핑
    refined_data = preprocessor.load_dataset_from_csv(args.data_path)
    dataset = preprocessor.preprocess_dataset(refined_data)

    # 학습
    trainer = Train(
        model_name=args.model_name,
        output_dir=args.output_dir,
        train_dataset=dataset,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        batch_size=args.batch_size,
        grad_accum_steps=args.grad_accum_steps,
        num_train_epochs=args.num_train_epochs,
        learning_rate=args.learning_rate,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps
    )

    trainer.train()


if __name__ == "__main__":
    main()

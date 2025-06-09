import argparse
from config.model_config import load_model
from data.loader import DataLoader
from trl import SFTTrainer, SFTConfig
import wandb

model_map = {
    "llama": {
        "model_name": "Bllossom/llama-3.2-Korean-Bllossom-3B",
        "template": "llama-3.1"
    },
    "gemma": {
        "model_name": "unsloth/gemma-3-4b-it",
        "template": "gemma-3"
    }
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SFT Training Script")
    parser.add_argument("--model", choices=["llama", "gemma"], required=True, help="Model choice: llama or gemma")
    parser.add_argument("--csv_path", type=str, required=True, help="Path to CSV dataset")
    args = parser.parse_args()

    config = model_map[args.model]
    model, tokenizer = load_model(config["model_name"], config["template"])

    loader = DataLoader(args.csv_path)
    dataset = loader.to_chat_dataset()
    dataset = loader.apply_template(dataset, tokenizer)
    split = dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset, eval_dataset = split["train"], split["test"]

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        args=SFTConfig(
            dataset_text_field="text",
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=5,
            max_steps=30,
            learning_rate=2e-4,
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            report_to="wandb",
            dataset_num_proc=2,
        ),
    )

    wandb.init(project=f"EcomGen_{args.model}")
    trainer.train()

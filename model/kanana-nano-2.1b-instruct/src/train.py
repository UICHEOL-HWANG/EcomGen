import torch
from transformers import AutoModelForCausalLM, TrainingArguments, Trainer, AutoTokenizer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, TaskType

class Train:
    def __init__(
        self,
        model_name: str,
        train_dataset,
        output_dir: str = "./results_lora",
        r: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.1,
        batch_size: int = 4,
        grad_accum_steps: int = 16,
        num_train_epochs: int = 3,
        learning_rate: float = 2e-5,
        logging_steps: int = 10,
        save_steps: int = 200,
        save_total_limit: int = 2,
    ):
        self.model_name = model_name
        self.train_dataset = train_dataset
        self.output_dir = output_dir

        # ✅ 1. 모델 로드
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,  # bfloat16 사용
            trust_remote_code=True
        ).to("cuda" if torch.cuda.is_available() else "cpu")

        # ✅ CUDA 체크
        if torch.cuda.is_available():
            print(f"[✅] CUDA 활성화: {torch.cuda.get_device_name(0)}")
        else:
            print("[❌] CUDA 사용 불가. CPU로 진행됩니다.")
        self.lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout
        )

        self.model = get_peft_model(self.model, self.lora_config)

        self.training_args = TrainingArguments(
            output_dir=self.output_dir,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=grad_accum_steps,
            num_train_epochs=num_train_epochs,
            learning_rate=learning_rate,
            logging_steps=logging_steps,
            save_steps=save_steps,
            save_total_limit=save_total_limit,
            report_to=None,
            fp16=True if torch.cuda.is_available() else False,
            label_names=["labels"],
        )

        # ✅ 6. Trainer
        self.trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=self.train_dataset,

        )

    # ✅ 학습 시작
    def train(self):
        self.trainer.train()

    # ✅ LoRA 가중치 저장
    def save_model(self, save_path: str = None):
        save_path = save_path or self.output_dir
        self.model.save_pretrained(save_path)


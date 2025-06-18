from langchain_huggingface import HuggingFacePipeline
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import logging

logger = logging.getLogger(__name__)

class ModelInitialized:
    def __init__(
        self, 
        model_name: str = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct", 
        max_new_tokens: int = 1024, 
        temperature: float = 0.7,
        repetition_penalty: float = 1.1
    ):
        """
        모델 초기화
        """
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.repetition_penalty = repetition_penalty
        self.llm = self._load_model()
        
    def _load_model(self):
        """모델과 토크나이저를 로드합니다."""
        try:
            logger.info(f"모델 로딩 시작: {self.model_name}")
            
            # 모델 로드
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,
                trust_remote_code=True,
                device_map="auto"
            )
            
            # 토크나이저 로드
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # 파이프라인 생성 (eos_token_id를 stop으로 활용)
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                do_sample=True,
                return_full_text=False,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
                repetition_penalty=self.repetition_penalty
            )

            llm = HuggingFacePipeline(pipeline=pipe)
            
            logger.info("모델 로딩 완료")
            return llm
            
        except Exception as e:
            logger.error(f"모델 로딩 중 오류 발생: {str(e)}")
            raise e
    
    def __call__(self):
        """
        모델 인스턴스를 반환합니다.
        """
        return self.llm
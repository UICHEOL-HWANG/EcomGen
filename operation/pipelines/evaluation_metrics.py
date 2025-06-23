import logging
import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import random
from prefect import flow, task

from storage.object import load_single_s3_json
from eval.inference import generate_description
from eval.evaluation import calculate_keywords_perplexity
from eval.wandb_logger import wandb_logger

load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def start_serve_mode():
    """프리팩트 serve 방식으로 실행"""
    logger.info("Prefect Cloud + 로컬 실행 모드 시작")
    perplexity_evaluation_flow.serve(
        name="perplexity-evaluation-serve",
        cron="0 9 1,15 * *",  # 매월 1일, 15일 오전 9시
        description="2주마다 실행되는 퍼플렉시티 평가",
        tags=["evaluation", "serve", "perplexity"]
    )


@task(name="load_evaluation_data", retries=3)
def load_data():
    """S3에서 평가 데이터 로드"""
    logger.info("데이터 로드 중...")
    data = load_single_s3_json(
        bucket_name=os.getenv("INSTRUCTION_BUCKETS"),
        key="main/argument_generated_dataset_final.json",
        aws_access_key=os.getenv("ACCESS_KEY"),
        aws_secret_key=os.getenv("SECRET_KEY"),
        endpoint_url=os.getenv("ENDPOINT_URL"),
    )
    
    if not data:
        raise ValueError("데이터 로드 실패")
    
    logger.info(f"총 {len(data)}개의 데이터 로드 완료")
    return data


@task(name="sample_data")
def sample_evaluation_data(data):
    """평가용 데이터 샘플링"""
    sample_size = int(os.getenv("EVAL_SAMPLE_SIZE", "5"))  
    eval_data = random.sample(data, min(sample_size, len(data)))
    logger.info(f"{len(eval_data)}개 샘플 선택")
    return eval_data


@task(name="evaluate_single_item", retries=2)
def evaluate_item(item):
    """단일 아이템 평가"""
    # 실제 데이터 구조에 맞게 키 값 추출
    product_name = item.get('name_cleaned', item.get('product_name', ''))
    category = item.get('main_category_name', item.get('category', ''))
    price = item.get('price', 0)
    
    # 키워드 처리 (top_keywords가 문자열로 되어 있을 수 있음)
    keywords_raw = item.get('top_keywords', item.get('keywords', []))
    if isinstance(keywords_raw, str):
        keywords = [k.strip() for k in keywords_raw.split(',')]
    else:
        keywords = keywords_raw if isinstance(keywords_raw, list) else []
    
    tone = item.get('tone', '기본')
    
    logger.info(f"평가 중: {product_name}")
    
    # 설명 생성
    start_time = time.time()
    try:
        description = generate_description(product_name, category, price, keywords, tone)
        generation_time = time.time() - start_time
        success = True
    except Exception as e:
        logger.error(f"생성 실패 {product_name}: {e}")
        description = ""
        generation_time = time.time() - start_time
        success = False
    
    # 퍼플렉시티 계산
    if description:
        ppl_result = calculate_keywords_perplexity(description, keywords)
    else:
        ppl_result = {"perplexity": float('inf'), "keywords_ratio": 0}
    
    return {
        "product_name": product_name,
        "category": category,
        "price": price,
        "keywords": keywords,
        "tone": tone,
        "success": success,
        "perplexity": ppl_result["perplexity"],
        "keywords_ratio": ppl_result["keywords_ratio"],
        "generation_time": round(generation_time, 2),
        "description": description,
        "original_id": item.get('original_id', None)
    }


@task(name="calculate_statistics")
def calculate_evaluation_statistics(results):
    """평가 결과 통계 계산"""
    successful = [r for r in results if r['success']]
    statistics = {}
    
    if successful:
        perplexities = [r['perplexity'] for r in successful if r['perplexity'] != float('inf')]
        avg_ppl = sum(perplexities) / len(perplexities) if perplexities else float('inf')
        avg_keywords = sum(r['keywords_ratio'] for r in successful) / len(successful)
        avg_time = sum(r['generation_time'] for r in successful) / len(successful)
        
        statistics = {
            "success_rate": len(successful) / len(results),
            "successful_count": len(successful),
            "avg_perplexity": avg_ppl,
            "avg_keywords_ratio": avg_keywords,
            "avg_generation_time": avg_time
        }
        
        logger.info("=== 평가 결과 ===")
        logger.info(f"성공률: {len(successful)}/{len(results)} ({len(successful)/len(results):.1%})")
        logger.info(f"평균 퍼플렉시티: {avg_ppl:.2f}")
        logger.info(f"평균 키워드 포함률: {avg_keywords:.1%}")
        logger.info(f"평균 생성 시간: {avg_time:.2f}초")
        
        # 베스트 결과
        best = min(successful, key=lambda x: x['perplexity'] if x['perplexity'] != float('inf') else float('inf'))
        logger.info(f"최고 결과: {best['product_name']} (퍼플렉시티: {best['perplexity']:.2f})")
    
    return statistics


@task(name="save_results")
def save_evaluation_results(results, statistics, eval_data_size):
    """평가 결과 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"perplexity_evaluation_scheduled_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "sample_size": eval_data_size,
            "statistics": statistics,
            "results": results,
            "wandb_run_id": wandb_logger.run_id,
            "execution_type": "scheduled"
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"결과 저장: {filename}")
    return filename


@task(name="wandb_logging")
def log_to_wandb(results, statistics, run_name):
    """WandB 로깅"""
    use_wandb = os.getenv("ENABLE_WANDB", "true").lower() == "true"
    if not use_wandb:
        logger.info("WandB 로깅 비활성화됨")
        return
    
    project_name = os.getenv("WANDB_PROJECT", "perplexity-evaluation-scheduled")
    
    try:
        # WandB 초기화
        wandb_logger.init(project_name, run_name)
        
        if wandb_logger.enabled:
            # 모든 데이터 로깅
            wandb_logger.log_all(results, statistics)
            logger.info("WandB 로깅 완료")
        
        return wandb_logger.run_id
    except Exception as e:
        logger.error(f"WandB 로깅 실패: {e}")
        return None
    finally:
        wandb_logger.finish()


@flow(name="perplexity-evaluation-flow", 
      description="2주마다 실행되는 퍼플렉시티 평가 플로우")
def perplexity_evaluation_flow():
    """메인 평가 플로우"""
    try:
        # 실행 정보
        run_name = f"scheduled_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"스케줄 평가 시작: {run_name}")
        
        # 1. 데이터 로드
        data = load_data()
        
        # 2. 샘플링
        eval_data = sample_evaluation_data(data)
        
        # 3. 병렬 평가 실행
        logger.info(f"{len(eval_data)}개 샘플 평가 시작")
        results = []
        for i, item in enumerate(eval_data, 1):
            logger.info(f"진행률: {i}/{len(eval_data)}")
            result = evaluate_item(item)
            results.append(result)
        
        # 4. 통계 계산
        statistics = calculate_evaluation_statistics(results)
        
        # 5. 결과 저장
        filename = save_evaluation_results(results, statistics, len(eval_data))
        
        # 6. WandB 로깅
        wandb_run_id = log_to_wandb(results, statistics, run_name)
        
        # 7. 아티팩트 업로드 (WandB 활성화된 경우)
        if wandb_run_id and os.getenv("ENABLE_WANDB", "true").lower() == "true":
            try:
                wandb_logger.init(os.getenv("WANDB_PROJECT", "perplexity-evaluation-scheduled"), run_name)
                wandb_logger.log_artifact(filename)
                wandb_logger.finish()
            except Exception as e:
                logger.error(f"아티팩트 업로드 실패: {e}")
        
        logger.info("스케줄 평가 완료!")
        return {
            "success": True,
            "results_count": len(results),
            "statistics": statistics,
            "filename": filename,
            "wandb_run_id": wandb_run_id
        }
        
    except Exception as e:
        logger.error(f"스케줄 평가 실행 오류: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # 프리팩트 serve 모드로 실행
    logger.info("퍼플렉시티 평가 서비스 시작...")
    start_serve_mode()

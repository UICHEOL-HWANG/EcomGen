import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import wandb

logger = logging.getLogger(__name__)


class WandBLogger:
    """WandB 로깅을 위한 클래스"""
    
    def __init__(self):
        self.enabled = False
        self.run = None
    
    def init(self, project_name: str = "perplexity-evaluation", run_name: str = None) -> bool:
        """WandB 초기화"""
        try:
            wandb_api_key = os.getenv("WANDB_API_KEY")
            if not wandb_api_key:
                logger.warning("WANDB_API_KEY가 설정되지 않았습니다. WandB 로깅이 비활성화됩니다.")
                return False
            
            # WandB 초기화
            self.run = wandb.init(
                project=project_name,
                name=run_name or f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                config={
                    "sample_size": int(os.getenv("EVAL_SAMPLE_SIZE", "5")),
                    "evaluation_date": datetime.now().isoformat(),
                }
            )
            self.enabled = True
            logger.info("WandB 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"WandB 초기화 실패: {e}")
            self.enabled = False
            return False
    
    def log_metrics(self, metrics: Dict[str, Any]):
        """기본 메트릭 로깅"""
        if not self.enabled or not self.run:
            return
        
        try:
            wandb.log(metrics)
        except Exception as e:
            logger.error(f"메트릭 로깅 실패: {e}")
    
    def log_results_table(self, results: List[Dict[str, Any]]):
        """결과를 테이블로 로깅"""
        if not self.enabled or not self.run:
            return
        
        try:
            # 성공한 결과만 필터링
            successful_results = [r for r in results if r.get('success')]
            
            if not successful_results:
                return
            
            table_data = []
            for result in successful_results:
                table_data.append([
                    result.get('product_name', ''),
                    result.get('category', ''),
                    result.get('price', 0),
                    result.get('perplexity', 0),
                    result.get('keywords_ratio', 0),
                    result.get('generation_time', 0),
                    len(result.get('description', '')),
                    ', '.join(result.get('keywords', []))
                ])
            
            # WandB 테이블 생성
            table = wandb.Table(
                columns=[
                    "Product Name", "Category", "Price", 
                    "Perplexity", "Keywords Ratio", "Generation Time", 
                    "Description Length", "Keywords"
                ],
                data=table_data
            )
            wandb.log({"evaluation_results": table})
            
        except Exception as e:
            logger.error(f"테이블 로깅 실패: {e}")
    
    def log_histograms(self, results: List[Dict[str, Any]]):
        """히스토그램 로깅"""
        if not self.enabled or not self.run:
            return
        
        try:
            successful_results = [r for r in results if r.get('success')]
            if not successful_results:
                return
            
            # 데이터 추출
            perplexities = [r['perplexity'] for r in successful_results if r['perplexity'] != float('inf')]
            keywords_ratios = [r['keywords_ratio'] for r in successful_results]
            generation_times = [r['generation_time'] for r in successful_results]
            
            # 히스토그램 로깅
            if perplexities:
                wandb.log({"perplexity_histogram": wandb.Histogram(perplexities)})
            wandb.log({"keywords_ratio_histogram": wandb.Histogram(keywords_ratios)})
            wandb.log({"generation_time_histogram": wandb.Histogram(generation_times)})
            
        except Exception as e:
            logger.error(f"히스토그램 로깅 실패: {e}")
    
    def log_category_stats(self, results: List[Dict[str, Any]]):
        """카테고리별 통계 로깅"""
        if not self.enabled or not self.run:
            return
        
        try:
            successful_results = [r for r in results if r.get('success')]
            
            # 카테고리별 통계 계산
            category_stats = {}
            for result in successful_results:
                category = result.get('category', 'Unknown')
                if category not in category_stats:
                    category_stats[category] = {'count': 0, 'perplexities': []}
                category_stats[category]['count'] += 1
                if result['perplexity'] != float('inf'):
                    category_stats[category]['perplexities'].append(result['perplexity'])
            
            # 카테고리별 메트릭 로깅
            for category, stats in category_stats.items():
                if stats['perplexities']:
                    avg_ppl = sum(stats['perplexities']) / len(stats['perplexities'])
                    wandb.log({f"category_{category}_avg_perplexity": avg_ppl})
                wandb.log({f"category_{category}_count": stats['count']})
                
        except Exception as e:
            logger.error(f"카테고리 통계 로깅 실패: {e}")
    
    def log_artifact(self, filepath: str, artifact_name: str = "evaluation_results", artifact_type: str = "results"):
        """아티팩트 업로드"""
        if not self.enabled or not self.run:
            return
        
        try:
            artifact = wandb.Artifact(artifact_name, type=artifact_type)
            artifact.add_file(filepath)
            wandb.log_artifact(artifact)
            logger.info(f"WandB에 아티팩트 업로드 완료: {filepath}")
        except Exception as e:
            logger.error(f"아티팩트 업로드 실패: {e}")
    
    def log_all(self, results: List[Dict[str, Any]], statistics: Dict[str, Any]):
        """모든 데이터를 한번에 로깅"""
        if not self.enabled:
            return
        
        # 기본 메트릭
        self.log_metrics({
            "success_rate": statistics.get("success_rate", 0),
            "avg_perplexity": statistics.get("avg_perplexity", 0),
            "avg_keywords_ratio": statistics.get("avg_keywords_ratio", 0),
            "avg_generation_time": statistics.get("avg_generation_time", 0),
            "total_samples": len(results),
            "successful_samples": statistics.get("successful_count", 0)
        })
        
        # 테이블, 히스토그램, 카테고리 통계
        self.log_results_table(results)
        self.log_histograms(results)
        self.log_category_stats(results)
        
        logger.info("WandB 로깅 완료")
    
    def finish(self):
        """WandB 실행 종료"""
        if self.enabled and self.run:
            wandb.finish()
            self.enabled = False
            self.run = None
    
    @property
    def run_id(self) -> Optional[str]:
        """현재 실행 ID 반환"""
        return self.run.id if self.enabled and self.run else None


# 전역 WandB 로거 인스턴스
wandb_logger = WandBLogger()

"""
부동산 거래 데이터 분석 패키지

사용 예시:
    from py import create_analyzer
    analyzer = create_analyzer('/path/to/data')
"""

from .core.analyzer import RealEstateAnalyzer
from .core.loader import DataLoader
from .config.settings import AnalysisConfig

__version__ = '1.0.0'
__all__ = ['create_analyzer', 'RealEstateAnalyzer', 'DataLoader', 'AnalysisConfig']


def create_analyzer(data_dir: str = None):
    """
    편의 함수: 분석기 인스턴스 생성
    
    Args:
        data_dir: 데이터 디렉토리 경로
    
    Returns:
        RealEstateAnalyzer 인스턴스
    """
    from pathlib import Path
    
    if data_dir is None:
        # 프로젝트 루트의 data 폴더를 기본으로 사용
        data_dir = Path(__file__).parent.parent / 'data'
    
    config = AnalysisConfig(data_dir=data_dir)
    loader = DataLoader(config)
    return RealEstateAnalyzer(loader)
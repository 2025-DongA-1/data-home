"""
부동산 분석 라이브러리 테스트

실행 방법:
    python test.py
"""

import json
from pathlib import Path

# 방법 1: 간단한 API 사용
# py/__init__.py에 정의된 create_analyzer를 가져옴
from py import create_analyzer

def test_simple_api():
    """편의 함수를 사용한 테스트"""
    print("=" * 60)
    print("[ 방법 1: create_analyzer() 사용 ]")
    print("=" * 60)
    
    # 데이터 경로 자동 탐지
    data_dir = Path(__file__).parent / 'data'
    analyzer = create_analyzer(str(data_dir))
    
    # 1. 전체 데이터 조회
    results = analyzer.get_monthly_volume_and_area()
    
    print(f"\n✓ (전체) 월별 데이터 {len(results)}건 분석 완료")
    print(f"✓ (전체) 샘플 데이터 (상위 3개):")
    print(json.dumps(results[:3], ensure_ascii=False, indent=2))

    # 2. '서울'의 1~3월 데이터만 조회
    print("\n✓ (필터링 테스트) '서울' 1~3월 데이터 조회")
    sido_filter = ['서울특별시']  # 조회할 시도(광역 지자체) 입려력
    start_m = '1월'  # 조회할 범위의 시작 컬럼명
    end_m = '3월'  # 조회할 범위의 마지막 컬럼명
    
    filtered_results = analyzer.get_monthly_volume_and_area(
        sidos=sido_filter,
        start_m=start_m,
        end_m=end_m
    )
    
    print(f"✓ (필터링) {len(filtered_results)}건 조회 완료")
    print(f"✓ (필터링) 샘플 데이터 (전체):")
    print(json.dumps(filtered_results, ensure_ascii=False, indent=2))


def test_detailed_api():
    """세밀한 제어가 필요한 경우"""
    print("\n" + "=" * 60)
    print("[ 방법 2: 수동 인스턴스 생성 ]")
    print("=" * 60)
    
    from py.config.settings import AnalysisConfig
    from py.core.loader import DataLoader
    from py.core.analyzer import RealEstateAnalyzer
    
    # 커스텀 설정
    config = AnalysisConfig(
        data_dir=Path(__file__).parent / 'data',
        encoding='utf-8-sig'
    )
    
    loader = DataLoader(config)
    analyzer = RealEstateAnalyzer(loader)
    
    # 월간 거래량 조회
    monthly_volume = analyzer.get_sido_monthly_volume(sidos=['부산광역시', '광주광역시']) # 필터링 테스트
    print(f"\n✓ [필터링됨] 월간 거래량 데이터: {len(monthly_volume)}개 시도")
    print(f"✓ 샘플 데이터:")
    print(json.dumps(monthly_volume, ensure_ascii=False, indent=2))
    
    # 캐시 상태 확인
    print(f"\n✓ 캐시 활성화: {loader._volume_cache is not None}")
    
    # 강제 리로드
    loader.load_volume_data(force_reload=True)
    print(f"✓ 데이터 재로드 완료")


def test_error_handling():
    """에러 핸들링 테스트"""
    print("\n" + "=" * 60)
    print("[ 방법 3: 에러 핸들링 ]")
    print("=" * 60)
    
    from py.config.settings import AnalysisConfig
    
    try:
        # 존재하지 않는 경로
        config = AnalysisConfig(data_dir='/nonexistent/path')
    except ValueError as e:
        print(f"✓ 예상된 에러 포착: {e}")


if __name__ == '__main__':
    test_simple_api()
    test_detailed_api()
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("[ 모든 테스트 완료 ]")
    print("=" * 60)
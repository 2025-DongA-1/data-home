"""
방법 1: 간단한 API (기본 경로 사용)
from realestate_analyzer import create_analyzer

analyzer = create_analyzer()
results = analyzer.get_sido_monthly_volume()

방법 2: 커스텀 경로 사용
analyzer = create_analyzer('/custom/data/path')
results = analyzer.get_total_volume_vs_area()

방법 3: 세밀한 제어가 필요한 경우
from realestate_analyzer import AnalysisConfig, DataLoader, RealEstateAnalyzer

config = AnalysisConfig(
    data_dir='/my/path',
    volume_filename='custom_volume.csv'
)
loader = DataLoader(config)
analyzer = RealEstateAnalyzer(loader)

캐시 강제 리로드
loader.load_volume_data(force_reload=True)
"""
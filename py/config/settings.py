from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class AnalysisConfig:
    """분석 설정을 관리하는 객체"""
    
    data_dir: Path
    volume_filename: str = '2020년 광역 지자체별 아파트 거래량.csv'
    area_filename: str = '2020년 지자체 거래 호수 및 면적 통계자료.csv'
    encoding: str = 'utf-8-sig'
    
    def __post_init__(self):
        """경로 검증"""
        self.data_dir = Path(self.data_dir)
        if not self.data_dir.exists():
            raise ValueError(f"데이터 디렉토리가 존재하지 않음: {self.data_dir}")
    
    @property
    def volume_path(self) -> Path:
        return self.data_dir / self.volume_filename
    
    @property
    def area_path(self) -> Path:
        return self.data_dir / self.area_filename
    
    @classmethod
    def from_base_dir(cls, base_dir: Optional[Path] = None) -> 'AnalysisConfig':
        """기본 설정으로 생성 (하위 호환성)"""
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / 'data'
        return cls(data_dir=base_dir)
import pandas as pd
from typing import Optional
from ..config.settings import AnalysisConfig 

class DataLoader:
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self._volume_cache: Optional[pd.DataFrame] = None
        self._area_cache: Optional[pd.DataFrame] = None
    
    def load_volume_data(self, force_reload: bool = False) -> pd.DataFrame:
        if self._volume_cache is not None and not force_reload:
            return self._volume_cache
        
        try:
            df = pd.read_csv(self.config.volume_path, encoding=self.config.encoding)
            df = df.rename(columns={'광역지방자치단체': '시도'})
            df_clean = df[df['시도'] != '전국'].reset_index(drop=True)
            self._volume_cache = df_clean
            return df_clean
        except FileNotFoundError:
            raise FileNotFoundError(f"파일 없음: {self.config.volume_path}")
    
    def load_area_data(self, force_reload: bool = False) -> pd.DataFrame:
        if self._area_cache is not None and not force_reload:
            return self._area_cache
        
        try:
            df = pd.read_csv(
                self.config.area_path,
                encoding=self.config.encoding,
                header=[0, 1]
            )
            
            # 멀티인덱스 정리
            new_cols = []
            for col in df.columns:
                if col[0] == col[1]:
                    new_cols.append(col[0])
                else:
                    metric = '면적' if '면적' in col[1] else col[1]
                    new_cols.append(f"{col[0]}_{metric}")
            
            df.columns = new_cols
            df = df.rename(columns={
                '행정구역별(1)': '시도',
                '행정구역별(2)': '시군구'
            })
            
            df_clean = df[
                df['시군구'].str.contains('소계', na=False)
            ].reset_index(drop=True)
            df_clean = df_clean[df_clean['시도'] != '전국'].reset_index(drop=True)
            
            self._area_cache = df_clean
            return df_clean
        except FileNotFoundError:
            raise FileNotFoundError(f"파일 없음: {self.config.area_path}")
    
    def clear_cache(self):
        self._volume_cache = None
        self._area_cache = None
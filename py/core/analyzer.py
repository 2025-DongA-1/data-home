from typing import List, Dict, Union, Optional
import pandas as pd
from .loader import DataLoader 


class RealEstateAnalyzer:
    """
    부동산 데이터 로더를 사용하여 데이터를 분석하는 클래스
    """
    
    def __init__(self, loader: DataLoader):
        """
        RealEstateAnalyzer 인스턴스를 초기화합니다.

        Args:
            loader (DataLoader): 데이터를 로드할 DataLoader 인스턴스
        """
        self.loader = loader
    
    def get_sido_monthly_volume(
        self, 
        sidos: Optional[List[str]] = None
    ) -> List[Dict[str, Union[str, int]]]:
        """
        시도별 월간 거래량(호수) 원본 데이터를 반환합니다. (Wide 포맷)

        Args:
            sidos (Optional[List[str]]): 
                필터링할 '시도' 이름의 리스트. None이면 전체 반환.
        """
        df = self.loader.load_volume_data()
        
        if sidos: 
            df = df[df['시도'].isin(sidos)].reset_index(drop=True)
            
        return df.to_dict(orient='records')
    
    def get_sido_monthly_area(
        self,
        sidos: Optional[List[str]] = None 
    ) -> List[Dict[str, Union[str, int]]]:
        """
        시도별 월간 거래 면적(천㎡) 원본 데이터를 반환합니다. (Wide 포맷)

        Args:
            sidos (Optional[List[str]]): 
                필터링할 '시도' 이름의 리스트. None이면 전체 반환.
        """
        df = self.loader.load_area_data()
        
        if sidos: # [축약]
            df = df[df['시도'].isin(sidos)].reset_index(drop=True)

        # [축약] area_cols -> a_cols
        a_cols = ['시도'] + [col for col in df.columns if '_면적' in col]
        
        valid_cols = [col for col in a_cols if col in df.columns]
        return df[valid_cols].to_dict(orient='records')
    
    def get_monthly_volume_and_area(
        self,
        sidos: Optional[List[str]] = None,
        start_m: Optional[str] = None,
        end_m: Optional[str] = None
    ) -> List[Dict[str, Union[str, int]]]:
        """
        시도별/월별 거래 호수와 거래 면적을 결합하여 'Long' 포맷으로 반환합니다.

        Args:
            sidos (Optional[List[str]]): 
                필터링할 '시도' 이름 리스트. None이면 전체.
            start_m (Optional[str]): 
                조회 시작 월 (YYYY-MM). None이면 처음부터.
            end_m (Optional[str]): 
                조회 종료 월 (YYYY-MM). None이면 끝까지.
        """
        # [축약] df_volume -> df_v, df_area -> df_a
        df_v = self.loader.load_volume_data()
        df_a = self.loader.load_area_data()
        
        if sidos:
            df_v = df_v[df_v['시도'].isin(sidos)].reset_index(drop=True)
            df_a = df_a[df_a['시도'].isin(sidos)].reset_index(drop=True)

        if df_v.empty or df_a.empty:
            return []
            
        vol_long = df_v.melt(
            id_vars=['시도'],
            var_name='월',
            value_name='거래호수'
        )
        
        a_cols = [col for col in df_a.columns if '_면적' in col]
        area_long = df_a.melt(
            id_vars=['시도'],
            value_vars=a_cols,
            var_name='월_col', 
            value_name='거래면적(천㎡)'
        )
        
        area_long['월'] = area_long['월_col'].str.replace('_면적', '')
        area_long = area_long.drop(columns=['월_col'])
        
        merged_df = pd.merge(
            vol_long, 
            area_long, 
            on=['시도', '월'], 
            how='outer'
        )
        
        if start_m:
            merged_df = merged_df[merged_df['월'] >= start_m]
                
        if end_m:
            merged_df = merged_df[merged_df['월'] <= end_m]

        merged_df = merged_df.fillna(0)
        
        merged_df['거래면적(천㎡)'] = (
            merged_df['거래면적(천㎡)'].round(0).astype(int)
        )
        merged_df['거래호수'] = merged_df['거래호수'].astype(int)
        
        merged_df = merged_df.sort_values(by=['시도', '월']).reset_index(drop=True)
        
        return merged_df.to_dict(orient='records')
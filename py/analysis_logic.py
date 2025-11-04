import pandas as pd
import warnings
import os
import json
from typing import List, Dict, Union


warnings.filterwarnings('ignore', category=UserWarning, module='pandas')

# 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')


# --- 1. 데이터 로딩 및 전처리 ---

def _load_and_clean_data():
    """
    두 개의 CSV 파일을 로드하고 분석에 적합하게 전처리
    
    Returns:
        tuple: (df_volume_clean, df_area_clean) 전처리된 DataFrame 튜플
    """
    
    # File 1: 거래량
    try:
        file1_path = os.path.join(DATA_DIR, '2020년 광역 지자체별 아파트 거래량.csv')
        df_volume = pd.read_csv(file1_path, encoding='utf-8-sig')
        
        df_volume = df_volume.rename(columns={'광역지방자치단체': '시도'})
        df_volume_clean = (
            df_volume[df_volume['시도'] != '전국']
            .reset_index(drop=True)
        )
        
    except FileNotFoundError:
        print(f"경고: '{file1_path}' 파일을 찾을 수 없습니다.")
        df_volume_clean = pd.DataFrame()
    except Exception as e:
        print(f"df_volume 로드 중 에러: {e}")
        df_volume_clean = pd.DataFrame()
    
    # File 2: 면적 통계
    try:
        file2_path = os.path.join(DATA_DIR, '2020년 지자체 거래 호수 및 면적 통계자료.csv')
        df_area = pd.read_csv(file2_path, encoding='utf-8-sig', header=[0, 1])
        
        # 멀티인덱스 컬럼 정리
        new_cols = []
        for col in df_area.columns:
            if col[0] == col[1]:
                new_cols.append(col[0])
            else:
                metric = '면적' if '면적' in col[1] else col[1]
                new_cols.append(f"{col[0]}_{metric}")
        
        df_area.columns = new_cols
        
        df_area = df_area.rename(columns={
            '행정구역별(1)': '시도',
            '행정구역별(2)': '시군구'
        })
        
        df_area_clean = df_area[
            df_area['시군구'].str.contains('소계', na=False)
        ].reset_index(drop=True)
        df_area_clean = df_area_clean[
            df_area_clean['시도'] != '전국'
        ].reset_index(drop=True)
        
    except FileNotFoundError:
        print(f"경고: '{file2_path}' 파일을 찾을 수 없습니다.")
        df_area_clean = pd.DataFrame()
    except Exception as e:
        print(f"df_area 로드 중 에러: {e}")
        df_area_clean = pd.DataFrame()
    
    return df_volume_clean, df_area_clean


# 모듈 레벨 데이터 로딩
try:
    DF_VOLUME, DF_AREA = _load_and_clean_data()
except Exception as e:
    print(f"초기 데이터 로드 실패: {e}")
    DF_VOLUME, DF_AREA = pd.DataFrame(), pd.DataFrame()


# --- 2. 분석 함수 ---

def get_sido_monthly_volume() -> List[Dict[str, Union[str, int]]]:
    """
    시도별 월간 아파트 거래량(호수) 반환
    
    Returns:
        List[Dict]: [{"시도": "서울특별시", "1월": 17545, ...}, ...]
                    데이터 없으면 빈 리스트 []
    """
    if DF_VOLUME.empty:
        return []
    
    return DF_VOLUME.to_dict(orient='records')


def get_sido_monthly_area() -> List[Dict[str, Union[str, int]]]:
    """
    시도별 월간 아파트 거래 면적(천㎡) 반환
    
    Returns:
        List[Dict]: [{"시도": "서울특별시", "1월_면적": 1217, ...}, ...]
    """
    if DF_AREA.empty:
        return []
    
    area_cols = ['시도'] + [col for col in DF_AREA.columns if '_면적' in col]
    df_area_only = DF_AREA[area_cols]
    
    return df_area_only.to_dict(orient='records')


def get_total_volume_vs_area() -> List[Dict[str, Union[str, int]]]:
    """
    시도별 2020년 연간 총 거래 호수 및 면적 합산
    
    Returns:
        List[Dict]: [{"시도": "...", "연간_총거래호수": ..., "연간_총거래면적(천㎡)": ...}, ...]
                    데이터 부족 시 빈 리스트 []
    """
    if DF_VOLUME.empty or DF_AREA.empty:
        print("경고: 데이터가 부족하여 연간 합산에 실패했습니다.")
        return []
    
    # 거래 호수 합계
    df_vol_indexed = DF_VOLUME.set_index('시도')
    df_vol_total = (
        df_vol_indexed.select_dtypes(include='number')
        .sum(axis=1)
        .reset_index(name='연간_총거래호수')
    )
    
    # 거래 면적 합계
    df_area_indexed = DF_AREA.set_index('시도')
    area_cols = [col for col in df_area_indexed.columns if '_면적' in col]
    df_area_total = (
        df_area_indexed[area_cols]
        .sum(axis=1)
        .reset_index(name='연간_총거래면적(천㎡)')
    )
    
    # 병합 및 정제
    df_merged = pd.merge(df_vol_total, df_area_total, on='시도', how='outer')
    df_merged['연간_총거래면적(천㎡)'] = (
        df_merged['연간_총거래면적(천㎡)'].round(0).astype(int)
    )
    df_merged = df_merged.fillna(0)
    
    return df_merged.to_dict(orient='records')


# --- 3. 테스트 코드 ---

if __name__ == '__main__':
    print("=" * 60)
    print("[ analysis_logic.py 테스트 실행 ]")
    print("=" * 60)
    
    if DF_VOLUME.empty or DF_AREA.empty:
        print("\n!! 테스트 실패: 파일이 로드되지 않았습니다. !!\n")
    else:
        # 1. 거래량 테스트
        print("\n[1] get_sido_monthly_volume() 테스트")
        print("-" * 60)
        volume_data = get_sido_monthly_volume()
        if volume_data:
            print(f"✓ 총 {len(volume_data)}개 시도 데이터 반환됨")
            print(f"✓ 샘플 데이터 (첫 1개):")
            print(json.dumps(volume_data[:1], ensure_ascii=False, indent=2))
        else:
            print("✗ 반환된 데이터 없음")
        
        # 2. 면적 테스트
        print("\n[2] get_sido_monthly_area() 테스트")
        print("-" * 60)
        area_data = get_sido_monthly_area()
        if area_data:
            print(f"✓ 총 {len(area_data)}개 시도 데이터 반환됨")
            print(f"✓ 샘플 데이터 (첫 1개):")
            print(json.dumps(area_data[:1], ensure_ascii=False, indent=2))
        else:
            print("✗ 반환된 데이터 없음")
        
        # 3. 연간 합계 테스트
        print("\n[3] get_total_volume_vs_area() 테스트")
        print("-" * 60)
        total_data = get_total_volume_vs_area()
        if total_data:
            print(f"✓ 총 {len(total_data)}개 시도 연간 합계 반환됨")
            print(f"✓ 샘플 데이터 (첫 2개):")
            print(json.dumps(total_data[:2], ensure_ascii=False, indent=2))
        else:
            print("✗ 빈 데이터")
    
    print("\n" + "=" * 60)
    print("[ 테스트 종료 ]")
    print("=" * 60 + "\n")
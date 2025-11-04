import pandas as pd
from dateutil import parser

# 공통 보조 함수

def safe_datetime(df, col):
    """
    문자열 형태의 날짜 데이터를 datetime 형식으로 변환합니다.
    이미 datetime 형식일 경우에는 변환하지 않습니다.
    변환 불가능한 값은 NaT로 처리합니다.
    """
    if not pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = pd.to_datetime(df[col], errors='coerce')
    return df


def safe_numeric(df, col):
    """
    쉼표(,)가 포함된 문자열 숫자 데이터를 float형으로 변환합니다.
    이미 숫자형일 경우에는 변환하지 않습니다.
    변환 불가능한 값은 NaN으로 처리합니다.
    """
    if not pd.api.types.is_numeric_dtype(df[col]):
        df[col] = df[col].astype(str).str.replace(',', '', regex=False).astype(float)
    return df


# 날짜열 정리 함수

def clean_date_column(df, date_name):
    """
    주어진 날짜 열(date_col)에 존재하는 다양한 날짜 형식을 datetime 형식으로 통일합니다.
    원본 DataFrame은 수정하지 않으며, 복사본을 반환합니다.

    매개변수:
        df (pd.DataFrame): 원본 데이터프레임
        date_col (str): 날짜가 포함된 열 이름

    반환값:
        pd.DataFrame: 날짜가 datetime 형식으로 변환된 DataFrame 복사본
    """

    # 1. 문자열 변환 + 특수 공백 제거
    df[date_name] = (
        df[date_name]
        .astype(str)
        .str.strip()
        .str.replace(r'[\u00A0\u202F\u3000]', '', regex=True)  # 비정상 공백 제거
        .str.replace(r'[^\x00-\x7F]', '', regex=True)  # 비ASCII 문자 제거 (숨은 BOM 등)
    )

    # 2. 안전한 파서 정의
    def parse_date_safe(x):
        if not x or x.lower() in ["nan", "none", "nat"]:
            return pd.NaT
        try:
            # yearfirst=True : YYYY-MM-DD 우선
            # fuzzy=True : "0:00" 같은 잔여 텍스트 무시
            return parser.parse(x, yearfirst=True, fuzzy=True)
        except Exception:
            return pd.NaT

    # 3. 변환 수행
    df[date_name] = df[date_name].apply(parse_date_safe)

    # 4. 결과 타입 확인
    if not pd.api.types.is_datetime64_any_dtype(df[date_name]):
        df[date_name] = pd.to_datetime(df[date_name], errors='coerce')

    return df



# 일별 통계 함수


def day_stat(df, date_col, value_col, stats=None):
    """
    일별 거래 통계를 계산합니다. (합계, 평균, 최대, 최소, 거래건수)

    매개변수:
        df (pd.DataFrame): 원본 데이터프레임
        date_col (str): 날짜가 포함된 열 이름
        value_col (str): 거래금액이 포함된 열 이름
        stats (list[str], 선택): 계산할 통계 항목. 예: ['합계', '평균'] 지정하지 않으면 모든 항목을 계산합니다.

    반환값:
        pd.DataFrame: 일별 통계 결과 (거래일, 합계, 평균, 최대, 최소, 거래건수)
    """
    data = df.copy()
    data = safe_datetime(data, date_col)
    data = safe_numeric(data, value_col)

    data['_거래일'] = data[date_col].dt.strftime('%Y-%m-%d')

    agg_map = {
        '합계': 'sum',
        '평균': 'mean',
        '최대': 'max',
        '최소': 'min',
        '거래건수': 'count'
    }

    if stats is None:
        stats = list(agg_map.keys())
    agg_selected = {k: agg_map[k] for k in stats if k in agg_map}

    result = (
        data.groupby('_거래일')[value_col]
        .agg(**agg_selected)
        .reset_index()
        .rename(columns={'_거래일': '거래일'})
        .sort_values('거래일')
        .reset_index(drop=True)
    )

    return result


# 월별 통계 함수

def month_stat(df, date_col, value_col, stats=None):
    """
    월별 거래 통계를 계산합니다. (합계, 평균, 최대, 최소, 거래건수)
    월은 'YYYY.MM' 형식으로 표시됩니다.

    매개변수:
        df (pd.DataFrame): 원본 데이터프레임
        date_col (str): 날짜가 포함된 열 이름
        value_col (str): 거래금액이 포함된 열 이름
        stats (list[str], 선택): 계산할 통계 항목. 지정하지 않으면 모두 계산합니다.

    반환값:
        pd.DataFrame: 월별 통계 결과 (년월, 합계, 평균, 최대, 최소, 거래건수)
    """
    data = df.copy()
    data = safe_datetime(data, date_col)
    data = safe_numeric(data, value_col)

    data['_년월'] = data[date_col].dt.strftime('%Y.%m')

    agg_map = {
        '합계': 'sum',
        '평균': 'mean',
        '최대': 'max',
        '최소': 'min',
        '거래건수': 'count'
    }

    if stats is None:
        stats = list(agg_map.keys())
    agg_selected = {k: agg_map[k] for k in stats if k in agg_map}

    result = (
        data.groupby('_년월')[value_col]
        .agg(**agg_selected)
        .reset_index()
        .rename(columns={'_년월': '년월'})
        .sort_values('년월')
        .reset_index(drop=True)
    )

    return result



# 년도별 통계 함수


def year_stat(df, date_col, value_col, stats=None):
    """
    년도별 거래 통계를 계산합니다. (합계, 평균, 최대, 최소, 거래건수)

    매개변수:
        df (pd.DataFrame): 원본 데이터프레임
        date_col (str): 날짜가 포함된 열 이름
        value_col (str): 거래금액이 포함된 열 이름
        stats (list[str], 선택): 계산할 통계 항목. 지정하지 않으면 모두 계산합니다.

    반환값:
        pd.DataFrame: 년도별 통계 결과 (년도, 합계, 평균, 최대, 최소, 거래건수)
    """
    data = df.copy()
    data = safe_datetime(data, date_col)
    data = safe_numeric(data, value_col)

    data['_년도'] = data[date_col].dt.year

    agg_map = {
        '합계': 'sum',
        '평균': 'mean',
        '최대': 'max',
        '최소': 'min',
        '거래건수': 'count'
    }

    if stats is None:
        stats = list(agg_map.keys())
    agg_selected = {k: agg_map[k] for k in stats if k in agg_map}

    result = (
        data.groupby('_년도')[value_col]
        .agg(**agg_selected)
        .reset_index()
        .rename(columns={'_년도': '년도'})
        .sort_values('년도')
        .reset_index(drop=True)
    )

    return result



# 주간 통계 함수 (월 포함, 월요일 기준)


def week_stat(df, date_col, value_col, stats=None):
    """
    월요일 기준으로 주간 거래 통계를 계산합니다.
    주차는 ISO 주차 기준으로 계산되며, 결과에는 년도, 월, 주차, 주시작일이 포함됩니다.


    매개변수:
        df (pd.DataFrame): 원본 데이터프레임
        date_col (str): 날짜가 포함된 열 이름
        value_col (str): 거래금액이 포함된 열 이름
        stats (list[str], 선택): 계산할 통계 항목. 지정하지 않으면 모두 계산합니다.

    반환값:
        pd.DataFrame: 주별 통계 결과 (년도, 월, 주차, 주시작일, 합계, 평균, 최대, 최소, 거래건수)
    """
    data = df.copy()
    iso = data[date_col].dt.isocalendar()
    data['_주차'] = iso['week']

    # 주 시작일 계산 (월요일)
    data['_주시작일'] = data[date_col] - pd.to_timedelta(data[date_col].dt.weekday, unit='D')

    # 년월 (YYYY.MM 형식)
    data['_년월'] = data['_주시작일'].dt.strftime('%Y.%m')

    agg_map = {
        '합계': 'sum',
        '평균': 'mean',
        '최대': 'max',
        '최소': 'min',
        '거래건수': 'count'
    }

    # 선택된 통계만 사용
    if stats is None:
        stats = list(agg_map.keys())
    agg_selected = {k: agg_map[k] for k in stats if k in agg_map}

    # 그룹별 계산
    result = (
        data.groupby(['_년월', '_주차', '_주시작일'])[value_col]
        .agg(**agg_selected)
        .reset_index()
        .rename(columns={
            '_년월': '년월',
            '_주차': '주차',
            '_주시작일': '주시작일'
        })
        .sort_values(['년월', '주차'])
        .reset_index(drop=True)
    )

    return result

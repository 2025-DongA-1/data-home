import pandas as pd
from dateutil import parser

def clean_date_column(df, column_name):
    """
    날짜 형식이 섞여 있는 열을 자동으로 인식해 YYYY-MM-DD 형식으로 통일해주는 함수

    Parameters:
        df (pd.DataFrame): 원본 데이터프레임
        column_name (str): 날짜가 들어 있는 열 이름

    Returns:
        pd.DataFrame: 날짜 열이 정리된 DataFrame
    """
    # 1️⃣ 문자열로 변환하고 공백 제거
    df[column_name] = (
        df[column_name]
        .astype(str)
        .str.strip()
        .str.replace('\u00A0', '', regex=False)  # 비정상 공백 제거
    )

    # 2️⃣ dateutil.parser로 다양한 날짜 형식 처리
    def parse_date_safe(x):
        try:
            return parser.parse(x)
        except Exception:
            return pd.NaT  # 인식 불가한 값은 NaT 처리

    df[column_name] = df[column_name].apply(parse_date_safe)

    # 3️⃣ 보기 좋은 날짜 문자열(YYYY-MM-DD)로 통일
    df[column_name] = df[column_name].dt.strftime('%Y-%m-%d')

    return df

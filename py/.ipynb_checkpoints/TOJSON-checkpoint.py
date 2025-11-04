import pandas as pd
import json
import date_cmp as dc



#def csv_to_json (  ,filep = )#일 위치 수정 필요


# 액샐 읽기         
df = pd.read_csv(../data/apttest.csv)

# 날짜 형식 정렬
df = dc.clean_date_column(df ,'거래일')

# 계산된 df
day_result = dc.day_stat(df , '거래일', '거래금액')
week_result = dc.week_stat(df , '거래일', '거래금액')
month_result = dc.month_stat(df , '거래일', '거래금액')
year_result = dc.year_stat(df , '거래일', '거래금액')


output = {
    "일간": day_result.to_dict(orient='records'),
    "주간": week_result.to_dict(orient='records'),
    "월간": month_result.to_dict(orient='records'),
    "년간": year_result.to_dict(orient='records')
}



with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)



print(" result.json 생성 완료")




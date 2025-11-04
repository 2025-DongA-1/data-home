import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import sys

# -------------------------------------------------------------
# 1. 기본 설정 (한글 폰트)
# -------------------------------------------------------------
# 윈도우: 'Malgun Gothic'
# 맥: 'AppleGothic'
# 리눅스: 'NanumGothic' (설치 필요)
try:
    # 윈도우 환경
    rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지
except:
    # 다른 환경 (맥, 리눅스 등)
    try:
        rc('font', family='AppleGothic')
        plt.rcParams['axes.unicode_minus'] = False
    except:
        print("경고: 'Malgun Gothic' 또는 'AppleGothic' 폰트를 찾을 수 없습니다.")
        print("그래프의 한글이 깨질 수 있습니다. 사용 중인 OS에 맞는 한글 폰트를 설정해주세요.")


# -------------------------------------------------------------
# 2. 데이터 로드 및 전처리
# -------------------------------------------------------------
try:
    # CSV 파일 로드
    file_path = './statistical data/광역 지자체별 지역별_아파트_거래량.csv'
    data = pd.read_csv(file_path, encoding='UTF-8')
    print(f"--- 1. 원본 데이터 로드 완료 ---")
    print(data.head())
    print("\n")

except FileNotFoundError:
    print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
    print("스크립트와 동일한 폴더에 CSV 파일이 있는지 확인해주세요.")
    sys.exit() # 파일이 없으면 스크립트 종료
except Exception as e:
    print(f"데이터 로드 중 오류 발생: {e}")
    sys.exit()


# '2020.'이 포함된 모든 월별 컬럼을 찾아 합산 -> '2020' 컬럼 생성
# (Notebook Cell 3)
data['2020'] = data.filter(like='2020.').astype(float).sum(axis=1).astype(int)
print(f"--- 2. '2020' 연간 총합 컬럼 생성 완료 ---")
print(data.head())
print("\n")


# 첫 번째 컬럼('광역지방자치단체')을 인덱스로 설정
# (Notebook Cell 5)
data.set_index(data.columns[0], inplace=True)
print(f"--- 3. '광역지방자치단체' 인덱스 설정 완료 ---")
print(data.head())
print("\n")


# -------------------------------------------------------------
# 3. 시각화 데이터 준비
# -------------------------------------------------------------
# '전국' 행을 제외한 새로운 데이터프레임 만들기
data_cities = data.drop('전국')

# '2020' (연간 총합) 기준으로 내림차순 정렬
data_cities = data_cities.sort_values(by='2020', ascending=False)

# x축 (인덱스), y축 (2020 총합) 데이터 준비
x = data_cities.index
y = data_cities['2020']


# -------------------------------------------------------------
# 4. 그래프 생성 및 표시
# -------------------------------------------------------------
print("--- 4. 막대 그래프 생성 중 ---")

# 그래프 크기 설정
plt.figure(figsize=(12, 7))

# 기본 막대 그래프 그리기
plt.bar(x, y)

# 그래프 제목 및 레이블 설정
plt.title('2020년 지자체별 거래량', fontsize=16)
plt.xlabel('광역지방자치단체', fontsize=12)
plt.ylabel('총 거래량', fontsize=12)

plt.xticks(rotation=90) # X축 레이블 90도 회전
plt.grid(axis='y', linestyle='--', alpha=0.7) # Y축 그리드 추가

plt.tight_layout() # 레이블이 잘리지 않도록 레이아웃 조정

# 그래프 출력
plt.show()

print("--- 5. 그래프가 성공적으로 표시되었습니다. ---")
# 부동산 거래 데이터 분석 라이브러리 README

이 라이브러리는 '광역 지자체별 아파트 거래량'과 '지자체 거래 호수 및 면적 통계'라는 두 개의 서로 다른 CSV 파일을 로드하고, 이를 병합 및 정제하여 시도별/월별 거래 데이터를 분석할 수 있는 기능을 제공합니다.

## 프로젝트 구조

라이브러리를 올바르게 사용하기 위해 다음과 같은 디렉토리 구조를 권장합니다.

/ (프로젝트 루트)
├── py/                  # 👈 라이브러리 소스 코드 (패키지)
│   ├── __init__.py      # 👈 create_analyzer 편의 함수
│   ├── config/
│   │   └── settings.py  # 👈 AnalysisConfig (설정)
│   └── core/
│       ├── analyzer.py  # 👈 RealEstateAnalyzer (분석)
│       └── loader.py      # 👈 DataLoader (I/O, 캐시)
│
├── data/                # 👈 분석할 데이터 (py/ 폴더와 같은 위치)
│   ├── 2020년 광역 지자체별 아파트 거래량.csv
│   └── 2020년 지자체 거래 호수 및 면적 통계자료.csv
│
└── test.py              # 👈 라이브러리 테스트 스크립트 (py/ 폴더와 같은 위치)

## 🚀 실행 원리

이 라이브러리는 **Config → Loader → Analyzer** 3단계의 계층적 구조로 작동합니다.

### 1. `AnalysisConfig` (설정 계층)

* `py/config/settings.py`에 정의되어 있습니다.
* 분석에 필요한 모든 설정값(데이터 디렉토리 경로, 파일명, 인코딩 등)을 관리합니다.
* `@property`를 통해 `volume_path`, `area_path` 등 동적 경로를 생성합니다.
* 인스턴스 생성 시(`__post_init__`) `data_dir`의 존재 여부를 즉시 검증하여 오류를 미리 방지합니다.

### 2. `DataLoader` (데이터 I/O 및 캐시 계층)

* `py/core/loader.py`에 정의되어 있습니다.
* `AnalysisConfig`를 주입받아 실제 파일 경로를 인지합니다.
* **파일 로드:** `pd.read_csv`를 사용해 CSV 파일을 Pandas DataFrame으로 로드합니다.
    * `load_volume_data`: 단일 헤더의 '거래량' 파일을 로드합니다.
    * `load_area_data`: **멀티인덱스 헤더**(`header=[0, 1]`)로 구성된 '면적' 파일을 로드하고, `(2020-01, 면적)` 같은 복잡한 컬럼명을 `2020-01_면적`처럼 사용하기 쉬운 단일 문자열로 자동 변환합니다.
* **기본 전처리:** '전국' 데이터를 제외하고, '시도' 컬럼명을 표준화하는 등 최소한의 전처리를 수행합니다. (이 단계에서는 '서울특별시'를 '서울'로 줄이는 등의 **값 정규화는 수행하지 않습니다.**)
* **캐시(Cache):**
    * 로드된 DataFrame을 `_volume_cache`, `_area_cache` 내부 변수에 저장합니다.
    * 데이터 로드 함수가 다시 호출되면, 파일을 다시 읽지 않고 캐시된 DataFrame을 즉시 반환하여 성능을 향상시킵니다.
    * `force_reload=True` 옵션을 통해 캐시를 무시하고 파일을 강제로 다시 읽도록 할 수 있습니다.

### 3. `RealEstateAnalyzer` (분석 및 정제 계층)

* `py/core/analyzer.py`에 정의되어 있습니다.
* `DataLoader`를 주입받아 데이터가 필요할 때 `loader`에게 요청합니다.
* **`get_sido_monthly_volume/area`**:
    * `Loader`로부터 원본 'Wide' 포맷 데이터를 받아, 사용자가 요청한 `sidos` (시도 목록)로 필터링하여 반환합니다.
* **`get_monthly_volume_and_area` (핵심 로직)**:
    1.  `Loader`로부터 '거래량(volume)'과 '거래면적(area)' 데이터를 각각 로드합니다.
    2.  `sidos` 인자가 있으면 우선 이 기준으로 데이터를 필터링합니다.
    3.  **데이터 형식 통일 (Date Normalization):**
        * '거래량' 데이터의 월 컬럼(`1월`, `2월`...)과 '거래면적' 데이터의 월 컬럼(`2020-01`, `2020-02`...)은 형식이 다릅니다.
        * '면적' 데이터의 컬럼명(`2020-01_면적`)에서 기준 연도(`'2020'`)를 추출합니다.
        * '거래량' 데이터의 `1월`을 `'2020-01'` 형식으로 변환합니다.
        * '면적' 데이터의 `2020-01_면적`을 `'2020-01'` 형식으로 변환합니다.
    4.  **데이터 병합 (Merge):** 형식이 통일된 `시도`와 `월(YYYY-MM)`을 기준으로 두 데이터를 병합(merge)하여 'Long' 포맷의 DataFrame을 생성합니다.
    5.  **필터링:** 사용자가 `start_m='1월'` 또는 `end_m='2020-03'`처럼 입력해도, 내부에서 `'2020-01'`, `'2020-03'` 형식으로 자동 변환하여 날짜 범위 필터링을 수행합니다.
    6.  결과를 `List[Dict]` 형태로 변환하여 반환합니다.

## 💡 사용 방법

라이브러리를 사용하는 방법은 2가지입니다.

### 방법 1: 간편 API (권장)

`py/__init__.py`에 정의된 `create_analyzer` 편의 함수를 사용하는 것이 가장 간단합니다. 이 함수는 `Config`, `Loader`, `Analyzer` 생성을 자동으로 처리해 줍니다.

**예시 (`test.py`의 `test_simple_api` 참고):**

```python
from pathlib import Path
from py import create_analyzer

# 1. 데이터 디렉토리 경로 설정
# (py/ 상위 폴더의 'data' 디렉토리를 기본값으로 사용)
data_dir = Path(__file__).parent / 'data'
analyzer = create_analyzer(str(data_dir))

# 2. 전체 데이터 조회 (Long 포맷)
# '시도', '월', '거래호수', '거래면적(천㎡)' 키를 가짐
all_data = analyzer.get_monthly_volume_and_area()
print(f"전체 월별 데이터: {len(all_data)}건")

# 3. 필터링 조회
# (날짜 형식은 '1월' 또는 '2020-01' 모두 가능)
filtered_data = analyzer.get_monthly_volume_and_area(
    sidos=['서울특별시', '부산광역시'],
    start_m='1월',
    end_m='3월'
)
print(f"필터링된 데이터: {len(filtered_data)}건")

from pathlib import Path
from py.config.settings import AnalysisConfig
from py.core.loader import DataLoader
from py.core.analyzer import RealEstateAnalyzer

# 1. Config 수동 생성
config = AnalysisConfig(
    data_dir=Path(__file__).parent / 'data',
    volume_filename='다른_거래량_파일.csv', # 파일명 변경 가능
    encoding='utf-8-sig'
)

# 2. Loader 및 Analyzer 수동 주입
loader = DataLoader(config)
analyzer = RealEstateAnalyzer(loader)

# 3. 원본 Wide 포맷 데이터 조회 (필터링)
volume_wide = analyzer.get_sido_monthly_volume(
    sidos=['광주광역시', '제주특별자치도']
)
print(f"Wide 포맷 데이터: {len(volume_wide)}개 시도")

# 4. Loader 캐시 제어
# 캐시가 아닌 실제 파일에서 강제로 다시 로드
loader.load_volume_data(force_reload=True)
print("데이터 강제 리로드 완료")
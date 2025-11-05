# -*- coding: utf-8 -*-
"""
아파트 거래 데이터 시각화 Flask 애플리케이션
- PEP 8 스타일 가이드 준수
- 동적 라우팅 방식으로 확장성 극대화
"""

from flask import Flask, render_template, jsonify, send_from_directory
import pandas as pd
import sys
import os


# ============================================
# 1. 데이터 가공 클래스
# ============================================
class Data:
    """
    CSV 데이터를 로드하고 다양한 집계 방식으로 가공하는 클래스
    """

    def __init__(self, file_path):
        """
        클래스 생성 시 CSV 파일을 로드하고 전처리합니다.

        :param file_path: CSV 파일 경로
        """
        self.df_origin = None

        try:
            # CSV 파일을 utf-8 인코딩으로 로드
            self.df_origin = pd.read_csv(file_path, encoding='utf-8')
            print(f"--- '{file_path}' (UTF-8) 로드 성공 ---")

            # 데이터 로드 성공 시 즉시 전처리 실행
            self.preprocess()

        except FileNotFoundError:
            print(
                f"치명적 오류: '{file_path}' 파일을 찾을 수 없습니다."
            )
            print(
                f"'app.py'와 '{file_path}' 파일이 같은 폴더에 "
                "있는지 확인하세요."
            )
            sys.exit()
        except Exception as e:
            print(f"CSV 로드 중 치명적 오류: {e}")
            print(
                "(해결책) CSV 파일을 VS Code로 열고 "
                "'Save with Encoding' -> 'UTF-8'로 다시 저장하세요."
            )
            sys.exit()

    def preprocess(self):
        """
        로드된 DataFrame을 전처리합니다.
        (datetime 변환, 컬럼명 변경 등)
        """
        try:
            # 거래금액 컬럼 전처리 (콤마 제거 후 숫자 변환)
            if ('거래금액' in self.df_origin.columns and
                    self.df_origin['거래금액'].dtype == 'object'):
                self.df_origin['거래금액'] = (
                    self.df_origin['거래금액']
                    .str.replace(',', '')
                    .astype(int)
                )

            # '법정동' -> '시도' 컬럼 생성
            if '법정동' in self.df_origin.columns:
                self.df_origin['시도'] = self.df_origin['법정동']
            else:
                raise KeyError("로드된 CSV에 '법정동' 컬럼이 없습니다.")

            # '거래일' datetime 변환
            if '거래일' in self.df_origin.columns:
                self.df_origin['거래일'] = pd.to_datetime(
                    self.df_origin['거래일']
                )
            else:
                raise KeyError("로드된 CSV에 '거래일' 컬럼이 없습니다.")

        except KeyError as e:
            print(f"전처리 중 치명적 오류: {e}")
            sys.exit()

    def create_json_response(self, key_name, records):
        """
        데이터를 JSON 형식으로 래핑하여 반환합니다.

        :param key_name: JSON의 최상위 키
        :param records: 데이터 리스트
        :return: Flask jsonify 응답
        """
        if records is None or len(records) == 0:
            return jsonify({key_name: []})
        return jsonify({key_name: records})

    # ----------------------------------------
    # 기간별 데이터 API 메소드
    # ----------------------------------------

    def get_data_floor(self):
        """층별 거래금액 합계"""
        df_temp = self.df_origin.copy()
        df_processed = (
            df_temp.groupby('층')['거래금액']
            .sum()
            .reset_index()
        )
        df_processed = df_processed.rename(columns={'층': '구분'})
        records = df_processed.to_dict('records')
        return self.create_json_response("층별", records)

    def get_data_daily(self):
        """일간 평균거래가 및 거래량"""
        df_temp = self.df_origin.copy()
        df_temp['일'] = (
            df_temp['거래일']
            .dt.to_period('D')
            .astype(str)
        )
        df_processed = df_temp.groupby('일').agg(
            평균거래가=('거래금액', 'mean'),
            거래량=('거래금액', 'count')
        ).reset_index()
        df_processed = df_processed.rename(columns={'일': '거래일'})
        records = df_processed.to_dict('records')
        return self.create_json_response("일간", records)

    def get_data_weekly(self):
        """주간 평균거래가 및 거래량"""
        df_temp = self.df_origin.copy()
        df_temp['주차'] = (
            df_temp['거래일']
            .dt.to_period('W')
            .astype(str)
        )
        df_processed = df_temp.groupby('주차').agg(
            평균거래가=('거래금액', 'mean'),
            거래량=('거래금액', 'count')
        ).reset_index()
        records = df_processed.to_dict('records')
        return self.create_json_response("주간", records)

    def get_data_monthly(self):
        """월간 평균거래가 및 거래량"""
        df_temp = self.df_origin.copy()
        df_temp['년월'] = (
            df_temp['거래일']
            .dt.to_period('M')
            .astype(str)
        )
        df_processed = df_temp.groupby('년월').agg(
            평균거래가=('거래금액', 'mean'),
            거래량=('거래금액', 'count')
        ).reset_index()
        records = df_processed.to_dict('records')
        return self.create_json_response("월간", records)

    def get_data_yearly(self):
        """년간 평균거래가 및 거래량"""
        df_temp = self.df_origin.copy()
        df_temp['년'] = df_temp['거래일'].dt.year.astype(str)
        df_processed = df_temp.groupby('년').agg(
            평균거래가=('거래금액', 'mean'),
            거래량=('거래금액', 'count')
        ).reset_index()
        records = df_processed.to_dict('records')
        return self.create_json_response("년간", records)

    # ----------------------------------------
    # 지역별 데이터 API 메소드
    # ----------------------------------------

    def get_data_apt_volume(self):
        """지역별 아파트 거래량"""
        df_processed = (
            self.df_origin
            .groupby('시도')
            .size()
            .reset_index(name="거래량")
        )
        records = df_processed.to_dict('records')
        return self.create_json_response("아파트 거래량", records)

    def get_data_apt_area(self):
        """지역별 평균 전용면적"""
        df_processed = (
            self.df_origin
            .groupby('시도')['전용면적']
            .mean()
            .reset_index()
        )
        records = df_processed.to_dict('records')
        return self.create_json_response("아파트 거래 면적", records)

    # ----------------------------------------
    # 월별 통합 데이터 API 메소드
    # ----------------------------------------

    def get_monthly_apt_volume(self):
        """월별 지역별 아파트 거래량"""
        df_temp = self.df_origin.copy()
        df_temp['년월'] = (
            df_temp['거래일']
            .dt.to_period('M')
            .astype(str)
        )

        # 년월별, 시도별 거래량 집계
        df_processed = (
            df_temp
            .groupby(['년월', '시도'])
            .size()
            .reset_index(name='거래량')
        )

        # 피벗 테이블로 변환 (년월을 행, 시도를 컬럼으로)
        df_pivot = (
            df_processed
            .pivot(index='년월', columns='시도', values='거래량')
            .fillna(0)
        )
        df_pivot = df_pivot.reset_index()

        # 컬럼명을 '년월', '서울', '부산' 등으로 정리
        df_pivot.columns.name = None

        records = df_pivot.to_dict('records')
        return self.create_json_response("월별 아파트 거래량", records)

    def get_monthly_apt_area(self):
        """월별 지역별 평균 전용면적"""
        df_temp = self.df_origin.copy()
        df_temp['년월'] = (
            df_temp['거래일']
            .dt.to_period('M')
            .astype(str)
        )

        # 년월별, 시도별 평균 전용면적 집계
        df_processed = (
            df_temp
            .groupby(['년월', '시도'])['전용면적']
            .mean()
            .reset_index()
        )

        # 피벗 테이블로 변환
        df_pivot = (
            df_processed
            .pivot(index='년월', columns='시도', values='전용면적')
            .fillna(0)
        )
        df_pivot = df_pivot.reset_index()
        df_pivot.columns.name = None

        records = df_pivot.to_dict('records')
        return self.create_json_response("월별 아파트 거래 면적", records)

    def get_monthly_apt_volume_area(self):
        """월별 지역별 거래량 + 면적 통합"""
        df_temp = self.df_origin.copy()
        df_temp['년월'] = (
            df_temp['거래일']
            .dt.to_period('M')
            .astype(str)
        )

        # 거래량과 평균면적을 동시에 집계
        df_processed = df_temp.groupby(['년월', '시도']).agg(
            거래량=('거래금액', 'count'),
            평균면적=('전용면적', 'mean')
        ).reset_index()

        records = df_processed.to_dict('records')
        return self.create_json_response(
            "월별 아파트 거래 거래량 면적",
            records
        )


# ============================================
# 2. Flask 앱 초기화
# ============================================
app = Flask(
    __name__,
    template_folder='html',
    static_folder=None  # 수동으로 정적 파일 처리
)


# ============================================
# 3. 데이터 로드 (서버 시작 전 1회 실행)
# ============================================
print("--- 데이터 로드를 시작합니다... ---")
data = Data('Apart Deal2020.csv')
print("--- 데이터 로드 및 전처리 완료 ---")


# ============================================
# 4. 라우트 정의
# ============================================

@app.route('/')
def index():
    """메인 페이지 (메뉴) 렌더링"""
    return render_template("index.html")


# ----------------------------------------
# 동적 페이지 라우팅 (확장성 우선)
# ----------------------------------------

@app.route('/<page>')
def show_page(page):
    """
    동적으로 페이지를 렌더링합니다.
    예: /day -> day.html, /week -> week.html

    :param page: 요청된 페이지 이름
    :return: HTML 템플릿 또는 404 에러
    """
    file_path = os.path.join('html', f'{page}.html')

    if os.path.exists(file_path):
        try:
            return render_template(f'{page}.html')
        except Exception as e:
            print(f"Template 렌더링 오류: {e}")
            return f"'{page}.html' 렌더링 중 오류가 발생했습니다.", 500
    else:
        return f"'{page}' 페이지를 찾을 수 없습니다.", 404


# ----------------------------------------
# 정적 파일 서빙
# ----------------------------------------

@app.route('/favicon.ico')
def serve_favicon():
    """
    브라우저 탭 아이콘(favicon)을 제공합니다.
    파일이 없으면 204 No Content 반환하여 404 에러 방지

    :return: favicon.ico 파일 또는 204
    """
    favicon_path = os.path.join('static', 'favicon.ico')

    if os.path.exists(favicon_path):
        return send_from_directory(
            'static',
            'favicon.ico',
            mimetype='image/x-icon'
        )
    else:
        # 파일이 없어도 에러 표시 안 함
        return '', 204


@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    정적 파일(CSS, 이미지 등)을 제공합니다.

    :param filename: 요청된 정적 파일명
    :return: 정적 파일 또는 404
    """
    try:
        return send_from_directory('static', filename)
    except Exception as e:
        print(f"정적 파일 로드 오류: {e}")
        return "정적 파일을 찾을 수 없습니다.", 404


@app.route('/js/<path:filename>')
def serve_js(filename):
    """
    JavaScript 파일을 제공합니다.

    :param filename: 요청된 JS 파일명
    :return: JS 파일 또는 404
    """
    try:
        return send_from_directory('js', filename)
    except Exception as e:
        print(f"JS 파일 로드 오류: {e}")
        return "JS 파일을 찾을 수 없습니다.", 404


@app.route('/data/<path:filename>')
def serve_data(filename):
    """
    데이터 파일을 제공합니다.

    :param filename: 요청된 데이터 파일명
    :return: 데이터 파일 또는 404
    """
    try:
        return send_from_directory('data', filename)
    except Exception as e:
        print(f"데이터 파일 로드 오류: {e}")
        return "데이터 파일을 찾을 수 없습니다.", 404


# ----------------------------------------
# JSON API 엔드포인트 (기간별)
# ----------------------------------------

@app.route('/py/층별.json')
def api_floor():
    """층별 거래금액 합계 API"""
    return data.get_data_floor()


@app.route('/py/일간.json')
def api_daily():
    """일간 평균거래가 및 거래량 API"""
    return data.get_data_daily()


@app.route('/py/주간.json')
def api_weekly():
    """주간 평균거래가 및 거래량 API"""
    return data.get_data_weekly()


@app.route('/py/월간.json')
def api_monthly():
    """월간 평균거래가 및 거래량 API"""
    return data.get_data_monthly()


@app.route('/py/년간.json')
def api_yearly():
    """년간 평균거래가 및 거래량 API"""
    return data.get_data_yearly()


# ----------------------------------------
# JSON API 엔드포인트 (지역별)
# ----------------------------------------

@app.route('/py/아파트 거래량.json')
def api_apt_volume():
    """지역별 아파트 거래량 API"""
    return data.get_data_apt_volume()


@app.route('/py/아파트 거래 면적.json')
def api_apt_area():
    """지역별 평균 전용면적 API"""
    return data.get_data_apt_area()


# ----------------------------------------
# JSON API 엔드포인트 (월별 통합)
# ----------------------------------------

@app.route('/py/월별 아파트 거래량.json')
def api_monthly_apt_volume():
    """월별 지역별 아파트 거래량 API"""
    return data.get_monthly_apt_volume()


@app.route('/py/월별 아파트 거래 면적.json')
def api_monthly_apt_area():
    """월별 지역별 평균 전용면적 API"""
    return data.get_monthly_apt_area()


@app.route('/py/월별 아파트 거래 거래량 면적.json')
def api_monthly_apt_volume_area():
    """월별 지역별 거래량+면적 통합 API"""
    return data.get_monthly_apt_volume_area()


# ============================================
# 5. 서버 실행
# ============================================
if __name__ == "__main__":
    app.run(
        host="192.168.219.50",
        port=5000,
        debug=True
    )
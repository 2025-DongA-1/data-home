/**********************************************************************
 * Chart.js - JSON 데이터를 불러와 표 + 그래프 표시
 * 모든 컬럼(숫자형 데이터)을 자동으로 그래프에 표시
 * 2025-11 버전 (줄마다 상세 주석 포함)
 **********************************************************************/

// ==============================================
// ① 불러올 JSON 파일 목록 정의
// ==============================================
const jsonFiles = [
    "../py/층별.json",            // 층별 거래 데이터
    "../py/일간.json",            // 일간 거래 데이터
    "../py/주간.json",            // 주간 거래 데이터
    "../py/월간.json",            // 월간 거래 데이터
    //"../py/년간.json",             년간 거래 데이터

    "../py/아파트 거래량.json",    // 지역별 아파트 거래량 데이터
    "../py/아파트 거래 면적.json"   // 지역별 아파트 거래량 면적 데이터
];

// ==============================================
// ② 각 JSON 파일을 순차적으로 불러오기 (for문)
// ==============================================
for (let i = 0; i < jsonFiles.length; i++) {   // 배열 길이만큼 반복
    const file = jsonFiles[i];                   // 현재 파일 이름 저장

    // fetch()로 JSON 파일을 비동기 요청
    fetch(file)
        .then(res => res.json())                   // 응답을 JSON 형식으로 변환
        .then(data => {
            // ======================================
            // ③ JSON 내부 구조 파악
            //    { "일간": [ {...}, {...} ] } 형태
            // ======================================
            const key = Object.keys(data)[0];        // 첫 번째 키 이름 추출 ("일간" 등)
            const records = data[key];               // 데이터 배열 부분만 가져오기



            // ======================================
            // ④ HTML 카드 구조 생성 (표 + 그래프)
            // ======================================
            let html = `<div class="card">`;                             // 카드 시작
            html += `<h2>${key} (${records.length}건)</h2>`;              // 제목과 건수 표시
            html += `<div class="chart-area"><canvas id="chart-${i}"></canvas></div>`; // 그래프용 캔버스
            html += `<div class="table-container"><table><thead><tr>`;    // 표 시작

            // ======================================
            // ⑤ 표 헤더(컬럼명) 생성
            // ======================================
            const headers = Object.keys(records[0]);                     // 첫 번째 행의 컬럼명 추출
            for (let j = 0; j < headers.length; j++) {                   // 모든 컬럼명 반복
                html += `<th>${headers[j]}</th>`;                          // <th>로 헤더 생성
            }
            html += `</tr></thead><tbody>`;                              // 헤더 종료 및 바디 시작

            // ======================================
            // ⑥ 표 내용(데이터 행) 생성
            // ======================================
            for (let r = 0; r < records.length; r++) {                   // 각 데이터 행 반복
                html += `<tr>`;                                            // 행 시작
                for (let c = 0; c < headers.length; c++) {                 // 각 컬럼 반복
                    const value = records[r][headers[c]];                    // 현재 셀 값
                    html += `<td>${value}</td>`;                             // 표 셀에 값 출력
                }
                html += `</tr>`;                                           // 행 종료
            }
            html += `</tbody></table></div>`;                            // 표 종료
            html += `<div class="table-status">총 ${records.length}건</div>`; // 상태 표시줄
            html += `</div>`;                                            // 카드 종료

            // ======================================
            // ⑦ 완성된 HTML을 페이지에 추가
            //    innerHTML += 대신 insertAdjacentHTML 사용
            //    (기존 DOM 유지 및 그래프 덮어쓰기 방지)
            // ======================================
            document
                .getElementById("container")                               // container 요소 선택
                .insertAdjacentHTML("beforeend", html);                    // 새 카드 HTML 뒤에 추가

            // ======================================
            // ⑧ Chart.js 그래프용 데이터 준비
            // ======================================
            labels = [];   // X축 라벨 배열

            if (key === "층별") {
                labels = records.map(r => r["구분"]);
            } else if (key === "주간") {
                labels = records.map(r => r["주차"]);
            } else if (key === "아파트 거래량") {
                labels = records.map(r => r["시도"]);
            } else if (key === "아파트 거래 면적") {
                labels = records.map(r => r["시도"]);
            } else {
                // 기본값 — 거래일, 년월, 년 중 하나 사용
                labels = records.map(r =>
                    r["거래일"] || r["년월"] || r["년"] || `#${records.indexOf(r) + 1}`
                );

            }

            /* // 날짜나 년월, 년 등의 컬럼명을 기준으로 라벨 구성
            for (let n = 0; n < records.length; n++) {
                const item = records[n];                                   // 현재 행 데이터
                labels.push(
                    item["거래일"] ||                                        // "거래일"이 있으면 사용
                    item["년월"] ||                                          // 없으면 "년월" 사용
                    item["년"] ||                                            // 없으면 "년" 사용
                    `#${n + 1}`                                              // 그래도 없으면 순번 사용
                );
            }
                */

            // ======================================
            // ⑨ 그래프 색상 팔레트 정의 (파스텔톤)
            // ======================================
            const colorList = [
                "#ff6384", "#36a2eb", "#ff9f40",
                "#4bc0c0", "#9966ff", "#c9cbcf",
                "#8bc34a", "#f06292", "#64b5f6"
            ];

            // ======================================
            // ⑩ Chart.js 데이터셋(datasets) 생성
            //    → 모든 컬럼을 자동으로 탐색해서
            //      숫자형 컬럼만 그래프에 추가
            // ======================================
            const datasets = [];                                         // 데이터셋 배열 초기화
            let colorIndex = 0;                                          // 색상 순서 인덱스

            for (let j = 0; j < headers.length; j++) {                   // 각 컬럼 순회
                const col = headers[j];                                    // 컬럼 이름
                const firstValue = records[0][col];                        // 첫 번째 행의 값으로 타입 판별

                // 숫자형 데이터만 그래프에 표시
                if (typeof firstValue === "number") {
                    const colData = [];                                      // 현재 컬럼의 값 배열
                    for (let r = 0; r < records.length; r++) {               // 모든 행 반복
                        colData.push(records[r][col]);                         // 각 행의 숫자값 저장
                    }

                    // 하나의 데이터셋 객체 생성
                    datasets.push({
                        label: col,                                            // 범례 라벨명
                        data: colData,                                         // 값 배열
                        borderColor: colorList[colorIndex % colorList.length], // 선 색상
                        backgroundColor: colorList[colorIndex % colorList.length], // 배경색
                        borderWidth: 2,                                        // 선 두께
                        fill: false,                                           // 면 채우기 비활성화
                        tension: 0.25                                          // 곡선 부드럽게
                    });

                    colorIndex++;                                            // 다음 컬러 사용 준비
                }
            }

            // ======================================
            // ⑪ Chart.js 그래프 생성
            // ======================================
            const ctx = document.getElementById(`chart-${i}`).getContext("2d"); // canvas 컨텍스트 가져오기
            new Chart(ctx, {
                type: "line",                                              // 그래프 유형 (꺾은선)
                data: {
                    labels: labels,                                          // X축 라벨 배열
                    datasets: datasets                                       // Y축에 표시할 데이터셋 전체
                },
                options: {
                    responsive: true,                                        // 반응형 활성화
                    maintainAspectRatio: false,                              // 비율 고정 해제 (높이 조절 가능)
                    plugins: {
                        legend: {                                              // 범례 설정
                            display: true,                                       // 표시 여부
                            position: "top"                                      // 상단 배치
                        },
                        tooltip: { enabled: true }                             // 마우스 오버 시 툴팁 표시
                    },
                    scales: {
                        x: {                                                   // X축 설정
                            title: { display: true, text: "기간" },               // X축 제목 표시
                            ticks: { autoSkip: true, maxTicksLimit: 20 }          // 라벨 개수 제한
                        },
                        y: {                                                   // Y축 설정
                            title: { display: true, text: "값" },                 // Y축 제목
                            ticks: {
                                // 숫자 단위 변환 (만, 억 단위로 보기 쉽게)
                                callback: function (value) {
                                    if (value >= 100000000)
                                        return (value / 100000000).toFixed(1) + "억";  // 1억 이상일 때
                                    if (value >= 10000)
                                        return (value / 10000).toFixed(0) + "만";      // 1만 이상일 때
                                    return value;                                    // 그 외는 그대로 표시
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(err => console.error(`${file} 로드 오류:`, err));        // 에러 발생 시 콘솔 출력
}

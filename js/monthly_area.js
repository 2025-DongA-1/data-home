// ==============================================
// JSON 파일 목록 정의 
// type: "bar", "line", "pie"
// (flip: 0=기본, 1=반전)
// ==============================================
const jsonFiles = [

        
    { file: "../py/월별 아파트 거래 면적.json", type: "line", flip: 1 }
];

// ==============================================
// ② 숫자 포맷 함수 (천 단위 구분, 소수점 2자리)
// ==============================================
/**********************************************************************
 * 숫자 포맷 함수 (천 단위 구분, 소수점 2자리)
 * - 예외 1: 컬럼명이 '년', '연도', '연', '년월'인 경우
 * - 예외 2: 값이 4자리 연도(예: 2020)
 * - 예외 3: 값이 연도.월 형태(예: 2020.01)
 **********************************************************************/
/**********************************************************************
 * 숫자 포맷 함수 (천 단위 구분, 소수점 2자리)
 * - 예외 1: 컬럼명이 '년', '연도', '연', '년월'인 경우
 * - 예외 2: 값이 4자리 연도(예: 2020)
 * - 예외 3: 값이 연도.월 형태(예: 2020.01)
 **********************************************************************/
function formatNumber(value, columnName = "") {

    // --- ① 컬럼명 예외 처리 ------------------------------------------------
    if (columnName) {                                       // 컬럼명이 전달된 경우
        const col = columnName.trim();                      // 앞뒤 공백 제거
        if (col.includes("년") ||                           // '년' 포함
            col.includes("연도") ||                         // '연도' 포함
            col.includes("연") ||                           // '연' 포함
            col.includes("년월")) {                         // '년월' 포함
            return value;                                   // 예외 컬럼은 그대로 반환
        }
    }

    // --- ② 문자열 형태일 경우 예외 패턴 먼저 검사 ----------------------------
    if (typeof value === "string") {                        // 문자열인 경우
        const str = value.trim();                           // 공백 제거

        // === (1) 연도.월 형태 (예: 2020.01) ===
        if (/^\d{4}\.\d{1,2}$/.test(str)) return str;

        // === (2) 4자리 연도 (예: 2020) ===
        if (/^\d{4}$/.test(str)) return str;
    }

    // --- ③ 숫자 판별 및 변환 ------------------------------------------------
    if (typeof value === "number" || (!isNaN(value) && value !== "")) {
        const num = parseFloat(value);                      // 숫자로 변환

        // --- ④ 4자리 연도 예외 --------------------------------------------
        if (Number.isInteger(num) && num >= 1000 && num <= 9999) {
            return num.toString();                          // 그대로 반환
        }

        // --- ⑤ 포맷 처리 (정수 / 소수 구분) -------------------------------
        if (num % 1 === 0) {                                // 정수인 경우
            return num.toLocaleString("ko-KR");             // 천 단위 구분 적용
        } else {                                            // 소수인 경우
            return num.toLocaleString("ko-KR", {            // 천 단위 + 소수점 자리
                minimumFractionDigits: 2,                   // 최소 소수점 2자리
                maximumFractionDigits: 2                    // 최대 소수점 2자리
            });
        }
    }

    // --- ⑥ 숫자가 아니면 그대로 반환 ----------------------------------------
    return value;                                           //
}

/*
function formatNumber(value) {
    if (typeof value === "number" || !isNaN(value)) {         // 숫자 또는 숫자형 문자열인지 확인
        const num = parseFloat(value);                          // 숫자로 변환
        return num % 1 === 0                                    // 정수라면
            ? num.toLocaleString("ko-KR")                         // 천 단위 구분
            : num.toLocaleString("ko-KR", {                       // 소수일 경우
                minimumFractionDigits: 2,                         // 소수점 최소 2자리
                maximumFractionDigits: 2,                         // 소수점 최대 2자리
            });
    }
    return value;                                             // 숫자 아니면 그대로 반환
}*/

// ==============================================
// ③ 각 JSON 파일을 순차적으로 로드 및 차트 생성
// ==============================================
for (let i = 0; i < jsonFiles.length; i++) {                // 파일 목록 반복
    const { file, type, flip } = jsonFiles[i];                // flip 값 포함 추출

    // fetch()로 JSON 파일 불러오기
    fetch(file)
        .then((res) => res.json())                              // JSON 객체로 변환
        .then((data) => {
            const key = Object.keys(data)[0];                     // 첫 번째 키 추출
            const records = data[key];                            // 키에 해당하는 데이터 배열
            if (!records || records.length === 0) return;         // 데이터 없으면 종료

            // ======================================
            // ④ HTML 카드 구조 생성
            // ======================================
            let html = `<div class="card">`;                      // 카드 시작
            html += `<h2>${key} (${records.length}건)</h2>`;      // 제목 표시
            html += `<div class="chart-area"><canvas id="chart-${i}"></canvas></div>`; // 차트 캔버스
            html += `<div class="table-container"><table><thead><tr>`;                // 표 시작

            const headers = Object.keys(records[0]);               // 컬럼명 추출
            for (let j = 0; j < headers.length; j++) {             // 컬럼 반복
                html += `<th>${headers[j]}</th>`;                    // 헤더 추가
            }
            html += `</tr></thead><tbody>`;                        // 헤더 종료

            // 표 본문 구성
            for (let r = 0; r < records.length; r++) {             // 행 반복
                html += `<tr>`;                                      // 행 시작
                for (let c = 0; c < headers.length; c++) {           // 열 반복
                    const value = records[r][headers[c]];              // 값 추출
                    html += `<td>${formatNumber(value)}</td>`;         // 셀 추가
                }
                html += `</tr>`;                                     // 행 종료
            }

            html += `</tbody></table></div>`;                      // 표 닫기
            html += `<div class="table-status" id="status-${i}">총 ${records.length}건 </div>`; // 상태 표시줄
            html += `</div>`;                                      // 카드 닫기

            // 완성된 카드 HTML 삽입
            document.getElementById("container").insertAdjacentHTML("beforeend", html);

            // ======================================
            // ⑤ 라벨 구성 (X축 라벨용)
            // ======================================
            let labels = [];                                       // 라벨 초기화
            if (key === "층별") labels = records.map((r) => r["구분"]);          // 층별 데이터
            else if (key === "주간") labels = records.map((r) => r["주차"]);     // 주간 데이터
            else if (key.includes("거래량") || key.includes("면적"))             // 거래 관련
                labels = records.map((r) => r["시도"]);                             // 시도 컬럼 사용
            else
                labels = records.map(                                               // 기본 라벨
                    (r) =>
                        r["거래일"] ||
                        r["년월"] ||
                        r["연도"] ||
                        r["년도"] ||
                        r["년"] ||
                        r["시도"] ||
                        `#${records.indexOf(r) + 1}`
                );

            // ======================================
            // ⑥ 색상 팔레트 정의
            // ======================================
            const colorList = [
                "#ff6384", "#36a2eb", "#ff9f40", "#4bc0c0", "#9966ff",
                "#c9cbcf", "#8bc34a", "#f06292", "#64b5f6", "#FFFACD",
                "#808000", "#A52A2A"
            ];

            // ======================================
            // ⑦ 데이터셋 구성
            // ======================================
            const datasets = [];
            let colorIndex = 0;
            for (let j = 0; j < headers.length; j++) {             // 컬럼 반복
                const col = headers[j];
                const firstValue = records[0][col];
                if (!isNaN(parseFloat(firstValue))) {                // 숫자형 컬럼만 포함
                    const colData = records.map((r) => parseFloat(r[col]) || 0);
                    datasets.push({
                        label: col,                                      // 범례 이름
                        data: colData,                                   // 데이터 배열
                        backgroundColor: colorList[colorIndex % colorList.length],
                        borderColor: colorList[colorIndex % colorList.length],
                        borderWidth: 2,
                        borderRadius: type === "bar" ? 10 : 0,
                        borderSkipped: false,
                        fill: type === "line" ? false : true,
                        tension: type === "line" ? 0.25 : 0,
                    });
                    colorIndex++;
                }
            }

            // ======================================
            // ⑧ Chart.js 차트 생성
            // ======================================
            const ctx = document.getElementById(`chart-${i}`).getContext("2d");
            const chart = new Chart(ctx, {
                type: type,
                data: { labels, datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: true, position: "top" },
                        tooltip: { enabled: true },
                    },
                    scales:
                        type === "pie" || type === "doughnut"
                            ? {}
                            : {
                                x: {
                                    title: { display: true, text: "기간" },
                                    ticks: { autoSkip: true, maxTicksLimit: 20 },
                                    grid: { display: false },
                                },
                                y: {
                                    title: { display: true, text: "값" },
                                    ticks: {
                                        callback: function (value) {
                                            if (value >= 100000000)
                                                return (value / 100000000).toFixed(1) + "억";
                                            if (value >= 10000)
                                                return (value / 10000).toFixed(0) + "만";
                                            return value;
                                        },
                                    },
                                    grid: { color: "rgba(0,0,0,0.1)" },
                                },
                            },
                },
            });

            // ======================================
            // ⑨ flip 값이 1이면 자동 반전 실행
            // ======================================
            if (flip === 1) {                                     // flip 설정값 확인
                flipChart(chart, headers, records, labels, colorList); // 반전 실행
                document.getElementById(`status-${i}`).dataset.flipped = "true"; // 상태 표시
                document.getElementById(`status-${i}`).textContent = `총 ${records.length}건`;
            }

            // ======================================
            // ⑩ 상태 표시줄 클릭 시 수동 전환
            // ======================================
            document.getElementById(`status-${i}`).addEventListener("click", function () {
                const isOriginal = !this.dataset.flipped;            // 현재 전환 상태 확인
                this.dataset.flipped = isOriginal ? "true" : "";     // 상태 반전
                if (isOriginal) {
                    flipChart(chart, headers, records, labels, colorList); // 반전 실행
                    this.textContent = `총 ${records.length}건 `;
                } else {
                    chart.data.labels = labels;                       // 원래 데이터 복원
                    chart.data.datasets = datasets;
                    chart.update();
                    this.textContent = `총 ${records.length}건 `;
                }
            });
        })
        .catch((err) => console.error(`${file} 로드 오류:`, err)); // 로드 오류 처리
}

// ==============================================
// ⑪ 행/열 전환용 공통 함수
// ==============================================
function flipChart(chart, headers, records, labels, colorList) {
    const newLabels = headers.filter((h) => !isNaN(records[0][h])); // 숫자형 컬럼만 라벨로 사용
    const newDatasets = [];                                         // 새로운 데이터셋 배열
    for (let r = 0; r < records.length; r++) {                      // 각 행 반복
        const row = records[r];
        const values = newLabels.map((col) => parseFloat(row[col]) || 0);
        const labelCandidates = [                                     // 이름 후보 목록
            "시도",  "구분", "항목", "규모", "기간",
            "거래일", "년월", "연도", "년도", "년"
        ];
        let name = null;
        for (let k = 0; k < labelCandidates.length; k++) {
            if (row[labelCandidates[k]]) {
                name = row[labelCandidates[k]];
                break;
            }
        }
        if (!name && labels[r]) name = labels[r];                     // 기존 라벨 사용
        if (!name) name = `행${r + 1}`;                               // 없으면 행번호 사용
        newDatasets.push({                                            // 데이터셋 추가
            label: name,
            data: values,
            backgroundColor: colorList[r % colorList.length],
            borderColor: colorList[r % colorList.length],
            borderWidth: 2,
            borderRadius: 10,
            borderSkipped: false,
        });
    }
    chart.data.labels = newLabels;                                  // 라벨 교체
    chart.data.datasets = newDatasets;                              // 데이터 교체
    chart.update();                                                 // 차트 갱신
}

/**********************************************************************
 * Chart.js - JSON 데이터를 불러와 표 + 막대 그래프 표시
 * 모든 컬럼(숫자형 데이터)을 자동으로 그래프에 표시
 * 2025-11 버전 (막대 그래프 적용 + 줄마다 상세 주석)
 **********************************************************************/

// ==============================================
// ① 불러올 JSON 파일 목록 정의
// ==============================================
const jsonFiles = [
    "../py/면적.json"            // 예시 JSON 파일 (면적 데이터)
];

// ==============================================
// 숫자 포맷 함수 정의 (천 단위 콤마 + 소수점 2자리)
// ==============================================
function formatNumber(value) {
    if (typeof value === "number") {
        return value % 1 === 0
            ? value.toLocaleString("ko-KR")
            : value.toLocaleString("ko-KR", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
    }
    return value;
}

// ==============================================
// ② JSON 파일을 순차적으로 불러오기
// ==============================================
for (let i = 0; i < jsonFiles.length; i++) {
    const file = jsonFiles[i]; // 현재 파일명

    fetch(file)
        .then(res => res.json()) // JSON 형식으로 파싱
        .then(data => {
            // ======================================
            // ③ JSON 구조 파악 ("면적": [ {...}, {...} ])
            // ======================================
            const key = Object.keys(data)[0];  // "면적" 등
            const records = data[key];         // 실제 배열 데이터

            // ======================================
            // ④ HTML 구조 (표 + 그래프 영역)
            // ======================================
            let html = `<div class="card">`;
            html += `<h2>${key} (${records.length}건)</h2>`;
            html += `<div class="chart-area"><canvas id="chart-${i}"></canvas></div>`;
            html += `<div class="table-container"><table><thead><tr>`;

            // ======================================
            // ⑤ 표 헤더 생성
            // ======================================
            const headers = Object.keys(records[0]);
            for (let j = 0; j < headers.length; j++) {
                html += `<th>${headers[j]}</th>`;
            }
            html += `</tr></thead><tbody>`;

            // ======================================
            // ⑥ 표 데이터 행 생성
            // ======================================
            for (let r = 0; r < records.length; r++) {
                html += `<tr>`;
                for (let c = 0; c < headers.length; c++) {
                    const value = records[r][headers[c]];
                    html += `<td>${formatNumber(value)}</td>`;
                }
                html += `</tr>`;
            }
            html += `</tbody></table></div>`;
            html += `<div class="table-status">총 ${records.length}건</div>`;
            html += `</div>`;

            // ======================================
            // ⑦ 완성된 HTML을 container에 추가
            // ======================================
            document
                .getElementById("container")
                .insertAdjacentHTML("beforeend", html);

            // ======================================
            // ⑧ X축 라벨 정의
            // ======================================
            let labels = [];
            if (key === "면적") labels = records.map(r => r["규모"]);
            else if (key === "주간") labels = records.map(r => r["주차"]);
            else if (key === "아파트 거래량") labels = records.map(r => r["시도"]);
            else if (key === "아파트 거래 면적") labels = records.map(r => r["시도"]);
            else
                labels = records.map(r =>
                    r["거래일"] || r["년월"] || r["년"] || `#${records.indexOf(r) + 1}`
                );

            // ======================================
            // ⑨ 색상 팔레트 정의
            // ======================================
            const colorList = [
                "#ff6384", "#36a2eb", "#ff9f40",
                "#4bc0c0", "#9966ff", "#c9cbcf",
                "#8bc34a", "#f06292", "#64b5f6",
                "#FFFACD", "#808000", "#A52A2A"
            ];

            // ======================================
            // ⑩ Chart.js 데이터셋 생성 (숫자형 컬럼만)
            // ======================================
            const datasets = [];
            let colorIndex = 0;

            for (let j = 0; j < headers.length; j++) {
                const col = headers[j];
                const firstValue = records[0][col];

                // 숫자형 데이터만 그래프에 포함
                if (typeof firstValue === "number") {
                    const colData = records.map(r => r[col]); // 값 배열
                    datasets.push({
                        label: col,                                            // 범례 이름
                        data: colData,                                         // Y축 데이터
                        backgroundColor: colorList[colorIndex % colorList.length], // 막대 색상
                        borderColor: colorList[colorIndex % colorList.length], // 테두리 색상
                        borderWidth: 2,                                        // 테두리 두께
                        borderRadius: 8,                                       // 막대 둥근 모서리
                        borderSkipped: false,                                  // 하단도 둥글게
                        barThickness: 30                                       // 막대 두께 조정
                    });
                    colorIndex++;
                }
            }

            // ======================================
            // ⑪ Chart.js 막대 그래프 생성
            // ======================================
            const ctx = document.getElementById(`chart-${i}`).getContext("2d");
            new Chart(ctx, {
                type: "bar", // ✅ 막대 그래프로 변경
                data: {
                    labels: labels,  // X축 라벨
                    datasets: datasets // 데이터셋 전체
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: true, position: "top" },
                        tooltip: { enabled: true }
                    },
                    scales: {
                        x: {
                            title: { display: true, text: "기간" },
                            ticks: { autoSkip: true, maxTicksLimit: 20 }
                        },
                        y: {
                            title: { display: true, text: "값" },
                            ticks: {
                                // 숫자 단위 축약 표시
                                callback: function (value) {
                                    if (value >= 100000000)
                                        return (value / 100000000).toFixed(1) + "억";
                                    if (value >= 10000)
                                        return (value / 10000).toFixed(0) + "만";
                                    return value;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(err => console.error(`${file} 로드 오류:`, err));
}

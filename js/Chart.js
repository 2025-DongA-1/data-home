/***********************************************************************
 * 아파트 거래 데이터 시각화 Chart.js
 * - result.json 파일을 불러와 년/월/주/일 단위로 표 + 그래프 표시
 * - 각 구간별 데이터(합계, 평균, 최대, 최소, 거래건수)를 파스텔톤으로 시각화
 * - for문 중심으로 단순화된 버전
 ***********************************************************************/

// JSON 데이터 불러오기
fetch("../py/result.json") // py 폴더 안의 result.json 경로
    .then(res => res.json()) // 응답을 JSON 형식으로 변환
    .then(data => {
        // 표시할 구간 목록 (년, 월, 주, 일)
        const sections = [
            ["년간", "year"],
            ["월간", "month"],
            ["주간", "week"],
            ["일간", "day"]
        ];

        // 각 구간별로 반복 렌더링
        for (let i = 0; i < sections.length; i++) {
            const [labelText, idPrefix] = sections[i]; // 구조분해 할당
            renderSection(data[labelText], idPrefix, labelText);
        }
    })
    .catch(err => console.error("JSON 로드 오류:", err)); // 에러 처리


/***********************************************************************
 * renderSection()
 * - 각 구간(년, 월, 주, 일)별 표와 그래프 렌더링 함수
 ***********************************************************************/
function renderSection(sectionData, idPrefix, labelText) {
    // HTML 요소 가져오기
    const tableHead = document.querySelector(`#table-${idPrefix} thead`);
    const tableBody = document.querySelector(`#table-${idPrefix} tbody`);
    const statusBox = document.querySelector(`#status-${idPrefix}`);

    // ==========================
    // 표 헤더 구성
    // ==========================
    const headers = Object.keys(sectionData[0]); // 첫 번째 행의 열 이름 가져오기
    let headHTML = "<tr>";
    for (let i = 0; i < headers.length; i++) {
        headHTML += `<th>${headers[i]}</th>`;
    }
    headHTML += "</tr>";
    tableHead.innerHTML = headHTML;

    // ==========================
    // 표 내용 구성
    // ==========================
    let bodyHTML = "";
    for (let i = 0; i < sectionData.length; i++) {
        let rowHTML = "<tr>";
        for (let j = 0; j < headers.length; j++) {
            rowHTML += `<td>${sectionData[i][headers[j]]}</td>`;
        }
        rowHTML += "</tr>";
        bodyHTML += rowHTML;
    }
    tableBody.innerHTML = bodyHTML;

    // ==========================
    // 상태 표시줄
    // ==========================
    const totalRows = sectionData.length;
    const visibleRows = Math.min(totalRows, 12);
    statusBox.textContent = `총 ${totalRows}건 `;

    // ==========================
    // 차트 데이터 준비
    // ==========================
    const labels = [];   // 날짜 or 년월
    const sumData = [];  // 합계
    const avgData = [];  // 평균
    const maxData = [];  // 최대
    const minData = [];  // 최소
    const cntData = [];  // 거래건수

    // 각 데이터 행에서 값 추출
    for (let i = 0; i < sectionData.length; i++) {
        const item = sectionData[i];
        labels.push(item["거래일"] || item["년월"] || item["년"]);
        sumData.push(item["합계"]);
        avgData.push(item["평균"]);
        maxData.push(item["최대"]);
        minData.push(item["최소"]);
        cntData.push(item["거래건수"]);
    }

    // ==========================
    // 색상 팔레트 (파스텔톤)
    // ==========================
    const colors = {
        sum: "#a3c9a8", // 연한 초록
        avg: "#9ab7d3", // 연한 파랑
        max: "#f6c1b2", // 연한 코랄
        min: "#f3d9b1", // 연한 베이지
        cnt: "#e0b0d5"  // 연한 보라
    };

    // ==========================
    // Chart.js 그래프 생성
    // ==========================
    const ctx = document.getElementById(`chart-${idPrefix}`).getContext("2d");

    // 그래프 항목 정의
    const datasets = [
        { label: "합계", data: sumData, color: colors.sum, axis: "y" },
        { label: "평균", data: avgData, color: colors.avg, axis: "y" },
        { label: "최대", data: maxData, color: colors.max, axis: "y" },
        { label: "최소", data: minData, color: colors.min, axis: "y" },
        { label: "거래건수", data: cntData, color: colors.cnt, axis: "y2" }
    ];

    // 데이터셋 변환 (for문 사용)
    const chartDatasets = [];
    for (let i = 0; i < datasets.length; i++) {
        chartDatasets.push({
            label: datasets[i].label,
            data: datasets[i].data,
            borderColor: datasets[i].color,
            backgroundColor: datasets[i].color,
            borderWidth: 2,
            fill: false,
            yAxisID: datasets[i].axis
        });
    }

    // ==========================
    // 차트 생성
    // ==========================
    new Chart(ctx, {
        type: "line", // 꺾은선 그래프
        data: {
            labels: labels,       // X축 값
            datasets: chartDatasets // Y축 데이터
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: { display: true, position: "top" },
                tooltip: { enabled: true }
            },
            scales: {
                // X축 설정
                x: {
                    title: { display: true, text: "날짜" },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 30,
                        autoSkip: true,
                        maxTicksLimit: 15
                    }
                },
                // 왼쪽 Y축 (금액)
                y: {
                    position: "left",
                    grace: "10%",
                    title: { display: true, text: "금액(단위: 원)" },
                    ticks: {
                        callback: function (value) {
                            if (value >= 100000000) return (value / 100000000).toFixed(1) + "억";
                            if (value >= 10000) return (value / 10000).toFixed(0) + "만";
                            return value;
                        }
                    }
                },
                // 오른쪽 Y축 (거래건수)
                y2: {
                    position: "right",
                    grid: { drawOnChartArea: false },
                    grace: "10%",
                    title: { display: true, text: "거래건수(건)" },
                    ticks: {
                        callback: function (value) {
                            if (value >= 1000) return (value / 1000).toFixed(0) + "K";
                            return value;
                        }
                    }
                }
            }
        }
    });
}

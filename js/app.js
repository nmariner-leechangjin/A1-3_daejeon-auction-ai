const analyzeButton = document.getElementById("analyze-button");
const resultBox = document.getElementById("result-box");

const aiOpinionButton =
    document.getElementById("ai-opinion-button");

const aiOpinionBox =
    document.getElementById("ai-opinion-box");


// =====================================================
// 1. 기본 경매 분석
// =====================================================

analyzeButton.addEventListener("click", function () {

    const appraisalPrice =
        Number(document.getElementById("appraisal-price").value);

    const minimumPrice =
        Number(document.getElementById("minimum-price").value);

    const failedCount =
        Number(document.getElementById("failed-count").value);

    const views =
        Number(document.getElementById("views").value);

    const kbPrice =
        Number(document.getElementById("kb-price").value);


    // 필수값 확인
    if (!appraisalPrice || !minimumPrice || !kbPrice) {

        resultBox.innerHTML =
            "감정가, 최저가, KB시세를 모두 입력해주세요.";

        return;
    }


    // 감정가 대비 최저가 비율
    const appraisalRate =
        (minimumPrice / appraisalPrice) * 100;


    // KB시세 대비 최저가 비율
    const kbRate =
        (minimumPrice / kbPrice) * 100;


    // =================================================
    // 2. 조회수에 따른 경쟁도
    // =================================================

    let competition = "";
    let competitionRate = 0;

    if (views < 200) {

        competition = "낮음";
        competitionRate = 0;

    } else if (views < 500) {

        competition = "보통";
        competitionRate = 0.02;

    } else if (views < 1000) {

        competition = "높음";
        competitionRate = 0.04;

    } else {

        competition = "매우 높음";
        competitionRate = 0.06;
    }


    // =================================================
    // 3. 프로그램 권장 입찰가 계산
    // =================================================

    // KB시세의 70%를 기본 입찰 기준가격으로 설정
    const baseBidPrice =
        kbPrice * 0.70;


    // 경쟁도를 반영한 중심 입찰가격
    let recommendedBid =
        baseBidPrice * (1 + competitionRate);


    // 권장 입찰가가 최저가보다 낮아지지 않도록 처리
    if (recommendedBid < minimumPrice) {

        recommendedBid = minimumPrice;
    }


    // 권장 입찰 범위
    const lowBid =
        recommendedBid * 0.98;

    const highBid =
        recommendedBid * 1.02;


    // =================================================
    // 4. 금액을 원화 형식으로 변환
    // =================================================

    function formatWon(price) {

        return Math.round(price).toLocaleString("ko-KR") + "원";
    }


    // =================================================
    // 5. 가격 매력도 판단
    // =================================================

    let priceAttractiveness = "";

    if (kbRate <= 60) {

        priceAttractiveness = "매우 높음";

    } else if (kbRate <= 70) {

        priceAttractiveness = "높음";

    } else if (kbRate <= 80) {

        priceAttractiveness = "보통";

    } else {

        priceAttractiveness = "낮음";
    }


    // =================================================
    // 6. 분석 결과 출력
    // =================================================

    resultBox.innerHTML = `

        <strong>경매 기초 분석</strong><br><br>

        감정가 대비 최저가:
        ${appraisalRate.toFixed(1)}%<br>

        KB시세 대비 최저가:
        ${kbRate.toFixed(1)}%<br>

        유찰 횟수:
        ${failedCount}회<br>

        마이옥션 조회수:
        ${views.toLocaleString()}회<br><br>


        <strong>가격 매력도</strong><br>
        ${priceAttractiveness}<br><br>


        <strong>예상 경쟁도</strong><br>
        ${competition}<br><br>


        <strong>프로그램 권장 입찰 범위</strong><br>

        ${formatWon(lowBid)}
        ~
        ${formatWon(highBid)}

        <br><br>

        <small>
        ※ 본 결과는 입력된 공개정보를 기준으로 계산한 참고용 분석입니다.
        실제 입찰 전 권리분석, 점유관계, 명도비용 등을 별도로 확인해야 합니다.
        </small>
    `;


    // 기본 분석이 끝나면 Gemini 버튼 활성화
    aiOpinionButton.disabled = false;
});


// =====================================================
// 7. Gemini AI 종합의견
// =====================================================

aiOpinionButton.addEventListener("click", async () => {

    aiOpinionBox.textContent =
        "AI가 경매 데이터를 분석하고 있습니다...";


    // 입력 데이터 수집
    const data = {

        case_number:
            document.getElementById("case-number").value,

        apartment_name:
            document.getElementById("apartment-name").value,

        address:
            document.getElementById("address").value,

        appraisal_price:
            document.getElementById("appraisal-price").value,

        minimum_price:
            document.getElementById("minimum-price").value,

        kb_price:
            document.getElementById("kb-price").value,

        failed_count:
            document.getElementById("failed-count").value,

        views:
            document.getElementById("views").value
    };


    try {

        // Flask 서버의 Gemini API 호출
        const response = await fetch(
            "/api/recommend",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(data)
            }
        );


        // 서버 응답을 JSON으로 변환
        const result = await response.json();


        // 서버에서 오류가 발생한 경우
        if (!response.ok) {

            throw new Error(
                result.error ||
                "AI 분석에 실패했습니다."
            );
        }


        // =================================================
        // Gemini 결과를 읽기 쉽게 표시
        // 줄바꿈을 HTML <br>로 변환
        // =================================================

        aiOpinionBox.innerHTML =
            result.result.replace(/\n/g, "<br>");


    } catch (error) {

        // 실제 오류 내용을 화면에 표시
        aiOpinionBox.textContent =
            "AI 분석 오류:\n\n" +
            error.message;

        console.error(error);
    }
});
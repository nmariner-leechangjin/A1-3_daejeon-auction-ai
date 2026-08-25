const analyzeButton =
    document.getElementById("analyze-button");

const resultBox =
    document.getElementById("result-box");

const aiOpinionButton =
    document.getElementById("ai-opinion-button");

const aiOpinionBox =
    document.getElementById("ai-opinion-box");


// =====================================================
// 기본 경매 분석
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


    if (!appraisalPrice || !minimumPrice || !kbPrice) {

        resultBox.innerHTML =
            "감정가, 최저가, KB시세를 모두 입력해주세요.";

        return;
    }


    const appraisalRate =
        (minimumPrice / appraisalPrice) * 100;


    const kbRate =
        (minimumPrice / kbPrice) * 100;


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


    const baseBidPrice =
        kbPrice * 0.70;


    let recommendedBid =
        baseBidPrice * (1 + competitionRate);


    if (recommendedBid < minimumPrice) {

        recommendedBid = minimumPrice;
    }


    const lowBid =
        recommendedBid * 0.98;

    const highBid =
        recommendedBid * 1.02;


    function formatWon(price) {

        return Math.round(price).toLocaleString("ko-KR") + "원";
    }


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


    aiOpinionButton.disabled = false;
});


// =====================================================
// Gemini AI 종합의견
// =====================================================

aiOpinionButton.addEventListener("click", async () => {

    aiOpinionBox.textContent =
        "AI가 경매 데이터를 분석하고 있습니다...";


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

        const response =
            await fetch(
                "/api/recommend",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(data)
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.error ||
                "AI 분석에 실패했습니다."
            );
        }


        // Gemini 결과를 읽기 쉽게 표시
        aiOpinionBox.textContent =
            result.result;


    } catch (error) {

        aiOpinionBox.textContent =
            "AI 분석 오류:\n\n" +
            error.message;

        console.error(error);
    }
});
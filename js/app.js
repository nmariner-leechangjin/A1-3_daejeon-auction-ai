const analyzeButton = document.getElementById("analyze-button");
const resultBox = document.getElementById("result-box");
const aiOpinionButton =
    document.getElementById("ai-opinion-button");

const aiOpinionBox =
    document.getElementById("ai-opinion-box");
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


    // 조회수에 따른 경쟁도와 가중치
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


    // 금액을 원화 형식으로 바꾸는 함수
    function formatWon(price) {

        return Math.round(price).toLocaleString("ko-KR") + "원";
    }


    // 가격 매력도 판단
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


    // 분석 결과 출력
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

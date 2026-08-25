const analyzeButton = document.getElementById("analyze-button");
const resultBox = document.getElementById("result-box");

analyzeButton.addEventListener("click", function () {

    const appraisalPrice =
        Number(document.getElementById("appraisal-price").value);

    const minimumPrice =
        Number(document.getElementById("minimum-price").value);

    const kbPrice =
        Number(document.getElementById("kb-price").value);

    const views =
        Number(document.getElementById("views").value);

    if (!appraisalPrice || !minimumPrice || !kbPrice) {

        resultBox.innerHTML =
            "감정가, 최저가, KB시세를 모두 입력해주세요.";

        return;
    }

    const appraisalRate =
        (minimumPrice / appraisalPrice) * 100;

    const kbRate =
        (minimumPrice / kbPrice) * 100;

    resultBox.innerHTML = `
        <strong>기초 분석 결과</strong><br><br>

        감정가 대비 최저가:
        ${appraisalRate.toFixed(1)}%<br>

        KB시세 대비 최저가:
        ${kbRate.toFixed(1)}%<br>

        마이옥션 조회수:
        ${views.toLocaleString()}회
    `;
});
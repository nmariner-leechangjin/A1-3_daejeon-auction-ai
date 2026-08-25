import os

from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from google import genai


load_dotenv()

app = Flask(__name__, static_folder=".", static_url_path="")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY가 없습니다.")

client = genai.Client(api_key=api_key)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)


@app.route("/api/recommend", methods=["POST"])
def recommend():

    try:
        # JSON 데이터를 안전하게 가져옵니다.
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "분석할 경매 정보가 없습니다."
            }), 400


        # ---------------------------------------------
        # 입력값
        # ---------------------------------------------

        appraisal_price = float(
            data.get("appraisal_price") or 0
        )

        minimum_price = float(
            data.get("minimum_price") or 0
        )

        kb_price = float(
            data.get("kb_price") or 0
        )

        failed_count = int(
            data.get("failed_count") or 0
        )

        views = int(
            data.get("views") or 0
        )


        if (
            appraisal_price <= 0
            or minimum_price <= 0
            or kb_price <= 0
        ):
            return jsonify({
                "error": "감정가, 최저가, KB시세를 확인해주세요."
            }), 400


        # ---------------------------------------------
        # 프로그램 분석값
        # ---------------------------------------------

        appraisal_rate = (
            minimum_price / appraisal_price
        ) * 100

        kb_rate = (
            minimum_price / kb_price
        ) * 100


        if views < 200:

            competition = "낮음"
            competition_rate = 0

        elif views < 500:

            competition = "보통"
            competition_rate = 0.02

        elif views < 1000:

            competition = "높음"
            competition_rate = 0.04

        else:

            competition = "매우 높음"
            competition_rate = 0.06


        if kb_rate <= 60:

            price_attractiveness = "매우 높음"

        elif kb_rate <= 70:

            price_attractiveness = "높음"

        elif kb_rate <= 80:

            price_attractiveness = "보통"

        else:

            price_attractiveness = "낮음"


        base_bid_price = kb_price * 0.70

        recommended_bid = (
            base_bid_price *
            (1 + competition_rate)
        )

        if recommended_bid < minimum_price:
            recommended_bid = minimum_price


        low_bid = recommended_bid * 0.98
        high_bid = recommended_bid * 1.02


        # ---------------------------------------------
        # Gemini 프롬프트
        # ---------------------------------------------

        prompt = f"""
당신은 대전 지역 아파트 부동산 경매 분석을 도와주는 AI입니다.

아래에 제공된 정보와 프로그램 계산 결과만 사용하여
초보자도 이해하기 쉬운 한국어 종합 의견을 작성하세요.

[경매 물건 정보]

사건번호: {data.get("case_number")}
아파트명: {data.get("apartment_name")}
주소: {data.get("address")}

감정가: {appraisal_price:,.0f}원
최저가: {minimum_price:,.0f}원
KB시세: {kb_price:,.0f}원

유찰 횟수: {failed_count}회
마이옥션 조회수: {views:,}회

[프로그램 계산 결과]

감정가 대비 최저가: {appraisal_rate:.1f}%
KB시세 대비 최저가: {kb_rate:.1f}%

가격 매력도: {price_attractiveness}
예상 경쟁도: {competition}

프로그램 권장 입찰 범위:
{low_bid:,.0f}원 ~ {high_bid:,.0f}원


다음 순서로 작성하세요.

1. 가격 측면의 장점

2. 예상 경쟁도

3. 주의해서 확인해야 할 사항

4. 프로그램 권장 입찰 범위

5. 초보 투자자를 위한 최종 의견


작성 규칙:

- 각 번호 항목 사이에 빈 줄을 넣으세요.
- 각 항목의 내용은 2~4개의 짧은 문단으로 작성하세요.
- 한 문단이 너무 길어지지 않도록 하세요.
- 제공된 숫자를 정확하게 사용하세요.
- None이라는 단어를 절대 사용하지 마세요.
- 제공되지 않은 사실을 만들어내지 마세요.
- 실제 낙찰이나 투자 수익을 보장하지 마세요.
- 실제 입찰 전 권리분석과 현장 확인이 필요하다고 알려주세요.
- Markdown 기호를 사용하지 마세요.
- 별표(*)를 사용하지 마세요.
- 샵(#)을 사용하지 마세요.
- 하이픈(-)을 bullet 용도로 사용하지 마세요.
- 물결표(~) 앞뒤에 백슬래시를 사용하지 마세요.
- 자연스러운 한국어 문장으로 작성하세요.
"""


        # ---------------------------------------------
        # Gemini 호출
        # ---------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        result_text = response.text.strip()


        if not result_text:
            return jsonify({
                "error": "Gemini에서 분석 결과를 받지 못했습니다."
            }), 500


        return jsonify({
            "result": result_text
        }), 200


    except Exception as error:

        # Render 로그에서 실제 원인을 확인할 수 있도록 출력
        print("========================================")
        print("GEMINI API ERROR")
        print(type(error).__name__)
        print(str(error))
        print("========================================")


        return jsonify({
            "error": (
                "Gemini 분석 중 오류가 발생했습니다: "
                + str(error)
            )
        }), 500


if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 8000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
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

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "분석할 경매 정보가 없습니다."
        }), 400

    try:

        # ---------------------------------------------
        # 입력값
        # ---------------------------------------------

        appraisal_price = float(data.get("appraisal_price") or 0)
        minimum_price = float(data.get("minimum_price") or 0)
        kb_price = float(data.get("kb_price") or 0)

        failed_count = int(data.get("failed_count") or 0)
        views = int(data.get("views") or 0)


        if appraisal_price <= 0 or minimum_price <= 0 or kb_price <= 0:
            return jsonify({
                "error": "감정가, 최저가, KB시세를 확인해주세요."
            }), 400


        # ---------------------------------------------
        # 프로그램 분석값 계산
        # ---------------------------------------------

        appraisal_rate = (
            minimum_price / appraisal_price
        ) * 100

        kb_rate = (
            minimum_price / kb_price
        ) * 100


        # 조회수에 따른 경쟁도
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


        # 가격 매력도
        if kb_rate <= 60:
            price_attractiveness = "매우 높음"

        elif kb_rate <= 70:
            price_attractiveness = "높음"

        elif kb_rate <= 80:
            price_attractiveness = "보통"

        else:
            price_attractiveness = "낮음"


        # 권장 입찰가
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
당신은 대전 지역 아파트 경매 분석을 도와주는 AI입니다.

사용자가 입력한 정보와 프로그램이 계산한 결과만 사용해서
초보자도 쉽게 이해할 수 있는 종합 의견을 작성하세요.

[경매 물건 정보]

사건번호: {data.get("case_number")}
아파트명: {data.get("apartment_name")}
주소: {data.get("address")}

감정가: {appraisal_price:,.0f}원
최저가: {minimum_price:,.0f}원
KB시세: {kb_price:,.0f}원

유찰횟수: {failed_count}회
마이옥션 조회수: {views:,}회

[프로그램 계산 결과]

감정가 대비 최저가: {appraisal_rate:.1f}%
KB시세 대비 최저가: {kb_rate:.1f}%

가격 매력도: {price_attractiveness}
예상 경쟁도: {competition}

프로그램 권장 입찰 범위:
{low_bid:,.0f}원 ~ {high_bid:,.0f}원


다음 형식으로 작성하세요.

1. 가격 측면의 장점
- 핵심 내용을 2~3개 bullet로 설명

2. 예상 경쟁도
- 조회수와 프로그램이 계산한 경쟁도를 바탕으로 설명

3. 주의해서 확인해야 할 사항
- 권리분석
- 점유관계
- 관리비
- 현장 상태
등 실제 입찰 전에 확인할 내용을 설명

4. 프로그램 권장 입찰 범위
- {low_bid:,.0f}원 ~ {high_bid:,.0f}원이 계산된 이유를 쉽게 설명

5. 초보 투자자를 위한 최종 의견
- 이 물건을 숫자만 보고 판단하면 안 되는 이유를 설명
- 실제 낙찰이나 수익을 보장하지 않는다고 명확히 설명

중요한 작성 규칙:

- 반드시 위에 제공된 숫자를 그대로 사용하세요.
- None이라는 단어를 사용하지 마세요.
- 제공되지 않은 사실을 만들어내지 마세요.
- 실제 낙찰 가능성이나 투자 수익을 보장하지 마세요.
- Markdown 문법을 사용하지 마세요.
- #, ##, ###, **, ---, * 기호를 사용하지 마세요.
- 제목은 "1. 가격 측면의 장점"처럼 작성하세요.
- 각 항목 사이에는 빈 줄을 넣으세요.
- 한국어로 자연스럽고 읽기 쉽게 작성하세요.
"""


        # ---------------------------------------------
        # Gemini 호출
        # ---------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        return jsonify({
            "result": response.text
        })


    except Exception as error:

        print("Gemini API 오류:", error)

        return jsonify({
            "error": f"Gemini API 오류: {str(error)}"
        }), 500


if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 8000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
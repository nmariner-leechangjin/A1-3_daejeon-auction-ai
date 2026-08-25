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

    prompt = f"""
당신은 대전 지역 아파트 부동산 경매 분석을 도와주는 AI입니다.

사건번호: {data.get("case_number")}
아파트명: {data.get("apartment_name")}
주소: {data.get("address")}

감정가: {data.get("appraisal_price")}원
최저가: {data.get("minimum_price")}원
KB시세: {data.get("kb_price")}원
유찰횟수: {data.get("failed_count")}회
마이옥션 조회수: {data.get("views")}회

프로그램 계산 결과:

감정가 대비 최저가: {data.get("appraisal_rate")}%
KB시세 대비 최저가: {data.get("kb_rate")}%
가격 매력도: {data.get("price_attractiveness")}
예상 경쟁도: {data.get("competition")}
프로그램 권장 입찰 범위:
{data.get("low_bid")}원 ~ {data.get("high_bid")}원

위 정보를 바탕으로 한국어로 종합 의견을 작성해주세요.

다음 순서로 작성해주세요.

1. 가격 측면의 장점
2. 예상 경쟁도
3. 주의해서 확인해야 할 사항
4. 프로그램 권장 입찰 범위에 대한 설명
5. 초보 경매 투자자가 이해하기 쉬운 최종 의견

중요:
- 제공된 데이터에 없는 사실을 만들지 마세요.
- 낙찰이나 수익을 보장하지 마세요.
- 실제 입찰 전 권리분석과 현장 확인이 필요하다고 알려주세요.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return jsonify({
            "result": response.text
        })

    except Exception as error:

        return jsonify({
            "error": f"Gemini API 오류: {str(error)}"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
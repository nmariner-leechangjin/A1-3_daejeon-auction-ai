import json
import os
from http.server import BaseHTTPRequestHandler

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY가 없습니다.")

client = genai.Client(api_key=api_key)


class handler(BaseHTTPRequestHandler):

    def do_POST(self):

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except json.JSONDecodeError:

            self.send_response(400)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.end_headers()

            response = {
                "error": "잘못된 JSON 데이터입니다."
            }

            self.wfile.write(
                json.dumps(
                    response,
                    ensure_ascii=False
                ).encode("utf-8")
            )

            return

        if not data:

            self.send_response(400)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.end_headers()

            response = {
                "error": "분석할 경매 정보가 없습니다."
            }

            self.wfile.write(
                json.dumps(
                    response,
                    ensure_ascii=False
                ).encode("utf-8")
            )

            return

        prompt = f"""
당신은 대전 지역 아파트 부동산 경매 분석을 도와주는 AI입니다.

아래 정보는 사용자가 입력한 경매물건 정보와
프로그램이 계산한 기초 분석 결과입니다.

[경매물건 정보]

사건번호: {data.get("case_number")}
아파트명: {data.get("apartment_name")}
주소: {data.get("address")}

감정가: {data.get("appraisal_price")}원
최저가: {data.get("minimum_price")}원
KB시세: {data.get("kb_price")}원

유찰횟수: {data.get("failed_count")}회
마이옥션 조회수: {data.get("views")}회

[프로그램 계산 결과]

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
- 제공된 데이터에 없는 사실을 만들어내지 마세요.
- 실제 낙찰 가능성이나 투자 수익을 보장하지 마세요.
- 실제 입찰 전 권리분석과 현장 확인이 필요하다는 점을 알려주세요.
"""

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            result = {
                "result": response.text
            }

            response_body = json.dumps(
                result,
                ensure_ascii=False
            ).encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(response_body))
            )

            self.end_headers()

            self.wfile.write(response_body)

        except Exception as error:

            response = {
                "error": f"Gemini API 오류: {str(error)}"
            }

            response_body = json.dumps(
                response,
                ensure_ascii=False
            ).encode("utf-8")

            self.send_response(500)

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(response_body))
            )

            self.end_headers()

            self.wfile.write(response_body)
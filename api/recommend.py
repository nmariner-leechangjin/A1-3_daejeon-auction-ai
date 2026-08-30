import json
import os
from http.server import BaseHTTPRequestHandler

from google import genai


def send_json(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return send_json(self, 400, {"error": "요청 형식이 올바르지 않습니다."})

        if content_length <= 0 or content_length > 20000:
            return send_json(self, 400, {"error": "분석할 경매 정보를 확인해주세요."})

        try:
            data = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return send_json(self, 400, {"error": "잘못된 JSON 데이터입니다."})

        required = ("appraisal_price", "minimum_price", "kb_price",
                    "appraisal_rate", "kb_rate", "low_bid", "high_bid")
        if not isinstance(data, dict) or any(data.get(key) in (None, "") for key in required):
            return send_json(self, 400, {"error": "필수 분석값이 누락되었습니다."})

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return send_json(self, 500, {"error": "서버의 AI 환경 변수가 설정되지 않았습니다."})

        prompt = f"""
당신은 대전 지역 아파트 부동산 경매 분석을 돕는 AI입니다.
제공된 정보만 사용하고, 없는 사실은 만들지 마세요.

[물건 정보]
사건번호: {str(data.get('case_number', '미입력'))[:30]}
아파트명: {str(data.get('apartment_name', '미입력'))[:50]}
주소: {str(data.get('address', '미입력'))[:100]}
감정가: {data.get('appraisal_price')}원
최저가: {data.get('minimum_price')}원
KB시세: {data.get('kb_price')}원
유찰횟수: {data.get('failed_count', 0)}회
조회수: {data.get('views', 0)}회

[프로그램 계산 결과]
감정가 대비 최저가: {data.get('appraisal_rate')}%
KB시세 대비 최저가: {data.get('kb_rate')}%
가격 매력도: {data.get('price_attractiveness', '미산정')}
예상 경쟁도: {data.get('competition', '미산정')}
권장 입찰 범위: {data.get('low_bid')}원 ~ {data.get('high_bid')}원

아래 다섯 항목을 초보자가 이해하기 쉬운 한국어로 작성하세요.
1. 가격 측면의 장점
2. 예상 경쟁도
3. 반드시 확인할 위험요소
4. 권장 입찰 범위의 의미
5. 최종 참고 의견

낙찰 가능성이나 투자수익을 보장하지 말고, 실제 입찰 전 권리분석과 현장 확인이 필요하다고 명시하세요.
"""
        try:
            client = genai.Client(api_key=api_key)
            configured_model = os.getenv("GEMINI_MODEL", "").strip()
            model_candidates = [
                configured_model,
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite",
            ]
            model_candidates = list(dict.fromkeys(
                model for model in model_candidates if model
            ))

            last_error = None
            for model in model_candidates:
                try:
                    response = client.models.generate_content(
                        model=model,
                        contents=prompt,
                    )
                    text = getattr(response, "text", None)
                    if text:
                        print(f"Gemini model selected: {model}")
                        return send_json(self, 200, {"result": text})
                except Exception as error:
                    last_error = error
                    print(f"Gemini model unavailable: {model} ({type(error).__name__})")

            if last_error:
                print(f"All Gemini models failed: {type(last_error).__name__}")
            return send_json(self, 502, {"error": "사용 가능한 AI 모델을 찾지 못했습니다. 잠시 후 다시 시도해주세요."})
        except Exception as error:
            print(f"Gemini client error: {type(error).__name__}")
            return send_json(self, 502, {"error": "AI 서비스 연결에 실패했습니다. 잠시 후 다시 시도해주세요."})

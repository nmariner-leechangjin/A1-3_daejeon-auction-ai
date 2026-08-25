import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY가 없습니다.")


client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="대전 아파트 경매 분석 서비스에 사용할 짧은 인사말을 만들어줘."
)

print(response.text)
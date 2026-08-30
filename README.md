# 경매로 내집찬스

대전 아파트 경매 물건의 감정가·최저가·KB시세·유찰 횟수·조회수를 비교하고, 참고용 입찰 범위와 Gemini AI 종합의견을 제공하는 반응형 웹서비스입니다.

> 분석 결과는 참고자료이며 낙찰이나 투자수익을 보장하지 않습니다. 실제 입찰 전 권리분석과 현장 확인이 필요합니다.

## 서비스 구성

1. **서비스 소개**: 가격 비교, 입찰 범위, AI 의견의 가치를 설명합니다.
2. **입찰가 분석**: 물건 정보를 입력해 기초 분석과 AI 의견을 확인합니다.
3. **이용 안내**: 입력부터 검토까지의 절차와 투자 유의사항을 안내합니다.

## 주요 기능

- 감정가 및 KB시세 대비 최저가 비율 계산
- 조회수 기반 예상 경쟁도 분류
- 시세와 경쟁도를 반영한 참고용 입찰 범위
- 계산 결과 기반 Gemini AI 종합의견
- 빈 입력, 잘못된 숫자, API 오류, 비정상 응답, 20초 타임아웃 안내
- 모바일·태블릿·데스크톱 반응형 화면
- 요청 시에만 AI를 호출하는 비용 절감 구조

## 기술 스택

- Frontend: HTML5, CSS3, Vanilla JavaScript
- Backend: Vercel Serverless Functions (Python)
- AI: Google Gemini API, google-genai
- Deployment: GitHub + Vercel

## 프로젝트 구조

```text
A1-3_daejeon-auction-ai/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── app.js
├── api/
│   └── recommend.py
├── images/
├── requirements.txt
├── vercel.json
├── SERVICE_PLAN.md
├── README.md
└── .gitignore
```

## 동작 흐름

```text
사용자 입력
→ JavaScript 기초 계산
→ 가격·경쟁 분석 표시
→ 사용자가 AI 의견 요청
→ fetch('/api/recommend')
→ Vercel Python 함수
→ Gemini API
→ JSON 응답
→ 화면에 AI 의견 표시
```

JavaScript에서 계산 가능한 항목을 먼저 처리하므로 AI 의견을 요청하지 않으면 Gemini API 비용이 발생하지 않습니다.

## 환경 변수

API 키는 코드나 GitHub에 입력하지 않습니다. 로컬 환경 또는 Vercel 프로젝트 환경 변수에 아래 값을 설정합니다.

```text
GEMINI_API_KEY=발급받은_Gemini_API_키
```

모델을 바꾸려면 선택적으로 다음 값을 추가합니다.

```text
GEMINI_MODEL=gemini-2.5-flash
```

.env와 .vercel은 .gitignore에 포함되어 GitHub에 업로드되지 않습니다.

## 로컬 실행

Vercel Serverless Function까지 함께 시험하려면 프로젝트 폴더에서 실행합니다.

```powershell
vercel dev
```

일반 정적 서버인 python -m http.server는 HTML/CSS/JavaScript만 제공하므로 Python API를 실행하지 못합니다.

## Vercel 배포

1. Vercel에서 GitHub 저장소를 가져옵니다.
2. Production Branch를 main으로 설정합니다.
3. GEMINI_API_KEY 환경 변수를 추가합니다.
4. 배포 URL에서 메뉴, 모바일 화면, 기초 분석과 AI 의견을 확인합니다.

**배포 URL:** https://a1-3-daejeon-auction-ai.vercel.app

## 테스트 기준

- 정상 입력 시 기초 분석과 권장 범위가 표시되는가
- 필수 금액이 비어 있거나 0이면 안내되는가
- AI 요청 중 버튼이 비활성화되는가
- API 오류와 20초 초과 시 안내되는가
- 375px 모바일과 데스크톱에서 화면이 깨지지 않는가
- API 키가 코드, README, 화면 캡처에 노출되지 않는가

## 제출 자료

- 서비스 기획서: SERVICE_PLAN.md
- 데스크톱·모바일·AI 결과 캡처: images 폴더
- AI 코딩 도구 사용 증빙 및 제출 문서: 저장소의 DOCX 파일

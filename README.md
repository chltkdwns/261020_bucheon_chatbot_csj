# 점심 메뉴 추천 챗봇

Groq API로 만든 터미널 챗봇입니다. 부천 토박이 친구처럼 반말로 대화하며 오늘 점심 메뉴를 추천해 줍니다.
Groq 호출이 실패하면(한도 초과 등) 자동으로 Gemini API로 전환됩니다.

## 주요 기능

- 기분, 예산, 먹고 싶은 종류를 되물으며 메뉴 최대 3개 추천
- 대화 기록을 유지해 이미 추천한 메뉴는 다시 추천하지 않음
- Groq 실패 시 Gemini로 자동 전환
- API 키는 `.env`로 관리 (GitHub에 올라가지 않음)

## 설치 라이브러리

`requirements.txt`에 정리되어 있습니다.

| 라이브러리 | 용도 |
|---|---|
| groq | Groq API 호출 |
| python-dotenv | `.env`에서 API 키 읽기 |
| google-genai | Gemini API 호출 (폴백) |

```bash
pip install -r requirements.txt
```

## API 키 설정

1. `.env.example`을 복사해서 `.env`로 이름을 바꿉니다.
2. 각 키를 채웁니다.

```
GROQ_API_KEY=여기에_Groq_키
GEMINI_API_KEY=여기에_Gemini_키
```

- Groq 키: https://console.groq.com/keys
- Gemini 키: https://aistudio.google.com/apikey

`GEMINI_API_KEY`는 선택입니다. 없으면 Groq만 사용합니다.

## 실행 방법

```bash
python chatbot.py
```

## 사용 예시

```
오늘 점심 뭐 먹을지 같이 정해 보자! (종료: exit)
질문 : 점심 추천해줘
오늘 기분이 어때? 든든하게 먹고 싶어, 가볍게 먹고 싶어? 🍚
질문 : 든든하게
- 김치찌개: 따뜻한 국물에 밥 한 공기 뚝딱이야
- 제육볶음: 매콤하고 밥도둑이라 든든해
- 돈까스: 바삭하고 양이 넉넉해 🍽️
```

종료하려면 `exit` 또는 `종료`를 입력하세요.

## 주의

- `.env`는 절대 GitHub에 올리지 마세요. (`.gitignore`에 등록되어 있습니다)
- 가게 이름, 가격, 영업시간은 모델이 정확히 모르므로 메뉴 종류 위주로 추천합니다.

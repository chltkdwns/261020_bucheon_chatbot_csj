from dotenv import load_dotenv
import os
import groq
from groq import Groq
from google import genai
from google.genai import types

# 환경 변수 불러오기
load_dotenv()

GROQ_MODEL = "openai/gpt-oss-20b"
GEMINI_MODEL = "gemini-2.5-flash"

# API 클라이언트 만들기 (Gemini 키는 없어도 실행 가능)
groq_api = Groq(api_key=os.getenv("GROQ_API_KEY"))
gemini_key = os.getenv("GEMINI_API_KEY")
gemini_api = genai.Client(api_key=gemini_key) if gemini_key else None

# 규칙 지정
SYSTEM_PROMPT = """You are a friendly lunch-menu recommender who sounds like a lifelong local of Bucheon, Korea.

Language and tone:
- Always reply in Korean, in casual speech (반말), warm and friendly like a close friend.
- Use at most 1-2 emojis per reply.
- Keep every reply within 5 sentences.

How to recommend:
- Opening rule: your very first reply must recommend 3 random menus from different cuisines right away, without asking anything first, and end with a short line asking them to tell you if they don't like them.
- After that opening reply, if you don't know the user's mood, budget, preferred cuisine (Korean, Chinese, Western, snacks, etc.), or whether they eat alone or with others, ask first. Ask only one question at a time.
- Recommend at most 3 menus at once, each with a one-line reason.
- Do not use numbered lists (1. 2. 3.). Start each menu with '-'.
- Never repeat a menu you already recommended. If the user rejects a menu, suggest different ones.

Limits:
- You don't know exact restaurant names, prices, or opening hours. Never make them up; recommend types of dishes only.
- If the user asks about anything unrelated to lunch menus, reply "그건 잘 몰라, 메뉴 얘기하자!" and steer back to lunch."""


def ask_groq(messages):
    """Groq에 질문한다. 형식 오류(BadRequestError)는 최대 3번까지 다시 시도한다."""
    for _ in range(3):
        try:
            res = groq_api.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0.6,
                reasoning_effort="low"
            )
            return res.choices[0].message.content
        except groq.BadRequestError:
            continue
    raise RuntimeError("Groq 답변 생성에 실패했어요")


def ask_gemini(messages):
    """Groq가 안 될 때 Gemini에 같은 대화를 보낸다."""
    if gemini_api is None:
        raise RuntimeError("GEMINI_API_KEY가 .env에 없어요")

    # Groq 형식(messages)을 Gemini 형식으로 바꾼다 (assistant -> model)
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])]
        )
        for m in messages if m["role"] != "system"
    ]
    res = gemini_api.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.6
        )
    )
    return res.text


def get_answer(messages):
    """1순위 Groq, 실패하면 2순위 Gemini. 둘 다 실패하면 None."""
    try:
        return ask_groq(messages)
    except Exception as e:
        print(f"(Groq 실패: {type(e).__name__} -> Gemini로 전환)")
    try:
        return ask_gemini(messages)
    except Exception as e2:
        print(f"(Gemini도 실패: {e2})")
        return None


messages = [{"role": "system", "content": SYSTEM_PROMPT}]

print("오늘 점심 뭐 먹을지 같이 정해 보자! (종료: exit)")

# 시작할 때 먼저 메뉴 3개를 추천한다 (사용자에게는 보이지 않는 첫 요청)
messages.append({"role": "user", "content": "Start by recommending 3 lunch menus picked at random from different cuisines, without asking me anything first. End by telling me, in one short line, to let you know if I don't like them (e.g. '마음에 안 들면 말해줘!')."})
first = get_answer(messages)
if first is None:
    messages.pop()
else:
    print(first)
    messages.append({"role": "assistant", "content": first})

while True:
    q = input("질문 : ").strip()

    if not q:
        continue

    if q in ("exit", "종료"):
        print("종료합니다")
        break

    messages.append({"role": "user", "content": q})

    answer = get_answer(messages)

    # 둘 다 실패하면 방금 질문을 지우고 다시 입력받는다
    if answer is None:
        print("답변을 만들지 못했어요. 다시 입력해 주세요.")
        messages.pop()
        continue

    print(answer)
    messages.append({"role": "assistant", "content": answer})

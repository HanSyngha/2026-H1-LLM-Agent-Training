"""
ADK 실습 정답: 멀티 도구 대화형 에이전트

Google ADK를 사용하여 2개 이상의 커스텀 도구를 가진 에이전트를 구현하고,
대화형 인터페이스로 동작하도록 합니다.

실행 방법:
    python exercise_solution.py

의존성:
    pip install google-adk litellm
"""

import asyncio
import os
import sys

# 공통 설정 로드
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

# LiteLLM 프록시 설정
os.environ["HTTPS_PROXY"] = PROXY_URL
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["OPENAI_API_KEY"] = GATEWAY_API_KEY
os.environ["OPENAI_API_BASE"] = GATEWAY_BASE_URL

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ============================================================
# 도구(Tool) 정의 - 2개 이상의 커스텀 도구를 구현합니다
# ============================================================

def search_menu(restaurant: str) -> dict:
    """식당의 메뉴를 검색합니다.

    사내 구내식당 또는 주변 식당의 메뉴 정보를 조회할 수 있습니다.

    Args:
        restaurant: 식당 이름 (예: "구내식당", "맛있는집", "스시오마카세")

    Returns:
        dict: 메뉴 목록과 가격 정보
    """
    # 더미 메뉴 데이터
    menus = {
        "구내식당": {
            "restaurant": "구내식당",
            "menus": [
                {"name": "된장찌개 정식", "price": 6000, "calories": 650},
                {"name": "제육볶음 정식", "price": 6500, "calories": 780},
                {"name": "생선구이 정식", "price": 7000, "calories": 550},
            ],
            "business_hours": "11:30 - 13:30",
        },
        "맛있는집": {
            "restaurant": "맛있는집",
            "menus": [
                {"name": "김치찌개", "price": 8000, "calories": 700},
                {"name": "순두부찌개", "price": 8500, "calories": 620},
                {"name": "비빔밥", "price": 9000, "calories": 580},
            ],
            "business_hours": "11:00 - 21:00",
        },
    }
    result = menus.get(restaurant)
    if result:
        return result
    return {"error": f"'{restaurant}' 식당 정보를 찾을 수 없습니다. 등록된 식당: {list(menus.keys())}"}


def book_meeting(date: str, time: str, participants: str, title: str = "회의") -> dict:
    """회의를 예약합니다.

    지정된 날짜와 시간에 참석자를 초대하여 회의를 예약합니다.

    Args:
        date: 회의 날짜 (예: "2026-04-01")
        time: 회의 시간 (예: "14:00")
        participants: 참석자 이름 (쉼표로 구분, 예: "홍길동, 김철수")
        title: 회의 제목

    Returns:
        dict: 예약 결과
    """
    participant_list = [p.strip() for p in participants.split(",")]
    return {
        "status": "예약 완료",
        "meeting_id": "MTG-20260401-001",
        "title": title,
        "date": date,
        "time": time,
        "participants": participant_list,
        "location": "회의실 A (3층)",
        "message": f"{len(participant_list)}명에게 초대 알림이 전송되었습니다.",
    }


def get_exchange_rate(currency: str) -> dict:
    """실시간 환율 정보를 조회합니다.

    주요 통화의 현재 환율을 한국 원화(KRW) 기준으로 조회합니다.

    Args:
        currency: 통화 코드 (예: "USD", "JPY", "EUR", "CNY")

    Returns:
        dict: 환율 정보
    """
    # 더미 환율 데이터 (1단위 외국 통화 = X KRW)
    rates = {
        "USD": {"rate": 1350.50, "change": -5.20, "change_pct": -0.38},
        "JPY": {"rate": 8.71, "change": 0.03, "change_pct": 0.35},
        "EUR": {"rate": 1468.30, "change": 2.10, "change_pct": 0.14},
        "CNY": {"rate": 186.20, "change": -0.80, "change_pct": -0.43},
    }
    currency = currency.upper()
    if currency in rates:
        info = rates[currency]
        return {
            "currency": currency,
            "base": "KRW",
            "rate": info["rate"],
            "change": info["change"],
            "change_percent": f"{info['change_pct']}%",
            "updated_at": "2026-03-31 10:00:00",
        }
    return {"error": f"'{currency}' 통화를 지원하지 않습니다. 지원 통화: {list(rates.keys())}"}


# ============================================================
# 에이전트 정의 - LiteLlm 모델을 사용합니다
# ============================================================

model = LiteLlm(model=f"openai/{DEFAULT_MODEL}")

agent = Agent(
    name="office-assistant",
    model=model,
    instruction="""당신은 사무실 업무를 도와주는 AI 어시스턴트입니다.
사용자의 요청에 친절하고 정확하게 답변하세요.
필요한 경우 제공된 도구를 적극적으로 활용하세요.

다음 도구들을 사용할 수 있습니다:
- search_menu: 식당 메뉴를 검색합니다.
- book_meeting: 회의를 예약합니다.
- get_exchange_rate: 환율을 조회합니다.

답변은 항상 한국어로 해주세요.
도구 실행 결과를 자연스러운 문장으로 정리하여 전달해주세요.""",
    tools=[search_menu, book_meeting, get_exchange_rate],
    description="식당 메뉴 검색, 회의 예약, 환율 조회가 가능한 사무실 어시스턴트",
)


# ============================================================
# 대화형 인터페이스 구현
# ============================================================

async def interactive_loop():
    """대화형 루프를 실행합니다. 사용자가 종료할 때까지 대화를 계속합니다."""

    # Runner와 Session을 설정합니다
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="office-app",
        session_service=session_service,
    )

    # 새 세션을 생성합니다 (대화 컨텍스트 유지)
    session = await session_service.create_session(
        app_name="office-app",
        user_id="user-001",
    )

    print("=" * 60)
    print("  사무실 AI 어시스턴트 (ADK)")
    print("=" * 60)
    print("사용 가능한 기능:")
    print("  - 식당 메뉴 검색 (예: '구내식당 메뉴 알려줘')")
    print("  - 회의 예약 (예: '내일 2시에 김철수와 회의 잡아줘')")
    print("  - 환율 조회 (예: '달러 환율 얼마야?')")
    print("'종료' 또는 'quit'을 입력하면 끝납니다.\n")

    while True:
        try:
            user_input = input("사용자: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n대화를 종료합니다.")
            break

        if not user_input:
            continue
        if user_input.lower() in ["종료", "quit", "exit", "q"]:
            print("대화를 종료합니다.")
            break

        # 사용자 메시지를 Content 객체로 변환합니다
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)],
        )

        # 에이전트를 실행하고 응답을 출력합니다
        async for event in runner.run_async(
            user_id="user-001",
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"에이전트: {part.text}")
                    elif part.function_call:
                        print(f"  [도구 호출] {part.function_call.name}({dict(part.function_call.args)})")
                    elif part.function_response:
                        print(f"  [도구 응답] {part.function_response.name}")

        print()  # 가독성을 위한 빈 줄


async def demo_mode():
    """데모 모드: 미리 정의된 질문으로 에이전트를 테스트합니다."""

    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="office-app",
        session_service=session_service,
    )
    session = await session_service.create_session(
        app_name="office-app",
        user_id="demo-user",
    )

    print("=" * 60)
    print("  ADK 에이전트 데모 모드")
    print("=" * 60)

    # 테스트 질문 목록입니다
    queries = [
        "구내식당 오늘 메뉴 알려줘",
        "내일 오후 3시에 홍길동, 김철수와 프로젝트 리뷰 회의 잡아줘",
        "달러 환율이 얼마야?",
    ]

    for query in queries:
        print(f"\n{'─' * 60}")
        print(f"사용자: {query}")
        print(f"{'─' * 60}")

        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)],
        )

        async for event in runner.run_async(
            user_id="demo-user",
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"에이전트: {part.text}")

    print(f"\n{'=' * 60}")
    print("  데모 완료!")
    print(f"{'=' * 60}")


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    if "--demo" in sys.argv:
        # 데모 모드: 미리 정의된 질문으로 테스트합니다
        asyncio.run(demo_mode())
    else:
        # 대화형 모드: 사용자 입력을 받아 대화합니다
        asyncio.run(interactive_loop())

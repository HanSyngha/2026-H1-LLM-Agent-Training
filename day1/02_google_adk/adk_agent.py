"""
Google ADK (Agent Development Kit) 에이전트 예제

Google ADK는 에이전트를 쉽게 만들 수 있는 프레임워크입니다.
핵심 개념:
- Agent: 에이전트의 정의 (이름, 모델, 도구, 지시문)
- Tool: 에이전트가 사용할 수 있는 도구 (Python 함수로 정의)
- Runner: 에이전트를 실행하는 런타임
- Session: 대화의 상태를 관리하는 세션

이 예제에서는 LiteLlm을 사용하여 사내 OpenAI 호환 게이트웨이에 연결합니다.

실행 방법:
    python adk_agent.py

의존성:
    pip install google-adk litellm
"""

import asyncio
import os
import sys

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

# ──────────────────────────────────────────────
# LiteLLM 프록시 설정
# ──────────────────────────────────────────────
# LiteLlm이 사내 프록시를 사용하도록 환경 변수 설정
os.environ["HTTPS_PROXY"] = PROXY_URL
os.environ["HTTP_PROXY"] = PROXY_URL

# LiteLlm이 게이트웨이의 API 키를 사용하도록 설정
os.environ["OPENAI_API_KEY"] = GATEWAY_API_KEY
os.environ["OPENAI_API_BASE"] = GATEWAY_BASE_URL

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


# ══════════════════════════════════════════════
# 도구(Tool) 정의
# ══════════════════════════════════════════════
# ADK에서 도구는 일반 Python 함수로 정의합니다.
# 함수의 이름, 파라미터 타입 힌트, docstring이 LLM에게 전달됩니다.
# 따라서 docstring을 정확하고 명확하게 작성하는 것이 중요합니다.


def get_weather(city: str) -> dict:
    """주어진 도시의 현재 날씨 정보를 조회합니다.

    Args:
        city: 날씨를 조회할 도시 이름 (예: "서울", "부산", "제주")

    Returns:
        dict: 온도, 상태, 습도 등의 날씨 정보
    """
    # 더미 데이터 (실제로는 외부 API 호출)
    weather_data = {
        "서울": {"temperature": 15, "condition": "맑음", "humidity": 45},
        "부산": {"temperature": 18, "condition": "구름 많음", "humidity": 60},
        "제주": {"temperature": 20, "condition": "흐림", "humidity": 70},
    }
    result = weather_data.get(city, {"temperature": 16, "condition": "정보 없음", "humidity": 50})
    result["city"] = city
    return result


def calculate(expression: str) -> str:
    """수학 계산식을 평가합니다.

    간단한 사칙연산부터 복잡한 수학 표현식까지 계산할 수 있습니다.
    지원하는 연산: +, -, *, /, **, //, %

    Args:
        expression: 계산할 수학 표현식 (예: "3 + 5", "100 * 2.5")

    Returns:
        str: 계산 결과 문자열
    """
    try:
        # 안전한 수학 연산만 허용 (eval 대신 제한된 환경 사용)
        allowed_chars = set("0123456789+-*/.()**% ")
        if not all(c in allowed_chars for c in expression):
            return f"오류: 허용되지 않은 문자가 포함되어 있습니다."
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"


def search_employee(name: str) -> dict:
    """직원 정보를 이름으로 검색합니다.

    Args:
        name: 검색할 직원 이름

    Returns:
        dict: 직원의 부서, 직급, 이메일 등 정보
    """
    employees = {
        "김철수": {"department": "개발팀", "position": "시니어 엔지니어", "email": "chulsoo@company.com"},
        "이영희": {"department": "기획팀", "position": "팀장", "email": "younghee@company.com"},
        "박민수": {"department": "데이터팀", "position": "ML 엔지니어", "email": "minsoo@company.com"},
    }
    if name in employees:
        result = employees[name]
        result["name"] = name
        return result
    return {"error": f"'{name}' 직원을 찾을 수 없습니다."}


# ══════════════════════════════════════════════
# 에이전트(Agent) 정의
# ══════════════════════════════════════════════
# Agent 클래스의 주요 파라미터:
# - name: 에이전트 이름 (고유 식별자)
# - model: 사용할 LLM 모델 (LiteLlm으로 OpenAI 호환 게이트웨이 사용)
# - instruction: 에이전트의 역할과 행동 지침 (시스템 프롬프트)
# - tools: 에이전트가 사용할 도구 리스트 (Python 함수들)
# - description: 에이전트에 대한 설명 (멀티 에이전트에서 라우팅에 사용)

# LiteLlm을 사용하여 사내 OpenAI 호환 게이트웨이에 연결
# "openai/<모델명>" 형식으로 지정하면 OpenAI API 호환 엔드포인트를 사용합니다.
model = LiteLlm(model=f"openai/{DEFAULT_MODEL}")

agent = Agent(
    name="assistant",
    model=model,
    instruction="""당신은 유능한 AI 어시스턴트입니다.
사용자의 질문에 친절하고 정확하게 답변하세요.
필요한 경우 제공된 도구를 적극적으로 활용하세요.

다음 도구들을 사용할 수 있습니다:
- get_weather: 도시의 날씨 정보를 조회합니다.
- calculate: 수학 계산을 수행합니다.
- search_employee: 직원 정보를 검색합니다.

답변은 항상 한국어로 해주세요.""",
    tools=[get_weather, calculate, search_employee],
    description="날씨 조회, 계산, 직원 검색이 가능한 범용 어시스턴트",
)


async def main():
    """에이전트 실행 메인 함수"""

    # ──────────────────────────────────────────
    # Runner & Session 설정
    # ──────────────────────────────────────────
    # Runner: 에이전트를 실행하는 런타임 환경
    # - agent: 실행할 에이전트 인스턴스
    # - app_name: 애플리케이션 이름
    # - session_service: 세션(대화 상태)을 관리하는 서비스
    #
    # InMemorySessionService: 메모리 기반 세션 저장소 (개발/테스트용)
    # 프로덕션에서는 DatabaseSessionService 등을 사용합니다.
    session_service = InMemorySessionService()

    runner = Runner(
        agent=agent,
        app_name="demo-app",
        session_service=session_service,
    )

    # 새 세션 생성
    # Session: 하나의 대화 스레드를 나타내는 객체
    # - app_name: 소속 애플리케이션
    # - user_id: 사용자 식별자
    # - session_id: 세션 고유 ID
    session = await session_service.create_session(
        app_name="demo-app",
        user_id="user-001",
    )

    print("=" * 60)
    print("  Google ADK 에이전트 데모")
    print("=" * 60)

    # ──────────────────────────────────────────
    # 에이전트에 질문 보내기
    # ──────────────────────────────────────────
    # 여러 가지 질문을 순차적으로 보내며 대화 흐름을 확인합니다.
    queries = [
        "서울 날씨 알려줘",
        "3 + 5 계산해줘",
        "김철수 직원 정보 검색해줘",
        "부산 날씨도 알려주고, 100 * 25 계산도 해줘",
    ]

    from google.genai import types

    for query in queries:
        print(f"\n{'─'*60}")
        print(f"사용자: {query}")
        print(f"{'─'*60}")

        # content 객체 생성
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)],
        )

        # run_async: 에이전트를 비동기로 실행
        # - user_id: 사용자 ID
        # - session_id: 세션 ID (대화 컨텍스트 유지)
        # - new_message: 사용자 메시지
        # 반환값: 이벤트 스트림 (도구 호출, 중간 결과, 최종 답변 등)
        response_events = runner.run_async(
            user_id="user-001",
            session_id=session.id,
            new_message=content,
        )

        # 이벤트 스트림에서 결과 수집
        async for event in response_events:
            # event.content가 있고, 텍스트 파트가 있는 경우 출력
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"에이전트: {part.text}")
                    elif part.function_call:
                        # 도구 호출 이벤트
                        print(f"  [도구 호출] {part.function_call.name}({dict(part.function_call.args)})")
                    elif part.function_response:
                        # 도구 응답 이벤트
                        print(f"  [도구 응답] {part.function_response.name}: {dict(part.function_response.response)}")

    print(f"\n{'='*60}")
    print("  대화 완료!")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())

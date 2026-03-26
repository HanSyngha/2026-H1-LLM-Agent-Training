"""
LangChain 도구 사용 챗봇 예제

LangChain의 Agent를 사용하여 도구(Tool)를 호출할 수 있는 챗봇을 구현합니다.

핵심 개념:
- Tool: 에이전트가 사용할 수 있는 도구 (Python 함수)
- create_tool_calling_agent: 도구 호출이 가능한 에이전트 생성
- AgentExecutor: 에이전트를 실행하고 도구 호출 루프를 관리

실행 방법:
    python chatbot_with_tools.py

의존성:
    pip install langchain langchain-openai langchain-community
"""

import os
import sys
from datetime import datetime

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

import httpx
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


# ══════════════════════════════════════════════
# 1. 도구(Tool) 정의
# ══════════════════════════════════════════════
# @tool 데코레이터를 사용하여 LangChain 도구를 정의합니다.
# 각 도구의 docstring은 LLM이 도구를 이해하는 데 사용되므로 명확하게 작성합니다.


@tool
def search_web(query: str) -> str:
    """웹에서 정보를 검색합니다. 최신 정보나 사실 확인이 필요할 때 사용합니다.

    Args:
        query: 검색할 키워드 또는 문장
    """
    # 더미 검색 결과 (실제로는 검색 API 호출)
    search_db = {
        "날씨": "오늘 서울의 기온은 15도이며 맑은 날씨입니다.",
        "뉴스": "오늘의 주요 뉴스: AI 기술 발전이 가속화되고 있습니다.",
        "주가": "코스피 지수는 2,650포인트를 기록하고 있습니다.",
        "환율": "현재 원/달러 환율은 1,320원입니다.",
    }
    for key, value in search_db.items():
        if key in query:
            return value
    return f"'{query}'에 대한 검색 결과: 관련 정보를 찾았습니다."


@tool
def calculator(expression: str) -> str:
    """수학 계산을 수행합니다. 사칙연산, 거듭제곱 등을 계산할 수 있습니다.

    Args:
        expression: 계산할 수학 표현식 (예: "3 + 5", "100 * 2.5")
    """
    try:
        allowed_chars = set("0123456789+-*/.()**% ")
        if not all(c in allowed_chars for c in expression):
            return "오류: 허용되지 않은 문자가 포함되어 있습니다."
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"


@tool
def get_datetime() -> str:
    """현재 날짜와 시간을 반환합니다. 오늘 날짜나 현재 시각이 궁금할 때 사용합니다."""
    now = datetime.now()
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    weekday = weekdays[now.weekday()]
    return f"현재 시각: {now.strftime('%Y년 %m월 %d일')} ({weekday}요일) {now.strftime('%H시 %M분 %S초')}"


# 도구 리스트
tools = [search_web, calculator, get_datetime]


# ══════════════════════════════════════════════
# 2. LLM 설정
# ══════════════════════════════════════════════
llm = ChatOpenAI(
    model=DEFAULT_MODEL,
    base_url=GATEWAY_BASE_URL,
    api_key=GATEWAY_API_KEY,
    http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
    temperature=0.3,  # 도구 호출 시에는 낮은 temperature가 안정적
)


# ══════════════════════════════════════════════
# 3. 에이전트 프롬프트 설정
# ══════════════════════════════════════════════
# create_tool_calling_agent에서 사용할 프롬프트 템플릿
# agent_scratchpad: 에이전트의 중간 사고 과정 (도구 호출/결과)이 저장되는 곳
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """당신은 다양한 도구를 활용하는 유능한 AI 어시스턴트입니다.

사용 가능한 도구:
- search_web: 웹 검색 (뉴스, 날씨, 주가 등 최신 정보 조회)
- calculator: 수학 계산 (사칙연산, 거듭제곱 등)
- get_datetime: 현재 날짜/시간 조회

규칙:
- 도구가 필요한 질문에는 반드시 도구를 사용하세요.
- 도구 결과를 바탕으로 자연스러운 한국어 답변을 작성하세요.
- 이전 대화 내용을 기억하고 맥락에 맞게 답변하세요.""",
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
    # agent_scratchpad: 에이전트의 중간 처리 과정이 들어가는 위치
    # (도구 호출 요청 → 도구 실행 결과 → 추가 도구 호출 ... 의 반복)
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


# ══════════════════════════════════════════════
# 4. 에이전트 생성
# ══════════════════════════════════════════════
# create_tool_calling_agent: OpenAI의 tool calling 기능을 사용하는 에이전트 생성
# - llm: 사용할 LLM 모델
# - tools: 사용 가능한 도구 리스트
# - prompt: 에이전트 프롬프트 템플릿
agent = create_tool_calling_agent(llm, tools, prompt)

# AgentExecutor: 에이전트를 실행하고 도구 호출 루프를 관리
# - agent: 위에서 생성한 에이전트
# - tools: 실제 도구 실행에 사용될 도구 리스트
# - verbose: True면 중간 과정을 상세히 출력 (디버깅에 유용)
# - max_iterations: 도구 호출 최대 반복 횟수 (무한 루프 방지)
# - handle_parsing_errors: 파싱 오류 발생 시 자동 복구
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,       # 도구 호출 과정을 상세히 출력
    max_iterations=5,   # 최대 5번까지 도구 호출 반복
    handle_parsing_errors=True,
)


# ══════════════════════════════════════════════
# 5. 대화 히스토리 관리
# ══════════════════════════════════════════════
message_histories: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """세션별 대화 히스토리를 반환합니다."""
    if session_id not in message_histories:
        message_histories[session_id] = InMemoryChatMessageHistory()
    return message_histories[session_id]


# 에이전트에 대화 히스토리 연동
agent_with_history = RunnableWithMessageHistory(
    runnable=agent_executor,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


# ══════════════════════════════════════════════
# 6. 대화 실행
# ══════════════════════════════════════════════
def chat(user_input: str, session_id: str = "default") -> str:
    """사용자 입력에 대한 에이전트 응답을 생성합니다."""
    response = agent_with_history.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}},
    )
    return response["output"]


def interactive_chat():
    """대화형 에이전트를 실행합니다."""
    session_id = "interactive"

    print("=" * 60)
    print("  LangChain 도구 사용 챗봇")
    print("=" * 60)
    print()
    print("  사용 가능한 도구:")
    print("    - 웹 검색 (날씨, 뉴스, 주가 등)")
    print("    - 수학 계산")
    print("    - 현재 날짜/시간 조회")
    print()
    print("  /quit 으로 종료")
    print("─" * 60)

    while True:
        try:
            user_input = input("\n사용자: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n대화를 종료합니다!")
            break

        if not user_input:
            continue
        if user_input in ["/quit", "/exit", "종료"]:
            print("\n대화를 종료합니다!")
            break

        try:
            response = chat(user_input, session_id)
            print(f"\nAI: {response}")
        except Exception as e:
            print(f"\n오류 발생: {e}")


if __name__ == "__main__":
    # 데모 모드: 도구 호출 흐름을 확인
    print("=" * 60)
    print("  데모 모드: 도구 호출 흐름 확인")
    print("=" * 60)

    demo_session = "demo"

    demo_queries = [
        "오늘 날짜가 어떻게 되나요?",
        "123 곱하기 456은 얼마인가요?",
        "서울 날씨 어때?",
        "방금 계산한 결과에 100을 더하면 얼마야?",
    ]

    for query in demo_queries:
        print(f"\n{'='*60}")
        print(f"사용자: {query}")
        print(f"{'='*60}")
        response = chat(query, demo_session)
        print(f"\n최종 답변: {response}")

    # 대화형 모드
    print("\n\n이제 직접 대화해보세요!")
    interactive_chat()

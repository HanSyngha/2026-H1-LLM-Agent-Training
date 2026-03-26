"""
LangChain 대화형 챗봇 예제

LangChain을 사용하여 대화 히스토리를 유지하는 챗봇을 구현합니다.

핵심 개념:
- ChatOpenAI: OpenAI 호환 LLM 모델 래퍼
- ChatPromptTemplate: 프롬프트 템플릿 (시스템 메시지 + 대화 히스토리 + 사용자 입력)
- ChatMessageHistory: 대화 히스토리를 메모리에 저장
- RunnableWithMessageHistory: 체인에 대화 히스토리를 자동으로 주입

실행 방법:
    python chatbot.py

의존성:
    pip install langchain langchain-openai langchain-community
"""

import os
import sys

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

import httpx
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI


# ══════════════════════════════════════════════
# 1. LLM 설정
# ══════════════════════════════════════════════
# ChatOpenAI: OpenAI API 호환 모델을 사용하기 위한 래퍼
# base_url: 사내 게이트웨이 주소
# http_client: 프록시 설정이 포함된 httpx 클라이언트
llm = ChatOpenAI(
    model=DEFAULT_MODEL,
    base_url=GATEWAY_BASE_URL,
    api_key=GATEWAY_API_KEY,
    http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
    temperature=0.7,  # 응답의 창의성 수준 (0.0=결정적, 1.0=창의적)
)


# ══════════════════════════════════════════════
# 2. 프롬프트 템플릿 설정
# ══════════════════════════════════════════════
# ChatPromptTemplate: 대화형 프롬프트를 구성하는 템플릿
# - system: 챗봇의 역할과 행동 지침을 정의하는 시스템 메시지
# - MessagesPlaceholder("history"): 이전 대화 히스토리가 삽입되는 위치
# - human: 현재 사용자 입력이 들어가는 위치
#
# 프롬프트 구조:
#   [시스템 메시지]
#   [이전 대화 히스토리: user1, ai1, user2, ai2, ...]
#   [현재 사용자 입력]
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """당신은 친절하고 유능한 AI 어시스턴트입니다.
다음 지침을 따라주세요:
- 항상 한국어로 답변합니다.
- 이전 대화 내용을 기억하고 맥락에 맞게 답변합니다.
- 모르는 것은 솔직히 모른다고 말합니다.
- 답변은 간결하되 필요한 정보는 충분히 포함합니다.""",
    ),
    # MessagesPlaceholder: 대화 히스토리가 여기에 자동으로 삽입됨
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])


# ══════════════════════════════════════════════
# 3. 체인(Chain) 구성
# ══════════════════════════════════════════════
# LCEL (LangChain Expression Language)을 사용한 체인 구성
# prompt | llm: 프롬프트 → LLM 순서로 실행
chain = prompt | llm


# ══════════════════════════════════════════════
# 4. 대화 히스토리 관리
# ══════════════════════════════════════════════
# 세션별 대화 히스토리를 저장하는 딕셔너리
# 키: session_id, 값: InMemoryChatMessageHistory 객체
message_histories: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """세션 ID에 해당하는 대화 히스토리를 반환합니다.

    없으면 새로 생성합니다. 이 함수는 RunnableWithMessageHistory가
    대화 히스토리를 조회할 때 호출됩니다.
    """
    if session_id not in message_histories:
        message_histories[session_id] = InMemoryChatMessageHistory()
    return message_histories[session_id]


# RunnableWithMessageHistory: 체인에 대화 히스토리를 자동으로 주입하는 래퍼
# - runnable: 원래 체인 (prompt | llm)
# - get_session_history: 세션별 히스토리를 가져오는 함수
# - input_messages_key: 사용자 입력이 들어가는 키 이름
# - history_messages_key: 히스토리가 삽입되는 키 이름
chain_with_history = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


# ══════════════════════════════════════════════
# 5. 대화 실행
# ══════════════════════════════════════════════
def chat(user_input: str, session_id: str = "default") -> str:
    """사용자 입력에 대한 챗봇 응답을 생성합니다.

    Args:
        user_input: 사용자가 입력한 메시지
        session_id: 대화 세션 ID (다중 사용자 지원)

    Returns:
        챗봇의 응답 텍스트
    """
    # config에 session_id를 전달하여 올바른 히스토리 사용
    response = chain_with_history.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}},
    )
    return response.content


def show_history(session_id: str = "default"):
    """현재 세션의 대화 히스토리를 출력합니다."""
    history = get_session_history(session_id)
    print(f"\n{'─'*40}")
    print(f"  대화 히스토리 (세션: {session_id})")
    print(f"{'─'*40}")
    for msg in history.messages:
        role = "사용자" if isinstance(msg, HumanMessage) else "AI"
        # 긴 메시지는 잘라서 출력
        content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        print(f"  [{role}] {content}")
    print(f"{'─'*40}")
    print(f"  총 {len(history.messages)}개 메시지")


# ══════════════════════════════════════════════
# 6. 대화형 루프
# ══════════════════════════════════════════════
def interactive_chat():
    """대화형 챗봇을 실행합니다."""
    session_id = "interactive"

    print("=" * 60)
    print("  LangChain 대화형 챗봇")
    print("=" * 60)
    print()
    print("  명령어:")
    print("    /history  - 대화 히스토리 보기")
    print("    /clear    - 대화 히스토리 초기화")
    print("    /quit     - 종료")
    print()
    print("  대화를 시작하세요!")
    print("─" * 60)

    while True:
        try:
            user_input = input("\n사용자: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n대화를 종료합니다. 감사합니다!")
            break

        if not user_input:
            continue

        # 명령어 처리
        if user_input == "/history":
            show_history(session_id)
            continue
        elif user_input == "/clear":
            message_histories[session_id] = InMemoryChatMessageHistory()
            print("  대화 히스토리가 초기화되었습니다.")
            continue
        elif user_input in ["/quit", "/exit", "종료"]:
            print("\n대화를 종료합니다. 감사합니다!")
            break

        # 챗봇 응답 생성
        try:
            response = chat(user_input, session_id)
            print(f"\nAI: {response}")
        except Exception as e:
            print(f"\n오류 발생: {e}")


if __name__ == "__main__":
    # 데모 모드: 미리 준비된 대화를 실행하고, 그 후 대화형 모드로 전환
    print("=" * 60)
    print("  데모 모드: 대화 히스토리 기능 확인")
    print("=" * 60)

    # 대화 히스토리가 유지되는지 확인하는 데모
    demo_session = "demo"
    demo_queries = [
        "안녕하세요! 제 이름은 홍길동입니다.",
        "제 이름이 뭐라고 했죠?",
        "Python에 대해 간단히 설명해주세요.",
        "방금 설명한 내용을 한 줄로 요약해주세요.",
    ]

    for query in demo_queries:
        print(f"\n사용자: {query}")
        response = chat(query, demo_session)
        print(f"AI: {response}")

    # 대화 히스토리 출력
    show_history(demo_session)

    # 대화형 모드로 전환
    print("\n\n이제 직접 대화해보세요!")
    interactive_chat()

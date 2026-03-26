"""
LangGraph 멀티 에이전트 예제

여러 에이전트가 협력하여 작업을 수행하는 그래프를 구성합니다.

에이전트 구성:
1. Router (라우터): 사용자 질문을 분석하여 적절한 에이전트로 라우팅
2. Researcher (연구원): 정보를 검색하고 수집하는 에이전트
3. Writer (작가): 수집된 정보를 바탕으로 깔끔한 답변을 작성하는 에이전트

그래프 흐름:
    [사용자 입력]
         │
    [router 노드] ← 질문 유형 분석
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 [researcher] [writer] ← 단순 작문은 바로 writer로
    │
    ▼
 [writer] ← 연구 결과를 바탕으로 작성
    │
    ▼
  [END]

실행 방법:
    python langgraph_multi_agent.py

의존성:
    pip install langgraph langchain-openai langchain-core
"""

import os
import sys
from typing import Annotated, Literal, TypedDict

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

import httpx
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


# ══════════════════════════════════════════════
# 1. 상태(State) 정의
# ══════════════════════════════════════════════
# 멀티 에이전트에서는 에이전트 간에 공유할 정보를 상태에 포함합니다.
class MultiAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # 현재 질문의 유형 (router가 결정)
    query_type: str
    # 연구원이 수집한 정보
    research_result: str
    # 최종 답변
    final_answer: str


# ══════════════════════════════════════════════
# 2. LLM 설정
# ══════════════════════════════════════════════
llm = ChatOpenAI(
    model=DEFAULT_MODEL,
    base_url=GATEWAY_BASE_URL,
    api_key=GATEWAY_API_KEY,
    http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
)


# ══════════════════════════════════════════════
# 3. 각 에이전트(노드) 정의
# ══════════════════════════════════════════════


def router_node(state: MultiAgentState) -> dict:
    """라우터 노드: 사용자 질문을 분석하여 적절한 에이전트를 결정합니다.

    질문 유형:
    - "research": 정보 검색/조사가 필요한 질문 → researcher로 라우팅
    - "writing": 글 작성, 요약, 번역 등 → 바로 writer로 라우팅
    """
    print("\n  [라우터] 질문 유형 분석 중...")

    # 마지막 사용자 메시지 추출
    user_message = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break

    # LLM을 사용하여 질문 유형 분류
    classification_prompt = f"""사용자 질문을 분석하여 다음 두 유형 중 하나로 분류하세요.

질문: "{user_message}"

유형:
- "research": 사실 확인, 정보 검색, 데이터 조회가 필요한 질문
- "writing": 글 작성, 요약, 번역, 창작 등 텍스트 생성 질문

반드시 "research" 또는 "writing" 중 하나만 답하세요. 다른 말은 하지 마세요."""

    response = llm.invoke([HumanMessage(content=classification_prompt)])
    query_type = response.content.strip().lower()

    # "research" 또는 "writing" 외의 값이 나오면 기본값 설정
    if "research" in query_type:
        query_type = "research"
    else:
        query_type = "writing"

    print(f"  [라우터] 분류 결과: {query_type}")
    return {"query_type": query_type}


def researcher_node(state: MultiAgentState) -> dict:
    """연구원 노드: 정보를 검색하고 수집합니다.

    사용자의 질문에 대해 관련 정보를 조사하고,
    핵심 내용을 정리하여 writer 노드에 전달합니다.
    """
    print("\n  [연구원] 정보 수집 중...")

    user_message = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break

    research_prompt = f"""당신은 전문 연구원입니다. 다음 질문에 대해 조사를 수행하세요.

질문: "{user_message}"

아래 형식으로 조사 결과를 정리해주세요:
1. 핵심 사실 (3-5개 항목)
2. 관련 배경 정보
3. 추가 참고 사항

조사 결과를 한국어로 상세하게 작성해주세요."""

    response = llm.invoke([
        SystemMessage(content="당신은 꼼꼼하고 정확한 정보 수집 전문가입니다."),
        HumanMessage(content=research_prompt),
    ])

    research_result = response.content
    print(f"  [연구원] 조사 완료 (결과 길이: {len(research_result)}자)")
    return {"research_result": research_result}


def writer_node(state: MultiAgentState) -> dict:
    """작가 노드: 최종 답변을 작성합니다.

    연구원의 조사 결과가 있으면 이를 바탕으로,
    없으면 직접 답변을 작성합니다.
    """
    print("\n  [작가] 답변 작성 중...")

    user_message = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break

    research_result = state.get("research_result", "")

    if research_result:
        # 연구 결과를 바탕으로 답변 작성
        writing_prompt = f"""다음 연구 결과를 바탕으로 사용자 질문에 대한 답변을 작성해주세요.

사용자 질문: "{user_message}"

연구 결과:
{research_result}

답변 작성 지침:
- 연구 결과를 바탕으로 정확하고 이해하기 쉬운 답변 작성
- 불필요한 전문 용어는 피하고 핵심을 간결하게 전달
- 한국어로 작성"""
    else:
        # 연구 결과 없이 직접 답변 (글쓰기 유형)
        writing_prompt = f"""다음 요청에 대한 답변을 작성해주세요.

요청: "{user_message}"

답변 작성 지침:
- 요청에 맞는 적절한 형식과 톤으로 작성
- 한국어로 작성
- 깔끔하고 읽기 쉬운 구조로 작성"""

    response = llm.invoke([
        SystemMessage(content="당신은 명확하고 읽기 쉬운 글을 쓰는 전문 작가입니다."),
        HumanMessage(content=writing_prompt),
    ])

    final_answer = response.content
    print(f"  [작가] 답변 작성 완료 (길이: {len(final_answer)}자)")

    # 최종 답변을 메시지로도 추가
    return {
        "final_answer": final_answer,
        "messages": [AIMessage(content=final_answer)],
    }


# ══════════════════════════════════════════════
# 4. 라우팅 함수 (조건부 엣지)
# ══════════════════════════════════════════════
def route_query(state: MultiAgentState) -> str:
    """질문 유형에 따라 다음 노드를 결정합니다.

    Returns:
        "researcher": 정보 조사가 필요한 경우
        "writer": 바로 글쓰기가 가능한 경우
    """
    query_type = state.get("query_type", "writing")
    print(f"  [라우팅] query_type={query_type}")
    return query_type


# ══════════════════════════════════════════════
# 5. 그래프 구성
# ══════════════════════════════════════════════
graph = StateGraph(MultiAgentState)

# 노드 추가
graph.add_node("router", router_node)
graph.add_node("researcher", researcher_node)
graph.add_node("writer", writer_node)

# 시작점 설정: router가 가장 먼저 실행
graph.set_entry_point("router")

# 조건부 엣지: router → (researcher 또는 writer)
# router의 결과(query_type)에 따라 분기
graph.add_conditional_edges(
    "router",       # 출발 노드
    route_query,    # 조건 판단 함수
    {
        "research": "researcher",  # 조사 필요 → researcher
        "writing": "writer",       # 글쓰기 → writer
    },
)

# 일반 엣지: researcher → writer (조사 후 항상 작성)
graph.add_edge("researcher", "writer")

# 일반 엣지: writer → END (작성 완료 후 종료)
graph.add_edge("writer", END)

# 그래프 컴파일
app = graph.compile()


# ══════════════════════════════════════════════
# 6. 그래프 구조 시각화
# ══════════════════════════════════════════════
def print_graph_structure():
    """그래프 구조를 ASCII로 출력합니다."""
    print("""
    ┌───────────────────────────────────────────────┐
    │       LangGraph 멀티 에이전트 구조             │
    └───────────────────────────────────────────────┘

              ┌──────────┐
              │  START   │
              └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │  router  │ (질문 유형 분석)
              └────┬─────┘
                   │
          (조건부 엣지: route_query)
                   │
          ┌────────┴────────┐
          │                 │
    query_type=         query_type=
    "research"          "writing"
          │                 │
          ▼                 │
    ┌────────────┐          │
    │ researcher │          │
    │ (정보 수집) │          │
    └─────┬──────┘          │
          │                 │
          └────────┬────────┘
                   │
                   ▼
              ┌──────────┐
              │  writer  │ (답변 작성)
              └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │   END    │
              └──────────┘
    """)


# ══════════════════════════════════════════════
# 7. 실행
# ══════════════════════════════════════════════
def run_multi_agent(query: str):
    """멀티 에이전트를 실행하고 결과를 출력합니다."""
    print(f"\n{'='*60}")
    print(f"  질문: {query}")
    print(f"{'='*60}")

    initial_state = {
        "messages": [HumanMessage(content=query)],
        "query_type": "",
        "research_result": "",
        "final_answer": "",
    }

    result = app.invoke(initial_state)

    print(f"\n{'─'*60}")
    print(f"  최종 답변")
    print(f"{'─'*60}")
    print(result["final_answer"])
    print(f"{'─'*60}")

    return result


if __name__ == "__main__":
    print_graph_structure()

    print("\n" + "=" * 60)
    print("  멀티 에이전트 시스템 실행")
    print("=" * 60)

    # 테스트 1: 정보 검색이 필요한 질문 → router → researcher → writer
    run_multi_agent("Python의 GIL(Global Interpreter Lock)이 뭔지 설명해줘")

    # 테스트 2: 글쓰기 질문 → router → writer
    run_multi_agent("회의 참석을 요청하는 이메일을 작성해줘")

    # 테스트 3: 조사 + 정리가 필요한 질문
    run_multi_agent("마이크로서비스 아키텍처의 장단점을 분석해줘")

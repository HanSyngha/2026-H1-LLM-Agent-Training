"""
LangGraph 실습 정답: 조건 분기 에이전트

질문 유형을 분류하고, 유형에 따라 다른 처리 경로를 타는 에이전트입니다.
최소 3개 노드와 조건부 엣지(conditional edge)를 포함합니다.

그래프 구조:
    [START]
       |
    [classifier] ← 질문 유형을 분류합니다
       |
    (조건부 엣지)
       |─── "technical" ──→ [technical_expert]  ──→ [END]
       |─── "creative"  ──→ [creative_writer]   ──→ [END]
       └─── "general"   ──→ [general_assistant] ──→ [END]

실행 방법:
    python exercise_solution.py

의존성:
    pip install langgraph langchain-openai langchain-core
"""

import os
import sys
from typing import Annotated, TypedDict

# 공통 설정 로드
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

import httpx
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


# ============================================================
# 1. State 정의 - 그래프 전체에서 공유되는 데이터 구조입니다
# ============================================================

class AgentState(TypedDict):
    """에이전트의 상태를 정의합니다."""
    messages: Annotated[list[BaseMessage], add_messages]
    query_type: str  # 질문 유형: "technical", "creative", "general"


# ============================================================
# 2. LLM 설정 - 사내 게이트웨이를 사용합니다
# ============================================================

llm = ChatOpenAI(
    model=DEFAULT_MODEL,
    base_url=GATEWAY_BASE_URL,
    api_key=GATEWAY_API_KEY,
    http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
    temperature=0.7,
)


# ============================================================
# 3. 노드(Node) 정의 - 최소 3개 이상 구현합니다
# ============================================================

def classifier_node(state: AgentState) -> dict:
    """분류기 노드: 질문 유형을 분석하여 분류합니다.

    LLM을 호출하여 질문이 기술/코딩, 창작/글쓰기, 일반 대화 중
    어떤 유형에 해당하는지 판단합니다.
    """
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    # LLM에게 질문 유형을 분류하도록 요청합니다
    classification_prompt = SystemMessage(content="""당신은 질문 분류 전문가입니다.
사용자의 질문을 분석하여 다음 3가지 유형 중 하나로 분류하세요:

- "technical": 프로그래밍, 코딩, 기술, IT, 소프트웨어, 알고리즘, 데이터베이스 관련 질문
- "creative": 글쓰기, 시, 소설, 스토리, 창작, 작문, 마케팅 문구 관련 요청
- "general": 일반적인 질문, 인사, 상식, 일상 대화, 기타

반드시 "technical", "creative", "general" 중 하나만 답하세요. 다른 텍스트는 포함하지 마세요.""")

    response = llm.invoke([classification_prompt, HumanMessage(content=last_message)])
    query_type = response.content.strip().lower()

    # 유효한 유형인지 확인합니다
    valid_types = ["technical", "creative", "general"]
    if query_type not in valid_types:
        query_type = "general"

    print(f"  [분류기] 질문 유형: {query_type}")
    return {"query_type": query_type}


def technical_expert_node(state: AgentState) -> dict:
    """기술 전문가 노드: 기술/코딩 관련 질문을 처리합니다.

    프로그래밍, 알고리즘, 소프트웨어 아키텍처 등에 대해
    전문적이고 정확한 답변을 생성합니다.
    """
    messages = state["messages"]

    system_prompt = SystemMessage(content="""당신은 시니어 소프트웨어 엔지니어이자 기술 전문가입니다.
기술 질문에 대해 정확하고 실용적인 답변을 제공하세요.

답변 시 다음 규칙을 따르세요:
1. 코드 예시가 필요하면 반드시 포함하세요
2. 핵심 개념을 먼저 설명하고 세부 사항을 이어가세요
3. 장단점이나 주의사항이 있으면 언급하세요
4. 한국어로 답변하세요""")

    response = llm.invoke([system_prompt, *messages])
    print(f"  [기술 전문가] 답변 생성 완료")
    return {"messages": [response]}


def creative_writer_node(state: AgentState) -> dict:
    """창작 작가 노드: 글쓰기/창작 관련 요청을 처리합니다.

    시, 소설, 마케팅 문구, 스토리텔링 등 창의적인 콘텐츠를 생성합니다.
    """
    messages = state["messages"]

    system_prompt = SystemMessage(content="""당신은 재능 있는 창작 작가입니다.
사용자의 요청에 따라 창의적이고 감성적인 글을 작성합니다.

답변 시 다음 규칙을 따르세요:
1. 생생한 표현과 비유를 활용하세요
2. 독자의 감정을 자극하는 문체를 사용하세요
3. 요청된 형식(시, 소설, 에세이 등)에 맞게 작성하세요
4. 한국어로 답변하세요""")

    response = llm.invoke([system_prompt, *messages])
    print(f"  [창작 작가] 답변 생성 완료")
    return {"messages": [response]}


def general_assistant_node(state: AgentState) -> dict:
    """일반 어시스턴트 노드: 일반적인 질문/대화를 처리합니다.

    상식, 일상 대화, 조언 등 범용적인 답변을 생성합니다.
    """
    messages = state["messages"]

    system_prompt = SystemMessage(content="""당신은 친절하고 도움이 되는 AI 어시스턴트입니다.
사용자의 일반적인 질문에 명확하고 이해하기 쉽게 답변합니다.

답변 시 다음 규칙을 따르세요:
1. 친절하고 자연스러운 말투를 사용하세요
2. 필요하면 예시를 들어 설명하세요
3. 불확실한 정보는 명시적으로 밝히세요
4. 한국어로 답변하세요""")

    response = llm.invoke([system_prompt, *messages])
    print(f"  [일반 어시스턴트] 답변 생성 완료")
    return {"messages": [response]}


# ============================================================
# 4. 조건부 라우팅 함수 - 질문 유형에 따라 경로를 결정합니다
# ============================================================

def route_by_query_type(state: AgentState) -> str:
    """분류 결과에 따라 다음 노드를 결정합니다.

    Returns:
        "technical": 기술 전문가 노드로 이동
        "creative": 창작 작가 노드로 이동
        "general": 일반 어시스턴트 노드로 이동
    """
    query_type = state.get("query_type", "general")
    print(f"  [라우팅] '{query_type}' 경로로 분기합니다")
    return query_type


# ============================================================
# 5. 그래프 구성 - 노드와 엣지를 연결합니다
# ============================================================

# 그래프를 생성합니다
graph = StateGraph(AgentState)

# 노드를 추가합니다 (3개 + 분류기 = 4개)
graph.add_node("classifier", classifier_node)
graph.add_node("technical", technical_expert_node)
graph.add_node("creative", creative_writer_node)
graph.add_node("general", general_assistant_node)

# 시작점을 설정합니다 (항상 분류기부터 시작)
graph.set_entry_point("classifier")

# 조건부 엣지를 추가합니다 (분류 결과에 따라 다른 노드로 분기)
graph.add_conditional_edges(
    "classifier",
    route_by_query_type,
    {
        "technical": "technical",
        "creative": "creative",
        "general": "general",
    },
)

# 각 전문가 노드에서 종료 엣지를 추가합니다
graph.add_edge("technical", END)
graph.add_edge("creative", END)
graph.add_edge("general", END)

# 그래프를 컴파일합니다
app = graph.compile()


# ============================================================
# 6. 실행 함수
# ============================================================

def run_agent(query: str) -> str:
    """에이전트를 실행하고 최종 답변을 반환합니다."""
    print(f"\n{'=' * 60}")
    print(f"  질문: {query}")
    print(f"{'=' * 60}")

    initial_state = {"messages": [HumanMessage(content=query)], "query_type": ""}
    result = app.invoke(initial_state)

    final_message = result["messages"][-1]
    print(f"\n답변:\n{final_message.content}")
    return final_message.content


def print_graph_structure():
    """그래프 구조를 ASCII로 출력합니다."""
    print("""
    ┌─────────────────────────────────────────────────┐
    │        LangGraph 조건 분기 에이전트 구조          │
    └─────────────────────────────────────────────────┘

             ┌────────────┐
             │   START    │
             └─────┬──────┘
                   │
                   ▼
             ┌────────────┐
             │ classifier │  (질문 유형 분류)
             └─────┬──────┘
                   │
          (조건부 엣지: route_by_query_type)
                   │
         ┌─────────┼─────────┐
         │         │         │
         ▼         ▼         ▼
    ┌──────────┐ ┌────────┐ ┌──────────┐
    │technical │ │creative│ │ general  │
    │ expert   │ │ writer │ │assistant │
    └────┬─────┘ └───┬────┘ └────┬─────┘
         │           │           │
         └───────────┼───────────┘
                     │
                     ▼
                ┌─────────┐
                │   END   │
                └─────────┘
    """)


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    # 그래프 구조를 출력합니다
    print_graph_structure()

    print("=" * 60)
    print("  LangGraph 조건 분기 에이전트 실행")
    print("=" * 60)

    # 테스트 1: 기술 질문 → technical_expert 경로
    run_agent("Python에서 비동기 프로그래밍의 async/await 패턴을 설명해줘")

    # 테스트 2: 창작 요청 → creative_writer 경로
    run_agent("봄을 주제로 짧은 시를 하나 써줘")

    # 테스트 3: 일반 질문 → general_assistant 경로
    run_agent("오늘 점심 뭐 먹을까? 추천해줘")

    # 테스트 4: 기술 질문 (코딩)
    run_agent("LangGraph에서 조건부 엣지를 사용하는 방법을 알려줘")

    print(f"\n{'=' * 60}")
    print("  모든 테스트 완료!")
    print(f"{'=' * 60}")

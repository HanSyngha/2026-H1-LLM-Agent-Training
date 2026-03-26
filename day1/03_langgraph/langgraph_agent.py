"""
LangGraph 에이전트 예제

LangGraph는 LLM 애플리케이션을 그래프(Graph) 구조로 구현하는 프레임워크입니다.
복잡한 에이전트 워크플로우를 명확하게 설계하고 제어할 수 있습니다.

핵심 개념:
1. State (상태): 그래프 전체에서 공유되는 데이터 구조. 각 노드가 읽고 쓸 수 있음.
2. Node (노드): 그래프의 각 처리 단계. 실제 로직이 실행되는 곳.
3. Edge (엣지): 노드 간의 연결. 한 노드에서 다음 노드로의 전이를 정의.
4. Conditional Edge (조건부 엣지): 상태에 따라 다른 노드로 분기하는 엣지.

그래프 구조:
    [사용자 입력]
         |
    [agent 노드] ← LLM이 도구 호출 여부 판단
         |
    (조건부 엣지) → 도구 호출 필요? → [tools 노드] → [agent 노드]로 돌아감
         |
    도구 호출 불필요 → END (최종 답변)

실행 방법:
    python langgraph_agent.py

의존성:
    pip install langgraph langchain-openai langchain-core
"""

import json
import os
import sys
from typing import Annotated, TypedDict

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

import httpx
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


# ══════════════════════════════════════════════
# 1. State (상태) 정의
# ══════════════════════════════════════════════
# State는 그래프 전체에서 공유되는 데이터 구조입니다.
# TypedDict를 사용하여 타입을 명시하면 코드 가독성과 안전성이 높아집니다.
#
# Annotated[list, add_messages]:
#   - 메시지 리스트에 새 메시지가 추가될 때 기존 리스트에 append됨
#   - add_messages는 LangGraph의 reducer 함수로, 메시지 병합 로직을 처리
#   - 이를 통해 대화 히스토리가 자동으로 관리됨
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ══════════════════════════════════════════════
# 2. 도구(Tool) 정의
# ══════════════════════════════════════════════
# @tool 데코레이터로 LangChain 도구를 정의합니다.
# LangGraph에서 도구는 LangChain의 Tool 인터페이스를 사용합니다.


@tool
def search(query: str) -> str:
    """웹에서 정보를 검색합니다. 최신 뉴스, 사실 확인, 일반 지식 검색에 사용합니다.

    Args:
        query: 검색할 키워드 또는 문장
    """
    # 더미 검색 결과 (실제로는 검색 API 호출)
    search_results = {
        "서울 날씨": "서울의 현재 기온은 15도이며 맑은 날씨입니다.",
        "파이썬": "Python은 1991년 귀도 반 로섬이 개발한 프로그래밍 언어입니다.",
        "LangGraph": "LangGraph는 LangChain 팀이 만든 에이전트 프레임워크로, 그래프 기반 워크플로우를 지원합니다.",
    }
    for key, value in search_results.items():
        if key in query:
            return value
    return f"'{query}'에 대한 검색 결과: 관련 정보를 찾았습니다. 해당 주제에 대한 일반적인 정보를 제공합니다."


@tool
def calculator(expression: str) -> str:
    """수학 계산을 수행합니다. 사칙연산, 거듭제곱 등의 수학 표현식을 계산합니다.

    Args:
        expression: 계산할 수학 표현식 (예: "3 + 5", "100 * 2.5", "2 ** 10")
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
def get_current_time() -> str:
    """현재 날짜와 시간을 반환합니다."""
    from datetime import datetime

    now = datetime.now()
    return f"현재 시각: {now.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}"


# 도구 리스트
tools = [search, calculator, get_current_time]

# ══════════════════════════════════════════════
# 3. LLM 설정
# ══════════════════════════════════════════════
# ChatOpenAI를 사내 게이트웨이로 설정
# bind_tools(): LLM에 사용 가능한 도구를 알려주는 메서드
# 이를 통해 LLM이 응답 시 도구 호출을 포함할 수 있게 됨

llm = ChatOpenAI(
    model=DEFAULT_MODEL,
    base_url=GATEWAY_BASE_URL,
    api_key=GATEWAY_API_KEY,
    http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
)

# LLM에 도구를 바인딩
# bind_tools 후에는 LLM이 응답에 tool_calls를 포함할 수 있음
llm_with_tools = llm.bind_tools(tools)


# ══════════════════════════════════════════════
# 4. Node (노드) 정의
# ══════════════════════════════════════════════
# 노드는 그래프의 각 처리 단계를 나타내는 함수입니다.
# 입력: 현재 State → 출력: 업데이트할 State 부분


def agent_node(state: AgentState) -> dict:
    """에이전트 노드: LLM을 호출하여 응답을 생성합니다.

    이 노드에서 LLM은 두 가지 중 하나를 결정합니다:
    1. 도구를 호출해야 하는 경우 → tool_calls가 포함된 AIMessage 반환
    2. 직접 답변할 수 있는 경우 → 텍스트가 포함된 AIMessage 반환
    """
    messages = state["messages"]
    # LLM 호출 (도구 바인딩된 모델 사용)
    response = llm_with_tools.invoke(messages)
    # 반환값은 State의 messages에 추가됨 (add_messages reducer에 의해)
    return {"messages": [response]}


# ToolNode: 도구 호출을 자동으로 처리하는 내장 노드
# AIMessage의 tool_calls를 파싱하여 해당 도구를 실행하고,
# ToolMessage로 결과를 반환합니다.
tool_node = ToolNode(tools)


# ══════════════════════════════════════════════
# 5. Conditional Edge (조건부 엣지) 정의
# ══════════════════════════════════════════════
# 조건부 엣지는 현재 상태를 보고 다음에 어떤 노드로 갈지 결정합니다.
# 이것이 LangGraph의 핵심 - 그래프의 흐름을 동적으로 제어합니다.


def should_continue(state: AgentState) -> str:
    """에이전트의 마지막 메시지를 확인하여 다음 단계를 결정합니다.

    Returns:
        "tools": LLM이 도구 호출을 요청한 경우 → tools 노드로 이동
        "end": LLM이 최종 답변을 생성한 경우 → 종료
    """
    last_message = state["messages"][-1]

    # AIMessage에 tool_calls가 있으면 도구 호출이 필요
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        print(f"  [조건 분기] 도구 호출 필요 → tools 노드로 이동")
        for tc in last_message.tool_calls:
            print(f"    - {tc['name']}({tc['args']})")
        return "tools"
    else:
        print(f"  [조건 분기] 최종 답변 생성 → 종료")
        return "end"


# ══════════════════════════════════════════════
# 6. 그래프(Graph) 구성
# ══════════════════════════════════════════════
# StateGraph: 상태 기반 그래프를 구성하는 클래스
# 노드를 추가하고, 엣지로 연결하여 워크플로우를 정의합니다.

# 그래프 생성 (AgentState를 상태 타입으로 사용)
graph = StateGraph(AgentState)

# 노드 추가
# add_node("노드이름", 노드함수): 그래프에 노드를 등록
graph.add_node("agent", agent_node)  # LLM 호출 노드
graph.add_node("tools", tool_node)   # 도구 실행 노드

# 시작점 설정
# set_entry_point: 그래프 실행 시 가장 먼저 실행될 노드
graph.set_entry_point("agent")

# 조건부 엣지 추가
# add_conditional_edges: 노드 실행 후 조건에 따라 다른 노드로 분기
# - "agent" 노드 실행 후 → should_continue 함수로 판단
# - "tools" → tools 노드로 이동
# - "end" → END (그래프 종료)
graph.add_conditional_edges(
    "agent",           # 출발 노드
    should_continue,   # 조건 판단 함수
    {
        "tools": "tools",  # "tools" 반환 시 → tools 노드
        "end": END,         # "end" 반환 시 → 종료
    },
)

# 일반 엣지 추가
# add_edge: 무조건적인 연결 (조건 없이 항상 다음 노드로 이동)
# tools 노드 실행 후 → 항상 agent 노드로 돌아감
# (도구 결과를 LLM에 다시 전달하여 최종 답변 생성)
graph.add_edge("tools", "agent")

# 그래프 컴파일
# compile(): 그래프를 실행 가능한 형태로 변환
app = graph.compile()


# ══════════════════════════════════════════════
# 7. 그래프 구조 시각화 (ASCII)
# ══════════════════════════════════════════════
def print_graph_structure():
    """그래프 구조를 ASCII로 출력합니다."""
    print("""
    ┌─────────────────────────────────────────┐
    │          LangGraph 에이전트 구조          │
    └─────────────────────────────────────────┘

         ┌──────────┐
         │  START   │
         └────┬─────┘
              │
              ▼
         ┌──────────┐
    ┌───▶│  agent   │ (LLM 호출)
    │    └────┬─────┘
    │         │
    │    (조건부 엣지: should_continue)
    │         │
    │    ┌────┴────┐
    │    │         │
    │    ▼         ▼
    │ ┌──────┐  ┌─────┐
    │ │tools │  │ END │ (최종 답변)
    │ └──┬───┘  └─────┘
    │    │
    └────┘ (도구 결과를 agent에 다시 전달)
    """)


# ══════════════════════════════════════════════
# 8. 실행
# ══════════════════════════════════════════════
def run_agent(query: str):
    """에이전트를 실행하고 결과를 출력합니다.

    Args:
        query: 사용자 질문
    """
    print(f"\n{'='*60}")
    print(f"  질문: {query}")
    print(f"{'='*60}")

    # 초기 상태 설정 (사용자 메시지)
    initial_state = {"messages": [HumanMessage(content=query)]}

    # 그래프 실행
    # invoke: 동기 실행 (모든 노드를 순차적으로 처리)
    # stream: 스트리밍 실행 (각 노드의 결과를 실시간으로 받음)
    result = app.invoke(initial_state)

    # 최종 메시지 (마지막 AIMessage) 출력
    final_message = result["messages"][-1]
    print(f"\n답변: {final_message.content}")

    return result


if __name__ == "__main__":
    # 그래프 구조 출력
    print_graph_structure()

    # 다양한 질문으로 에이전트 테스트
    print("\n" + "=" * 60)
    print("  LangGraph 에이전트 실행")
    print("=" * 60)

    # 테스트 1: 검색이 필요한 질문
    run_agent("LangGraph가 뭐야?")

    # 테스트 2: 계산이 필요한 질문
    run_agent("2의 10제곱은 얼마야?")

    # 테스트 3: 복합 질문 (여러 도구 사용)
    run_agent("현재 시간 알려주고, 123 * 456 계산해줘")

    # 테스트 4: 도구가 필요 없는 질문
    run_agent("안녕하세요, 자기소개 해주세요.")

# 실습: LangGraph로 조건 분기 에이전트 만들기

## 목표

LangGraph를 사용하여 사용자 질문 유형에 따라 서로 다른 처리 경로를 타는 에이전트를 구현합니다.

---

## 요구사항

### 1. 최소 3개의 노드(Node) 구현

예시 구성:

| 노드 이름 | 역할 | 설명 |
|-----------|------|------|
| classifier | 분류기 | 질문 유형을 분석하고 분류 |
| technical_expert | 기술 전문가 | 기술/코딩 관련 질문 처리 |
| general_assistant | 일반 어시스턴트 | 일반 질문/대화 처리 |
| creative_writer | 창작 작가 | 글쓰기/창작 요청 처리 |

또는 자유롭게 구성해도 됩니다.

### 2. 조건부 엣지(Conditional Edge) 포함

- classifier 노드의 결과에 따라 다른 노드로 분기
- 최소 2개 이상의 분기 경로

### 3. State 설계

```python
class MyState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    query_type: str       # 질문 유형
    # ... 필요한 상태 추가
```

---

## 체크리스트

- [ ] StateGraph로 그래프가 정의되어 있음
- [ ] 3개 이상의 노드가 구현됨
- [ ] 조건부 엣지가 1개 이상 포함됨
- [ ] 각 노드의 역할이 명확히 구분됨
- [ ] 그래프가 컴파일되고 실행 가능함
- [ ] 다양한 유형의 질문에 대해 올바른 경로로 분기됨

---

## 힌트

### 그래프 구성 기본 패턴
```python
graph = StateGraph(MyState)

# 노드 추가
graph.add_node("classifier", classifier_node)
graph.add_node("expert", expert_node)
graph.add_node("assistant", assistant_node)

# 시작점
graph.set_entry_point("classifier")

# 조건부 엣지
graph.add_conditional_edges(
    "classifier",
    route_function,  # 상태를 보고 다음 노드 이름을 반환하는 함수
    {
        "technical": "expert",
        "general": "assistant",
    },
)

# 종료 엣지
graph.add_edge("expert", END)
graph.add_edge("assistant", END)

# 컴파일
app = graph.compile()
```

### 조건부 라우팅 함수 작성법
```python
def route_function(state: MyState) -> str:
    """상태를 분석하여 다음 노드 이름을 반환합니다."""
    query_type = state["query_type"]
    if query_type == "technical":
        return "technical"
    elif query_type == "creative":
        return "creative"
    else:
        return "general"
```

### 노드에서 LLM 호출
```python
def my_node(state: MyState) -> dict:
    """노드 함수는 State를 입력받아 업데이트할 부분을 반환합니다."""
    messages = state["messages"]
    response = llm.invoke([
        SystemMessage(content="당신은 ...입니다."),
        *messages,
    ])
    return {"messages": [response]}
```

---

## 보너스 도전

- 노드 간 순환(loop) 추가: 답변 품질이 낮으면 다시 처리하는 자기 검증 루프
- 3개 이상의 분기 경로 구현
- 그래프 실행 과정을 스트리밍으로 출력하기 (`app.stream()` 사용)
- 그래프를 이미지로 시각화하기 (`app.get_graph().draw_mermaid()` 사용)

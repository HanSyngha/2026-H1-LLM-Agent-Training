# 실습: LangChain 대화형 챗봇 만들기

## 목표

LangChain을 사용하여 대화 히스토리를 유지하고, 도구를 활용할 수 있는 챗봇을 구현합니다.

---

## 요구사항

### 1. 메모리 기반 대화 유지

- 이전 대화 내용을 기억하는 챗봇 구현
- 사용자가 이전에 말한 내용을 참조할 수 있어야 함
- 예: "제 이름은 홍길동이에요" → (이후) "제 이름이 뭐였죠?" → "홍길동"

### 2. 최소 1개 도구 연동

자신만의 도구를 1개 이상 만들어 에이전트에 연결하세요.

**아이디어 예시:**
- 사내 공지사항 검색 도구
- 번역 도구
- 일정 관리 도구
- 코드 실행 도구

### 3. 시스템 프롬프트 커스터마이징

챗봇의 성격과 역할을 정의하는 시스템 프롬프트를 작성하세요.

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 ... 입니다. ..."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
```

---

## 체크리스트

- [ ] ChatOpenAI가 사내 게이트웨이를 통해 연결됨
- [ ] 대화 히스토리가 유지됨 (이전 대화를 기억)
- [ ] 최소 1개 이상의 커스텀 도구가 구현됨
- [ ] 시스템 프롬프트가 커스터마이징됨
- [ ] 대화형 루프 (input)가 구현됨
- [ ] 도구가 필요한 질문에서 올바르게 도구를 호출함

---

## 힌트

### 기본 챗봇 구조
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 1. LLM 설정
llm = ChatOpenAI(model=DEFAULT_MODEL, base_url=GATEWAY_BASE_URL, ...)

# 2. 프롬프트 설정
prompt = ChatPromptTemplate.from_messages([
    ("system", "시스템 메시지"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

# 3. 체인 구성
chain = prompt | llm

# 4. 히스토리 연동
chain_with_history = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)
```

### 커스텀 도구 만들기
```python
from langchain_core.tools import tool

@tool
def my_custom_tool(param: str) -> str:
    """도구 설명 (LLM이 이 설명을 읽고 호출 여부를 결정합니다)

    Args:
        param: 파라미터 설명
    """
    # 도구 로직 구현
    return "결과"
```

### 에이전트에 도구 연결하기
```python
from langchain.agents import AgentExecutor, create_tool_calling_agent

# agent_scratchpad이 프롬프트에 있어야 함
agent = create_tool_calling_agent(llm, [my_tool], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[my_tool], verbose=True)
```

---

## 보너스 도전

- 여러 세션을 관리하여 다중 사용자 지원
- 대화 히스토리를 파일로 저장/불러오기
- 스트리밍 응답 구현 (`stream()` 메서드 사용)
- 시스템 프롬프트를 동적으로 변경할 수 있게 구현

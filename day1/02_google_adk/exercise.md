# 실습: ADK로 멀티 도구 에이전트 만들기

## 목표

Google ADK를 사용하여 여러 도구를 가진 에이전트를 만들고, 대화형으로 동작하게 합니다.

---

## 요구사항

### 1. 커스텀 도구 2개 이상 정의

자신만의 Python 함수를 만들어 도구로 등록하세요.

**아이디어 예시:**
- `search_menu(restaurant)`: 식당 메뉴 검색
- `book_meeting(date, time, participants)`: 회의 예약
- `get_exchange_rate(currency)`: 환율 조회
- `summarize_text(text)`: 텍스트 요약
- `translate(text, lang)`: 번역

### 2. ADK Agent 생성

```python
agent = Agent(
    name="my-agent",
    model=model,
    instruction="에이전트의 역할과 행동 지침...",
    tools=[tool1, tool2, ...],
)
```

### 3. 대화형 인터페이스 구현

```python
# 대화 루프 예시
while True:
    user_input = input("사용자: ")
    if user_input.lower() in ["종료", "quit", "exit"]:
        break
    # 에이전트 실행 및 응답 출력
```

---

## 체크리스트

- [ ] 2개 이상의 커스텀 도구가 정의되어 있음
- [ ] 각 도구의 docstring이 명확하게 작성됨
- [ ] Agent의 instruction이 도구 활용 방법을 포함함
- [ ] 대화형 루프가 구현되어 사용자 입력을 받을 수 있음
- [ ] 대화 컨텍스트가 유지됨 (이전 대화를 기억)
- [ ] 에이전트가 적절한 도구를 선택하여 호출함

---

## 힌트

### 대화 루프 구현
```python
async def interactive_loop():
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="my-app", session_service=session_service)
    session = await session_service.create_session(app_name="my-app", user_id="user-001")

    print("대화를 시작합니다. '종료'를 입력하면 끝납니다.")
    while True:
        user_input = input("\n사용자: ")
        if user_input.strip().lower() in ["종료", "quit", "exit"]:
            print("대화를 종료합니다.")
            break

        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)],
        )

        async for event in runner.run_async(
            user_id="user-001",
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"에이전트: {part.text}")
```

### LiteLlm 모델 설정
```python
from google.adk.models.lite_llm import LiteLlm

# 사내 게이트웨이 사용 시 환경 변수 설정 필요
os.environ["OPENAI_API_KEY"] = GATEWAY_API_KEY
os.environ["OPENAI_API_BASE"] = GATEWAY_BASE_URL

model = LiteLlm(model=f"openai/{DEFAULT_MODEL}")
```

---

## 보너스 도전

- MCP 서버의 도구를 MCPToolset으로 함께 사용해보기
- 도구 호출 로그를 파일에 기록하기
- 에이전트의 instruction을 다양하게 바꿔보며 행동 변화 관찰

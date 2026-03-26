# 실습: 나만의 Agent Loop 구현하기

## 목표
프레임워크 없이 `requests` 라이브러리만 사용하여 **완전한 Agent Loop**를 구현합니다.

---

## 요구사항

### 필수 (기본)

1. **최소 2개 이상의 도구(Tool) 구현**
   - 각 도구는 독립적인 Python 함수로 구현
   - OpenAI Tool Schema (JSON Schema) 형식으로 정의
   - 예시: 계산기, 날씨 조회, 파일 읽기, 번역, 단위 변환 등

2. **Agent Loop 구현**
   - `requests`로 `/v1/chat/completions` 직접 호출
   - 응답에서 `tool_calls` 확인
   - 도구 실행 후 결과를 `role: "tool"` 메시지로 추가
   - 도구 호출이 없을 때까지 반복 (루프)
   - 무한 루프 방지 (최대 반복 횟수 설정)

3. **Multi-turn 대화 지원**
   - `input()`을 사용한 대화형 인터페이스
   - 이전 대화를 기억하는 히스토리 관리
   - 종료 명령어 (`quit`, `exit`) 지원

### 보너스 (선택)

4. **스트리밍 지원**
   - `stream=True`로 요청
   - SSE(Server-Sent Events) 파싱
   - 토큰 도착 시 즉시 출력
   - 스트리밍에서 `tool_calls` delta 누적

5. **추가 기능**
   - 토큰 수 추정 및 컨텍스트 관리
   - 대화 히스토리 표시 명령어
   - 시스템 프롬프트 커스터마이징

---

## 구현 가이드

### Step 1: 도구 정의
```python
# 도구 함수 구현
def my_tool(param: str) -> str:
    """도구의 기능을 구현합니다."""
    return "결과"

# OpenAI Tool Schema
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "my_tool",
            "description": "도구 설명",
            "parameters": {
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "파라미터 설명"}
                },
                "required": ["param"]
            }
        }
    }
]

# 디스패치 테이블
TOOL_FUNCTIONS = {"my_tool": my_tool}
```

### Step 2: LLM 호출 함수
```python
def call_llm(messages, tools=None):
    payload = {"model": DEFAULT_MODEL, "messages": messages}
    if tools:
        payload["tools"] = tools
    response = requests.post(url, headers=headers, json=payload, proxies=PROXIES)
    return response.json()
```

### Step 3: Agent Loop
```python
while iteration < max_iterations:
    response = call_llm(messages, tools=TOOLS)
    assistant_msg = response["choices"][0]["message"]

    if not assistant_msg.get("tool_calls"):
        return assistant_msg["content"]  # 최종 응답

    messages.append(assistant_msg)
    for tc in assistant_msg["tool_calls"]:
        result = execute_tool(tc["function"]["name"], ...)
        messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
```

---

## 테스트 시나리오

다음 질문들로 Agent가 올바르게 동작하는지 확인하세요:

1. **단일 도구 호출**: "123과 456을 더하면?"
2. **복합 도구 호출**: "지금 시간 알려주고, 현재 디렉토리 파일 목록도 보여줘"
3. **도구 불필요**: "파이썬이란 무엇인가요?"
4. **Multi-turn 맥락 유지**: 이전 대화 결과를 참조하는 후속 질문
5. **연쇄 도구 호출**: 한 도구의 결과를 다른 도구의 입력으로 사용하는 경우

---

## 평가 기준

| 항목 | 배점 |
|------|------|
| 도구 2개 이상 구현 및 Schema 정의 | 25% |
| Agent Loop 정상 동작 (도구 호출 → 실행 → 결과 반환) | 30% |
| Multi-turn 대화 지원 | 20% |
| 에러 처리 및 안전장치 | 15% |
| 코드 품질 및 주석 | 10% |
| (보너스) 스트리밍 지원 | +10% |

---

## 참고 자료

- `basic_agent.py`: 기본 Agent Loop 구현 예시
- `multi_turn_agent.py`: Multi-turn 대화 예시
- `streaming_agent.py`: 스트리밍 구현 예시
- OpenAI API 문서: https://platform.openai.com/docs/api-reference/chat/create

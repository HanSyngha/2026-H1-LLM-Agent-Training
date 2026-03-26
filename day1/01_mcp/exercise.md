# 실습: 나만의 MCP 서버 만들기

## 목표

FastMCP를 사용하여 나만의 MCP 서버를 만들고, LLM과 연동하여 자연어로 도구를 호출해봅니다.

---

## 요구사항

### 1. MCP 서버 구현 (`my_mcp_server.py`)

- **도구 (Tool) 3개 이상** 구현
  - 예시 아이디어:
    - `translate(text, target_lang)`: 텍스트 번역 (더미 구현 가능)
    - `get_stock_price(ticker)`: 주식 가격 조회
    - `send_notification(recipient, message)`: 알림 전송
    - `convert_currency(amount, from_currency, to_currency)`: 환율 변환
    - `search_document(query)`: 문서 검색
  - 각 도구에 명확한 docstring 작성 (LLM이 이해할 수 있도록)

- **리소스 (Resource) 1개 이상** 구현
  - 예시:
    - `config://my-app`: 애플리케이션 설정
    - `schema://database`: 데이터베이스 스키마 정보
    - `docs://api`: API 문서

- **프롬프트 (Prompt) 1개 이상** 구현
  - 예시:
    - `summarize_prompt(text)`: 요약 프롬프트
    - `email_draft_prompt(recipient, subject, key_points)`: 이메일 작성 프롬프트

### 2. MCP 클라이언트 (`my_mcp_client.py`)

- 위에서 만든 서버에 연결
- 모든 도구, 리소스, 프롬프트를 호출하여 테스트

### 3. LLM 연동 (`my_mcp_llm.py`)

- MCP 도구를 OpenAI function calling 형식으로 변환
- 자연어 질문으로 도구 호출이 이루어지는 것을 확인

---

## 체크리스트

- [ ] FastMCP 서버가 정상적으로 실행됨
- [ ] 3개 이상의 도구가 등록되어 있음
- [ ] 각 도구의 docstring이 명확하게 작성됨
- [ ] 1개 이상의 리소스가 등록되어 있음
- [ ] 1개 이상의 프롬프트가 등록되어 있음
- [ ] 클라이언트에서 모든 도구/리소스/프롬프트를 호출할 수 있음
- [ ] LLM이 자연어 질문을 이해하고 적절한 도구를 호출함
- [ ] 도구 실행 결과가 LLM의 최종 답변에 반영됨

---

## 힌트

### 도구 정의 시 주의할 점
```python
@mcp.tool()
def my_tool(param1: str, param2: int) -> dict:
    """도구 설명을 명확하게 작성하세요.

    LLM은 이 docstring을 읽고 언제 이 도구를 사용할지 결정합니다.
    파라미터 설명도 꼼꼼히 작성하면 LLM의 도구 선택 정확도가 높아집니다.

    Args:
        param1: 파라미터1에 대한 설명
        param2: 파라미터2에 대한 설명
    """
    # 구현
    pass
```

### OpenAI function calling 변환 핵심
```python
# MCP 도구 -> OpenAI 형식 변환의 핵심은 inputSchema 매핑입니다
openai_tool = {
    "type": "function",
    "function": {
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.inputSchema,  # JSON Schema 호환
    }
}
```

### 여러 도구를 한번에 호출하려면
- LLM에게 시스템 프롬프트로 "여러 작업이 요청되면 가능한 모든 도구를 호출하세요"라고 지시
- `tool_choice="auto"`로 설정하여 LLM이 판단하도록 함

---

## 보너스 도전

- 도구 간 의존성이 있는 시나리오 구현 (예: 검색 결과를 번역)
- 에러 처리 추가 (잘못된 파라미터, 서버 오류 등)
- 도구 실행 로깅 추가

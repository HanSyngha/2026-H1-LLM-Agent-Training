# Structured Output과 Tool Calling 실습

## 학습 목표

- JSON 모드와 Structured Output(JSON Schema)의 차이를 이해하고 적절히 사용할 수 있다
- Tool Calling의 전체 흐름을 구현할 수 있다
- tool_choice 옵션에 따른 동작 차이를 설명할 수 있다

---

## Part 1: 뉴스 기사 Structured Output 분석

### 과제

아래 뉴스 기사 텍스트를 Structured Output(json_schema)으로 분석하는 코드를 작성하세요.

```
[샘플 뉴스 기사]

삼성전자가 차세대 AI 반도체 'Exynos 2500'을 공개했다.
이번 칩은 4나노 공정으로 제작되며, 온디바이스 AI 성능이
전작 대비 40% 향상됐다. 업계에서는 이 제품이 글로벌
스마트폰 시장에서 퀄컴 스냅드래곤과의 경쟁에서 우위를
점할 수 있을지 주목하고 있다. 삼성전자 반도체 부문
사장은 "AI 시대에 맞는 혁신적인 칩을 선보이게 되어
기쁘다"고 밝혔다.
```

### 요구사항

1. **Pydantic 모델 정의**: 다음 필드를 포함하는 `NewsAnalysis` 모델을 만드세요
   - `title` (str): 기사 제목 (LLM이 생성)
   - `category` (str, enum): 카테고리 — "정치", "경제", "사회", "기술", "문화", "스포츠" 중 택일
   - `summary` (str): 3문장 이내 요약
   - `keywords` (list[str]): 핵심 키워드 5개
   - `sentiment` (str, enum): 감정 — "긍정", "부정", "중립" 중 택일
   - `confidence` (float): 분석 신뢰도 (0.0 ~ 1.0)

2. **response_format에 json_schema 사용**: `structured_output.py`의 `pydantic_to_json_schema()` 함수를 참고하세요

3. **Pydantic으로 응답 검증**: `model_validate_json()`을 사용하여 타입 안전하게 파싱하세요

### 힌트

```python
from pydantic import BaseModel, Field
from enum import Enum

class Category(str, Enum):
    # 여기에 카테고리 정의
    ...

class NewsAnalysis(BaseModel):
    title: str = Field(description="...")
    # 나머지 필드 정의
    ...
```

### 체크리스트

- [ ] Pydantic 모델이 모든 필수 필드를 포함하는가?
- [ ] enum 타입으로 카테고리와 감정을 제한했는가?
- [ ] response_format에 json_schema를 사용했는가?
- [ ] `model_validate_json()`으로 응답을 파싱했는가?
- [ ] 결과를 읽기 좋게 출력했는가?

---

## Part 2: 복수 Tool 정의 및 자동 호출

### 과제

2개 이상의 도구를 정의하고, LLM이 사용자 질문에 따라 적절한 도구를 자동으로 선택하여 호출하도록 구현하세요.

### 요구사항

1. **최소 2개의 도구 정의**: 아래에서 선택하거나 직접 만드세요
   - `search_news(query: str, date_range: str)` — 뉴스 검색
   - `get_stock_price(symbol: str)` — 주가 조회
   - `translate_text(text: str, target_lang: str)` — 번역
   - `summarize_document(document: str, max_length: int)` — 문서 요약

2. **도구 스키마를 JSON Schema로 정의**: `tool_calling.py`의 TOOLS 형식을 참고하세요

3. **전체 흐름 구현**:
   - 도구 정의 → LLM에 전송 → tool_calls 파싱 → 도구 실행 → 결과 반환 → 최종 답변

4. **다양한 질문 테스트**: 각 도구가 호출되는 질문을 각각 만들어 테스트하세요

### 힌트

```python
# 도구 스키마 정의 예시
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_news",
            "description": "키워드로 뉴스를 검색합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "검색 키워드"},
                    # ...
                },
                "required": ["query"],
            },
        },
    },
    # 두 번째 도구 정의...
]
```

### 체크리스트

- [ ] 2개 이상의 도구를 JSON Schema로 정확히 정의했는가?
- [ ] 각 도구의 실제 실행 함수(시뮬레이션 포함)를 구현했는가?
- [ ] tool_calls 응답을 올바르게 파싱하여 실행하는가?
- [ ] tool 역할 메시지로 결과를 LLM에 다시 전달하는가?
- [ ] tool_call_id를 올바르게 매칭하고 있는가?
- [ ] 각 도구가 올바른 질문에서 호출되는지 테스트했는가?

---

## Part 3: tool_choice 옵션 비교 실험

### 과제

Part 2에서 만든 도구를 사용하여 `tool_choice` 옵션을 바꿔가며 동작 차이를 관찰하세요.

### 요구사항

1. **동일한 질문**으로 아래 4가지 tool_choice를 테스트하세요:
   - `tool_choice="auto"` — LLM이 자동 판단
   - `tool_choice="required"` — 도구 호출 강제
   - `tool_choice="none"` — 도구 호출 금지
   - `tool_choice={"type": "function", "function": {"name": "특정_함수명"}}` — 특정 함수 강제

2. **2가지 유형의 질문**으로 테스트하세요:
   - 도구가 필요한 질문 (예: "삼성전자 최근 뉴스 찾아줘")
   - 도구가 필요 없는 질문 (예: "안녕하세요, 반갑습니다")

3. **결과를 표로 정리**: 각 조합에서의 동작을 기록하세요

### 예상 결과 표

| 질문 유형 | auto | required | none | 특정 함수 |
|----------|------|----------|------|----------|
| 도구 필요 | 도구 호출 | 도구 호출 | 텍스트 응답 | 해당 함수 호출 |
| 도구 불필요 | 텍스트 응답 | ??? | 텍스트 응답 | ??? |

### 관찰 포인트

- `required`일 때 도구가 필요 없는 질문에서 LLM이 어떤 도구를 선택하는가?
- `none`일 때 도구가 필요한 질문에서 LLM이 어떻게 답변하는가?
- 특정 함수를 강제했을 때 관련 없는 질문에서 어떤 인자를 생성하는가?

### 체크리스트

- [ ] 4가지 tool_choice 옵션을 모두 테스트했는가?
- [ ] 2가지 유형의 질문을 각각 테스트했는가?
- [ ] 각 조합의 결과(도구 호출 여부, 호출된 함수명, 응답 내용)를 기록했는가?
- [ ] 예상과 다른 동작이 있었다면 그 이유를 분석했는가?

---

## 보너스 과제

### 도전 1: 체인 호출 구현

하나의 질문에 대해 LLM이 여러 도구를 순차적으로 호출하는 시나리오를 구현하세요.

예시: "삼성전자 뉴스를 검색하고, 검색 결과를 영어로 번역해줘"
→ `search_news` → `translate_text` (체인 호출)

### 도전 2: 에러 핸들링

도구 실행 중 에러가 발생하는 시나리오를 만들고, LLM이 에러를 인지하고 사용자에게 적절히 안내하도록 구현하세요.

- 도구 함수에서 의도적으로 예외를 발생시키기
- 에러 정보를 JSON 형태로 LLM에 전달하기
- LLM이 에러를 이해하고 대안을 제시하는지 확인하기

---

## 참고 파일

| 파일 | 내용 |
|-----|------|
| `json_formatting.py` | JSON 모드 기초 (response_format 사용법) |
| `structured_output.py` | JSON Schema + Pydantic (Structured Output) |
| `tool_calling.py` | Tool Calling 기초 (전체 흐름, 병렬 호출, tool_choice) |
| `tool_calling_advanced.py` | 고급 패턴 (체인 호출, 에러 처리, 스트리밍) |

# 실습: 프로덕션 수준 Agent 아키텍처 구현하기

## 목표

`tool_registry.py`의 ToolRegistry와 `safe_agent.py`의 안전장치 패턴을 활용하여,
프로덕션 환경에서 운영 가능한 수준의 Agent를 구성합니다.

---

## 요구사항

### 1. ToolRegistry를 활용한 도구 등록

`tool_registry.py`의 `ToolRegistry` 클래스를 사용하여 도구를 등록하세요.

**필수 사항:**
- 데코레이터(`@registry.tool()`)로 최소 3개 도구 등록
- 각 도구에 타입 힌트와 docstring 작성
- 자동 생성된 OpenAI Tool Schema 확인

```python
from tool_registry import ToolRegistry

registry = ToolRegistry()

@registry.tool(description="두 수를 더합니다")
def add(a: float, b: float) -> float:
    """두 수를 더합니다.

    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자
    """
    return a + b

# 자동 생성된 스키마 확인
print(registry.get_tool_schemas())
```

### 2. SafeAgent의 안전장치 패턴 적용

`safe_agent.py`의 `SafeAgent` 클래스를 참고하여 안전장치를 적용하세요.

**필수 사항:**
- `SafetyPolicy` 설정: 허용 경로, 차단 명령어, 위험 도구 목록
- `SafetyChecker`로 도구 실행 전 검사
- `RateLimiter`로 속도 제한
- 도구 실행 로그 기록

### 3. Agent Loop 통합

ToolRegistry + SafeAgent를 결합하여 완전한 Agent를 구성하세요.

```python
# 도구를 ToolRegistry에 등록
registry = ToolRegistry()

@registry.tool()
def my_tool(...):
    ...

# SafeAgent에 연결
agent = SafeAgent(
    tool_schemas=registry.get_tool_schemas(),
    tool_functions=registry.get_tool_functions(),
    policy=SafetyPolicy(allowed_paths=[...]),
    system_prompt="...",
)

# 대화형 실행
result = agent.run("질문")
```

---

## 체크리스트

- [ ] ToolRegistry에 3개 이상의 도구가 등록됨
- [ ] 각 도구에 타입 힌트와 docstring이 작성됨
- [ ] OpenAI Tool Schema가 자동 생성됨
- [ ] SafetyPolicy가 적절히 설정됨
- [ ] 경로 제한이 동작함 (허용 경로 밖 접근 시 거부)
- [ ] 차단 명령어가 동작함 (위험 명령어 차단)
- [ ] 위험 도구 실행 시 사용자 확인이 동작함
- [ ] 속도 제한이 적용됨
- [ ] 도구 실행 로그가 기록됨
- [ ] 대화형 인터페이스가 동작함

---

## 힌트

### ToolRegistry 핵심 메서드

```python
registry = ToolRegistry()

# 도구 등록 (데코레이터)
@registry.tool(description="설명")
def my_func(param: str) -> str:
    ...

# 스키마 조회
schemas = registry.get_tool_schemas()     # OpenAI Tool Schema 리스트
functions = registry.get_tool_functions() # {이름: 함수} 딕셔너리
registry.describe()                        # 등록된 도구 요약

# 도구 실행 (입력 검증 + 에러 래핑)
result = registry.execute("my_func", {"param": "value"})
```

### SafeAgent 핵심 구성요소

```python
# 안전 정책
policy = SafetyPolicy(
    allowed_paths=["~/projects"],           # 경로 제한
    blocked_commands=["rm -rf", "format"],  # 차단 명령어
    dangerous_tools=["run_command"],         # 위험 도구
    max_iterations=20,                       # 최대 반복
    rate_limit_per_second=2.0,              # 속도 제한
)

# 안전 Agent
agent = SafeAgent(
    tool_schemas=schemas,
    tool_functions=functions,
    policy=policy,
    system_prompt="...",
    log_file="agent.log",
)
```

---

## 보너스 과제

### 도전 1: 커스텀 안전 규칙 추가
- 특정 도구의 특정 인자에 대한 검증 규칙 추가
- 예: 파일 크기 제한, 특정 확장자만 허용

### 도전 2: 사용 통계 대시보드
- 도구별 호출 횟수, 평균 실행 시간 등을 집계
- 통계를 표로 출력

### 도전 3: 권한 기반 도구 제어
- 사용자 역할(admin, user, viewer)에 따라 사용 가능한 도구를 제한
- admin: 모든 도구 사용 가능
- user: 읽기 도구만 사용 가능
- viewer: 조회 도구만 사용 가능

---

## 참고 파일

| 파일 | 내용 |
|-----|------|
| `tool_registry.py` | ToolRegistry 클래스 (도구 등록, Schema 자동 생성) |
| `safe_agent.py` | SafeAgent 클래스 (안전장치 포함 Agent) |
| `system_prompts.py` | 시스템 프롬프트 관리 패턴 |
| `harness_engineering.py` | Agent 하네스 엔지니어링 패턴 |

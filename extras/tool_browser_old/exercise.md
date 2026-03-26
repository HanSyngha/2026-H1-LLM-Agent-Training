# 실습: 브라우저 자동화 Agent

## 목표
Playwright를 활용하여 웹사이트를 탐색하고 정보를 수집하는 Agent를 구현합니다.

---

## 사전 준비

```bash
# Playwright 설치
pip install playwright

# 브라우저 바이너리 설치 (Chromium)
playwright install chromium
```

---

## 요구사항

### 필수

1. **최소 3개 브라우저 도구 사용**
   - `navigate`: 페이지 이동
   - `get_page_content`: 페이지 내용 추출
   - 추가 1개 이상: `click_element`, `fill_input`, `get_links`, `screenshot` 등

2. **정보 수집 플로우 구현**
   - 검색 엔진(구글/네이버)에서 키워드 검색
   - 검색 결과 페이지 파싱
   - 상위 결과에서 정보 추출
   - 결과를 정리하여 사용자에게 전달

3. **Agent Loop 통합**
   - 브라우저 도구를 Agent Loop에 등록
   - LLM이 자율적으로 브라우저 도구를 선택하여 실행
   - 여러 단계의 브라우저 조작을 자동으로 수행

### 보너스

4. **에러 복구**
   - 페이지 로딩 실패 시 재시도
   - 셀렉터를 찾을 수 없을 때 대체 방법 시도
   - 타임아웃 처리

5. **스크린샷 기반 판단**
   - 각 단계에서 스크린샷 저장
   - 시각적 확인을 위한 로깅

---

## 구현 예시: 뉴스 헤드라인 수집기

### 동작 시나리오
```
사용자: "오늘 주요 뉴스 3개 알려줘"

Agent 내부 동작:
1. search_google("오늘 주요 뉴스") 호출
2. 검색 결과에서 뉴스 사이트 URL 확인
3. navigate(뉴스_사이트_URL) 호출
4. get_page_content() 호출
5. 내용 분석 후 헤드라인 3개 추출
6. 정리된 결과를 사용자에게 전달
```

### 코드 구조
```python
# 브라우저 도구 import
from browser_tools import BROWSER_TOOL_SCHEMAS, BROWSER_TOOL_FUNCTIONS

# Agent Loop에서 사용
def run_browser_agent(user_message, messages):
    messages.append({"role": "user", "content": user_message})

    while iteration < max_iterations:
        response = call_llm(messages, tools=BROWSER_TOOL_SCHEMAS)
        # ... tool_calls 처리 ...

    return final_response
```

---

## 테스트 시나리오

1. **기본 탐색**
   ```
   사용자: example.com 페이지 내용을 보여줘
   ```

2. **검색 + 정보 추출**
   ```
   사용자: 구글에서 "Python 3.12 new features"를 검색해줘
   ```

3. **다단계 탐색**
   ```
   사용자: 네이버에서 오늘 뉴스 헤드라인 3개를 가져와줘
   ```

4. **폼 입력**
   ```
   사용자: 위키피디아에서 "인공지능"을 검색해줘
   ```

---

## 주의사항

- 웹사이트의 구조는 자주 변경되므로, 하드코딩된 셀렉터에 의존하지 마세요.
- 로봇 차단(CAPTCHA, 접근 제한)이 발생할 수 있습니다.
- 브라우저 리소스 사용을 최소화하세요 (headless 모드 사용).
- 테스트 시에는 `headless=False`로 설정하면 브라우저 화면을 볼 수 있어 디버깅에 유리합니다.
- 반드시 작업 완료 후 브라우저를 종료하세요 (메모리 누수 방지).

---

## 참고 파일

- `browser_tools.py`: 브라우저 도구 구현 (BrowserManager, 각종 도구 함수)
- `browser_agent.py`: Agent 통합 예시
- Playwright 공식 문서: https://playwright.dev/python/

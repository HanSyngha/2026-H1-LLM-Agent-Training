"""
브라우저 Agent - 웹 탐색 및 정보 수집 Agent

browser_tools.py의 도구들을 Agent Loop에 통합하여,
자연어로 웹사이트를 탐색하고 정보를 수집하는 Agent입니다.

사용 예시:
- "네이버에서 오늘 뉴스 헤드라인 3개 가져와줘"
- "구글에서 Python 3.12 새 기능을 검색해줘"
- "https://example.com 페이지의 내용을 요약해줘"
- "위키피디아에서 인공지능 항목을 찾아줘"

=== 브라우저 Agent의 동작 흐름 ===
1. 사용자: "네이버에서 오늘 뉴스를 알려줘"
2. LLM → tool_call: navigate("https://www.naver.com")
3. 도구 실행: 네이버 페이지 이동 완료
4. LLM → tool_call: get_page_content()
5. 도구 실행: 페이지 텍스트 추출
6. LLM → 최종 응답: "네이버 메인 뉴스 헤드라인은 다음과 같습니다: ..."

Agent가 여러 단계의 브라우저 조작을 자율적으로 수행합니다.
"""

import sys
import os
import json
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

# 브라우저 도구 import
from browser_tools import (
    BROWSER_TOOL_SCHEMAS,
    BROWSER_TOOL_FUNCTIONS,
    BrowserManager,
)


# ============================================================
# LLM 호출
# ============================================================

def call_llm(messages: list[dict], tools: list[dict] | None = None) -> dict:
    """OpenAI 호환 API 호출"""
    url = f"{GATEWAY_BASE_URL}/chat/completions"
    headers = get_headers()

    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
    }
    if tools:
        payload["tools"] = tools

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        proxies=PROXIES,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


# ============================================================
# 도구 실행기
# ============================================================

def execute_tool(tool_name: str, arguments: dict) -> str:
    """도구를 실행하고 결과를 반환합니다."""
    if tool_name not in BROWSER_TOOL_FUNCTIONS:
        return f"오류: 알 수 없는 도구 '{tool_name}'"

    func = BROWSER_TOOL_FUNCTIONS[tool_name]
    try:
        result = func(**arguments)
        return str(result)
    except TypeError as e:
        return f"도구 파라미터 오류: {e}"
    except Exception as e:
        return f"도구 실행 오류: {e}"


# ============================================================
# 시스템 프롬프트
# ============================================================

SYSTEM_PROMPT = """당신은 웹 브라우저를 제어하는 AI 어시스턴트입니다.
사용자의 요청에 따라 웹사이트를 탐색하고 정보를 수집합니다.

## 사용 가능한 도구

1. **navigate(url)**: 웹 페이지로 이동
2. **get_page_content()**: 현재 페이지 텍스트 추출
3. **click_element(selector)**: CSS 셀렉터로 요소 클릭
4. **fill_input(selector, value)**: 입력 필드에 텍스트 입력
5. **screenshot(path)**: 스크린샷 저장
6. **get_links()**: 페이지의 모든 링크 추출
7. **search_google(query)**: 구글 검색
8. **close_browser()**: 브라우저 종료

## 행동 전략

### 웹 페이지 탐색 시:
1. navigate()로 페이지 이동
2. get_page_content()로 내용 파악
3. 필요하면 get_links()로 링크 확인 후 추가 탐색

### 정보 검색 시:
1. search_google()로 검색
2. 유용한 결과 URL로 navigate()
3. get_page_content()로 상세 내용 확인

### 폼 입력 시:
1. navigate()로 페이지 이동
2. fill_input()으로 필드 입력
3. click_element()으로 제출 버튼 클릭

## 주의사항
- 한 번에 하나의 도구를 호출하세요 (순차적 작업).
- 페이지 내용이 길면 핵심만 요약하여 전달하세요.
- 오류 발생 시 다른 접근 방법을 시도하세요.
- 항상 한국어로 응답하세요.
"""


# ============================================================
# 브라우저 Agent Loop
# ============================================================

def run_browser_agent(user_message: str, messages: list[dict]) -> str:
    """
    브라우저 Agent의 한 턴을 실행합니다.

    브라우저 작업은 여러 단계가 필요하므로 (이동 → 내용 추출 → 분석),
    최대 반복 횟수를 넉넉하게 설정합니다.
    """
    messages.append({"role": "user", "content": user_message})

    max_iterations = 20  # 브라우저 작업은 단계가 많을 수 있음
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response_data = call_llm(messages, tools=BROWSER_TOOL_SCHEMAS)
        assistant_message = response_data["choices"][0]["message"]
        tool_calls = assistant_message.get("tool_calls")

        if not tool_calls:
            content = assistant_message.get("content", "")
            messages.append({"role": "assistant", "content": content})
            return content

        messages.append(assistant_message)

        for tc in tool_calls:
            tool_name = tc["function"]["name"]
            arguments = json.loads(tc["function"]["arguments"])
            tool_call_id = tc["id"]

            args_str = json.dumps(arguments, ensure_ascii=False)
            print(f"  [브라우저] {tool_name}({args_str[:150]})")

            result = execute_tool(tool_name, arguments)

            # 결과 미리보기 (너무 길면 축약)
            preview = result[:300].replace("\n", " ")
            if len(result) > 300:
                preview += "..."
            print(f"  [결과] {preview}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result,
            })

    return "오류: 최대 브라우저 작업 횟수를 초과했습니다."


# ============================================================
# 대화형 인터페이스
# ============================================================

def main():
    print("=" * 60)
    print("브라우저 Agent - 웹 탐색 & 정보 수집")
    print("=" * 60)
    print()
    print("사용 예시:")
    print("  - '네이버에서 오늘 뉴스 헤드라인 3개 가져와줘'")
    print("  - '구글에서 Python 3.12 새 기능을 검색해줘'")
    print("  - 'https://example.com 페이지 내용을 요약해줘'")
    print()
    print("종료: 'quit' 또는 'exit'")
    print("=" * 60)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    try:
        while True:
            try:
                user_input = input("\n사용자: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n종료합니다.")
                break

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "종료"):
                print("종료합니다.")
                break

            # Agent 실행
            print("\nAgent:")
            response = run_browser_agent(user_input, messages)
            print(f"\n{response}")

    finally:
        # 종료 시 브라우저 정리
        print("\n브라우저를 종료합니다...")
        BrowserManager.get_instance().close()


if __name__ == "__main__":
    main()

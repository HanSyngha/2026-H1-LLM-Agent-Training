"""
Office Agent - Excel + 앱 제어 Agent

office_tools.py와 app_control_tools.py의 도구를 결합하여,
데이터를 Excel로 정리하거나 Windows 앱을 제어하는 Agent입니다.

사용 예시:
- "매출 데이터를 Excel로 정리해줘"
- "이 Excel 파일에 차트를 추가해줘"
- "실행 중인 앱 목록을 알려줘"
- "VS Code 창을 활성화해줘"
"""

import sys
import os
import json
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

# Office 도구 import
from office_tools import OFFICE_TOOL_SCHEMAS, OFFICE_TOOL_FUNCTIONS
from app_control_tools import APP_CONTROL_TOOL_SCHEMAS, APP_CONTROL_TOOL_FUNCTIONS


# ============================================================
# 모든 도구 통합
# ============================================================

# 두 도구 세트의 스키마를 합침
ALL_TOOL_SCHEMAS = OFFICE_TOOL_SCHEMAS + APP_CONTROL_TOOL_SCHEMAS

# 두 도구 세트의 함수 매핑을 합침
ALL_TOOL_FUNCTIONS = {**OFFICE_TOOL_FUNCTIONS, **APP_CONTROL_TOOL_FUNCTIONS}


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
    if tool_name not in ALL_TOOL_FUNCTIONS:
        return f"오류: 알 수 없는 도구 '{tool_name}'"

    func = ALL_TOOL_FUNCTIONS[tool_name]
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

SYSTEM_PROMPT = """당신은 Office 자동화와 Windows 앱 제어 전문 AI 어시스턴트입니다.
사용자의 요청에 따라 데이터를 Excel로 정리하거나, Windows 앱을 제어합니다.

## Excel 도구
1. **create_excel(path, data)**: Excel 파일 생성 (데이터는 JSON 형식)
2. **read_excel(path)**: Excel 파일 읽기
3. **update_excel_cell(path, sheet, cell, value)**: 특정 셀 수정
4. **create_excel_chart(path, data_range, chart_type)**: 차트 추가

## Windows 앱 제어 도구
5. **get_running_apps()**: 실행 중인 앱 목록
6. **focus_window(title)**: 창 활성화
7. **type_text(text)**: 텍스트 입력
8. **click_at(x, y)**: 마우스 클릭
9. **connect_to_electron_app(port)**: Electron 앱 CDP 연결

## 행동 규칙

### Excel 작업 시:
- 데이터를 받으면 적절한 JSON 형식으로 변환하여 create_excel 호출
- 기존 파일 수정 시 read_excel로 먼저 확인 후 update_excel_cell 사용
- 차트 추가 시 데이터 범위를 정확하게 지정

### 앱 제어 시:
- 먼저 get_running_apps()로 대상 앱 확인
- focus_window()로 대상 창 활성화 후 type_text() 또는 click_at() 사용

### 데이터 처리:
- 사용자가 자연어로 데이터를 설명하면, JSON 형식으로 구조화
- 가능하면 헤더를 포함하여 의미 있는 표 형태로 구성

항상 한국어로 응답하세요.
"""


# ============================================================
# Office Agent Loop
# ============================================================

def run_office_agent(user_message: str, messages: list[dict]) -> str:
    """Office Agent의 한 턴을 실행합니다."""
    messages.append({"role": "user", "content": user_message})

    max_iterations = 15
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response_data = call_llm(messages, tools=ALL_TOOL_SCHEMAS)
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

            # 실행 정보 출력
            args_preview = json.dumps(arguments, ensure_ascii=False)
            if len(args_preview) > 150:
                args_preview = args_preview[:150] + "..."
            print(f"  [도구] {tool_name}({args_preview})")

            # 도구 실행
            result = execute_tool(tool_name, arguments)

            # 결과 미리보기
            preview = result[:300].replace("\n", " ")
            if len(result) > 300:
                preview += "..."
            print(f"  [결과] {preview}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result,
            })

    return "오류: 최대 도구 실행 횟수를 초과했습니다."


# ============================================================
# 대화형 인터페이스
# ============================================================

def main():
    print("=" * 60)
    print("Office Agent - Excel 자동화 & 앱 제어")
    print("=" * 60)
    print()
    print("사용 예시:")
    print("  - '다음 데이터를 Excel로 만들어줘: 1월 매출 1000, 2월 매출 1200'")
    print("  - 'output.xlsx 파일 내용을 읽어줘'")
    print("  - 'output.xlsx에 막대 차트를 추가해줘'")
    print("  - '실행 중인 앱 목록을 보여줘'")
    print()
    print("종료: 'quit' 또는 'exit'")
    print("=" * 60)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

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
        response = run_office_agent(user_input, messages)
        print(f"\n{response}")


if __name__ == "__main__":
    main()

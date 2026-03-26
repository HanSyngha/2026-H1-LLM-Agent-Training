"""
CLI Agent - 파일 시스템과 명령어를 다루는 Agent

cli_tools.py의 도구들을 Agent Loop에 통합하여,
자연어로 파일 시스템을 탐색하고 명령어를 실행하는 Agent입니다.

사용 예시:
- "현재 디렉토리의 Python 파일 목록을 보여줘"
- "이 프로젝트의 구조를 파악해줘"
- "README.md 파일 내용을 읽어줘"
- "test.txt 파일을 만들어줘"
"""

import sys
import os
import json
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

# CLI 도구 import
from cli_tools import CLI_TOOL_SCHEMAS, CLI_TOOL_FUNCTIONS


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
    """
    도구를 실행하고 결과를 반환합니다.

    Tool Registry 패턴:
    - 도구 이름으로 함수를 찾아 실행
    - 알 수 없는 도구는 에러 반환
    - 모든 예외를 catch하여 안전하게 처리
    """
    if tool_name not in CLI_TOOL_FUNCTIONS:
        return f"오류: 알 수 없는 도구 '{tool_name}'"

    func = CLI_TOOL_FUNCTIONS[tool_name]
    try:
        result = func(**arguments)
        return str(result)
    except TypeError as e:
        return f"도구 파라미터 오류: {e}"
    except Exception as e:
        return f"도구 실행 오류: {e}"


# ============================================================
# CLI Agent Loop
# ============================================================

# 시스템 프롬프트: Agent의 역할, 도구 사용법, 안전 규칙을 정의
SYSTEM_PROMPT = """당신은 파일 시스템과 CLI 명령어를 다루는 전문 어시스턴트입니다.

## 사용 가능한 도구

1. **run_command**: 시스템 명령어 실행 (ls, cat, grep, find 등)
2. **run_powershell**: PowerShell 스크립트 실행 (Windows 관리 작업)
3. **list_directory**: 디렉토리 파일/폴더 목록 조회
4. **read_file**: 파일 내용 읽기
5. **write_file**: 파일 생성/수정
6. **search_files**: 파일 검색 (glob 패턴)

## 행동 규칙

- 사용자의 요청에 맞는 도구를 선택하여 실행하세요.
- 파일을 삭제하거나 시스템에 큰 변경을 가하는 작업은 먼저 확인하세요.
- 여러 단계가 필요한 작업은 순서대로 도구를 호출하세요.
- 도구 실행 결과를 사용자에게 읽기 쉽게 정리하여 전달하세요.
- 항상 한국어로 응답하세요.

## 현재 환경
- 운영체제: WSL2 (Windows Subsystem for Linux)
- 작업 디렉토리: 사용자 홈 디렉토리
"""


def run_cli_agent(user_message: str, messages: list[dict]) -> str:
    """
    CLI Agent의 한 턴을 실행합니다.

    Args:
        user_message: 사용자 입력
        messages: 대화 히스토리 (in-place 수정됨)

    Returns:
        Agent의 최종 응답
    """
    messages.append({"role": "user", "content": user_message})

    max_iterations = 15  # CLI 작업은 여러 단계가 필요할 수 있음
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response_data = call_llm(messages, tools=CLI_TOOL_SCHEMAS)
        assistant_message = response_data["choices"][0]["message"]
        tool_calls = assistant_message.get("tool_calls")

        if not tool_calls:
            # 최종 응답
            content = assistant_message.get("content", "")
            messages.append({"role": "assistant", "content": content})
            return content

        # 도구 호출 처리
        messages.append(assistant_message)

        for tc in tool_calls:
            tool_name = tc["function"]["name"]
            arguments = json.loads(tc["function"]["arguments"])
            tool_call_id = tc["id"]

            # 실행 정보 출력
            args_preview = json.dumps(arguments, ensure_ascii=False)
            if len(args_preview) > 100:
                args_preview = args_preview[:100] + "..."
            print(f"  [도구] {tool_name}({args_preview})")

            # 도구 실행
            result = execute_tool(tool_name, arguments)

            # 결과 미리보기 출력
            result_preview = result[:200].replace("\n", " ")
            if len(result) > 200:
                result_preview += "..."
            print(f"  [결과] {result_preview}")

            # 결과를 메시지에 추가
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
    print("CLI Agent - 파일 시스템 & 명령어 실행 Agent")
    print("=" * 60)
    print()
    print("사용 예시:")
    print("  - '현재 디렉토리의 Python 파일 목록을 보여줘'")
    print("  - '이 프로젝트의 구조를 파악해줘'")
    print("  - 'README.md 파일 내용을 읽어줘'")
    print("  - 'hello.py 파일을 만들어줘 (Hello World 출력)'")
    print()
    print("종료: 'quit' 또는 'exit'")
    print("=" * 60)

    # 대화 히스토리 초기화
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
        response = run_cli_agent(user_input, messages)
        print(f"\n{response}")


# ============================================================
# 비대화형 실행 (스크립트에서 사용)
# ============================================================

def run_single_query(query: str) -> str:
    """
    단일 질문에 대해 Agent를 실행합니다.
    스크립트나 다른 프로그램에서 호출할 때 사용합니다.

    사용 예시:
        result = run_single_query("현재 디렉토리의 파일 목록을 알려줘")
        print(result)
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    return run_cli_agent(query, messages)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CLI Agent")
    parser.add_argument(
        "--query", "-q",
        type=str,
        default=None,
        help="단일 질문 실행 (대화형 모드 대신)",
    )
    args = parser.parse_args()

    if args.query:
        # 단일 질문 모드
        result = run_single_query(args.query)
        print(result)
    else:
        # 대화형 모드
        main()

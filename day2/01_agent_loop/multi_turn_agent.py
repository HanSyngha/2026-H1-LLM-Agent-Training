"""
멀티턴 대화형 Agent - requests만 사용

basic_agent.py를 확장하여 다음을 추가합니다:
- 대화 히스토리 관리 (이전 대화를 기억)
- 대화형 input() 루프
- 다양한 도구: 계산기, 날짜/시간, 파일 읽기
- 컨텍스트 크기 관리 힌트

=== 멀티턴의 핵심 ===
대화 히스토리(messages 리스트)를 계속 유지하면서 LLM에 전달하면,
LLM은 이전 대화 맥락을 이해하고 연속적인 대화가 가능합니다.
단, 히스토리가 길어지면 토큰 한도를 초과할 수 있으므로 관리가 필요합니다.
"""

import sys
import os
import json
import math
import requests
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 도구 함수 구현
# ============================================================

def calculator(expression: str) -> str:
    """
    수학 표현식을 계산합니다.
    사칙연산, 거듭제곱, 제곱근 등을 지원합니다.

    보안 주의: eval()은 위험할 수 있으므로,
    허용된 함수/연산자만 사용하도록 제한합니다.
    """
    # 허용된 이름만 사용 가능하도록 제한 (보안)
    allowed_names = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e,
        "log": math.log,
        "log10": math.log10,
    }
    try:
        # __builtins__를 비우고 허용된 이름만 전달
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"계산 결과: {expression} = {result}"
    except Exception as e:
        return f"계산 오류: {e}"


def get_datetime_info(query: str = "now") -> str:
    """
    날짜/시간 관련 정보를 반환합니다.
    query 옵션: "now"(현재시각), "date"(오늘 날짜), "weekday"(요일),
    "timestamp"(Unix 타임스탬프)
    """
    now = datetime.now()

    info = {
        "now": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "weekday": ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][now.weekday()],
        "timestamp": str(int(now.timestamp())),
        "year": str(now.year),
        "month": str(now.month),
        "day": str(now.day),
    }

    if query in info:
        return f"{query}: {info[query]}"

    # 전체 정보 반환
    return json.dumps(info, ensure_ascii=False, indent=2)


def read_file(file_path: str) -> str:
    """
    파일을 읽어 내용을 반환합니다.
    보안을 위해 파일 크기를 제한합니다.
    """
    max_size = 10_000  # 최대 10,000자 (LLM 컨텍스트 보호)

    try:
        # 경로 정규화 (상대경로 -> 절대경로)
        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            return f"오류: 파일을 찾을 수 없습니다 - {abs_path}"

        if not os.path.isfile(abs_path):
            return f"오류: 디렉토리입니다. 파일 경로를 지정하세요 - {abs_path}"

        file_size = os.path.getsize(abs_path)
        if file_size > 100_000:  # 100KB 이상은 거부
            return f"오류: 파일이 너무 큽니다 ({file_size:,} bytes). 100KB 이하만 읽을 수 있습니다."

        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_size)

        if len(content) >= max_size:
            content += f"\n\n... (파일이 {max_size}자에서 잘렸습니다)"

        return f"=== {abs_path} ===\n{content}"

    except PermissionError:
        return f"오류: 파일 읽기 권한이 없습니다 - {file_path}"
    except Exception as e:
        return f"오류: 파일 읽기 실패 - {e}"


def list_files(directory: str = ".") -> str:
    """디렉토리의 파일 목록을 반환합니다."""
    try:
        abs_dir = os.path.abspath(directory)
        if not os.path.isdir(abs_dir):
            return f"오류: 디렉토리가 아닙니다 - {abs_dir}"

        entries = []
        for entry in sorted(os.listdir(abs_dir)):
            full_path = os.path.join(abs_dir, entry)
            if os.path.isdir(full_path):
                entries.append(f"  [DIR]  {entry}/")
            else:
                size = os.path.getsize(full_path)
                entries.append(f"  [FILE] {entry} ({size:,} bytes)")

        header = f"=== {abs_dir} ===\n"
        if not entries:
            return header + "  (비어있는 디렉토리)"
        return header + "\n".join(entries)

    except Exception as e:
        return f"오류: 디렉토리 목록 조회 실패 - {e}"


# ============================================================
# OpenAI Tool Schema 정의
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "수학 표현식을 계산합니다. 사칙연산, 삼각함수, 로그 등을 지원합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "계산할 수학 표현식 (예: '2 + 3 * 4', 'sqrt(144)', 'sin(pi/2)')",
                    },
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime_info",
            "description": "현재 날짜, 시간, 요일 등 시간 관련 정보를 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "조회 유형: 'now'(현재시각), 'date'(날짜), 'weekday'(요일), 'timestamp'(타임스탬프). 기본값: 'now'",
                        "enum": ["now", "date", "weekday", "timestamp"],
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "파일의 내용을 읽어 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "읽을 파일의 경로 (절대경로 또는 상대경로)",
                    },
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "디렉토리의 파일 및 폴더 목록을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "조회할 디렉토리 경로. 기본값: 현재 디렉토리",
                    },
                },
                "required": [],
            },
        },
    },
]

# 도구 이름 -> 함수 매핑
TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_datetime_info": get_datetime_info,
    "read_file": read_file,
    "list_files": list_files,
}


# ============================================================
# LLM 호출
# ============================================================

def call_llm(messages: list[dict], tools: list[dict] | None = None) -> dict:
    """OpenAI 호환 API에 요청을 보내고 응답을 반환합니다."""
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
# 토큰 추정 함수
# ============================================================

def estimate_tokens(messages: list[dict]) -> int:
    """
    메시지 리스트의 대략적인 토큰 수를 추정합니다.

    정확한 토큰 수는 tiktoken 라이브러리를 사용해야 하지만,
    여기서는 간단한 근사치를 사용합니다.
    - 한글: 약 1.5~2 토큰/글자
    - 영문: 약 0.25 토큰/단어 (4글자 ≈ 1토큰)

    간편하게 글자 수 / 2로 근사합니다.
    """
    total_chars = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total_chars += len(content)
        # tool_calls가 있는 경우 JSON 크기도 추정
        if "tool_calls" in msg:
            total_chars += len(json.dumps(msg["tool_calls"], ensure_ascii=False))
    return total_chars // 2  # 매우 대략적인 추정


def trim_messages(messages: list[dict], max_tokens: int = 50000) -> list[dict]:
    """
    메시지가 토큰 한도를 초과하면 오래된 메시지부터 제거합니다.

    === 컨텍스트 관리 전략 ===
    1. system 메시지는 항상 유지 (첫 번째 메시지)
    2. 가장 최근 메시지들을 우선 유지
    3. 오래된 메시지부터 삭제

    더 고급 전략:
    - 요약: 오래된 대화를 LLM으로 요약하여 압축
    - 슬라이딩 윈도우: 최근 N개 턴만 유지
    - 중요도 기반: 도구 결과는 압축, 사용자 메시지는 유지
    """
    estimated = estimate_tokens(messages)
    if estimated <= max_tokens:
        return messages

    print(f"\n⚠️ 컨텍스트 크기 초과 (추정 {estimated:,} 토큰). 오래된 메시지를 제거합니다.")

    # system 메시지 보존
    system_msg = messages[0] if messages[0]["role"] == "system" else None
    other_msgs = messages[1:] if system_msg else messages[:]

    # 뒤에서부터 유지 (최신 메시지 우선)
    trimmed = []
    current_tokens = estimate_tokens([system_msg] if system_msg else [])

    for msg in reversed(other_msgs):
        msg_tokens = estimate_tokens([msg])
        if current_tokens + msg_tokens > max_tokens:
            break
        trimmed.insert(0, msg)
        current_tokens += msg_tokens

    result = ([system_msg] if system_msg else []) + trimmed
    print(f"  {len(messages)} → {len(result)} 메시지로 축소 (추정 {current_tokens:,} 토큰)")
    return result


# ============================================================
# Agent Loop 실행
# ============================================================

def execute_tool(tool_name: str, arguments: dict) -> str:
    """도구를 실행하고 결과를 문자열로 반환합니다."""
    if tool_name not in TOOL_FUNCTIONS:
        return f"오류: 알 수 없는 도구 '{tool_name}'"

    func = TOOL_FUNCTIONS[tool_name]
    try:
        result = func(**arguments)
        return str(result)
    except Exception as e:
        return f"도구 실행 오류: {e}"


def agent_turn(messages: list[dict]) -> str | None:
    """
    Agent Loop 한 사이클을 실행합니다.
    messages는 in-place로 수정됩니다.

    반환값:
    - 최종 응답 문자열: 루프 종료
    - None: 아직 더 실행할 도구가 있음 (외부에서 다시 호출 필요)
    """
    max_tool_rounds = 10
    round_count = 0

    while round_count < max_tool_rounds:
        round_count += 1

        # 컨텍스트 크기 관리
        messages[:] = trim_messages(messages)

        response_data = call_llm(messages, tools=TOOLS)
        assistant_message = response_data["choices"][0]["message"]
        tool_calls = assistant_message.get("tool_calls")

        if not tool_calls:
            # 최종 응답
            return assistant_message.get("content", "")

        # tool_calls 처리
        messages.append(assistant_message)

        for tc in tool_calls:
            tool_name = tc["function"]["name"]
            arguments = json.loads(tc["function"]["arguments"])
            tool_call_id = tc["id"]

            print(f"  🔧 {tool_name}({json.dumps(arguments, ensure_ascii=False)})")
            result = execute_tool(tool_name, arguments)
            print(f"     → {result[:200]}{'...' if len(result) > 200 else ''}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result,
            })

    return "오류: 도구 실행 횟수가 너무 많습니다."


# ============================================================
# 대화형 메인 루프
# ============================================================

def main():
    """
    대화형 Agent를 실행합니다.

    대화 히스토리가 계속 유지되므로, 이전 대화를 참조하는 질문이 가능합니다.
    예:
      사용자: 서울 날씨 알려줘
      Agent: (get_weather 호출) 서울은 맑음, 22도입니다.
      사용자: 그 도시의 현재 시각은?   ← "그 도시"가 서울임을 이해
    """
    print("=" * 60)
    print("멀티턴 대화형 Agent")
    print("사용 가능한 도구: 계산기, 날짜/시간, 파일 읽기, 파일 목록")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("=" * 60)

    # 시스템 프롬프트로 Agent의 성격과 역할을 정의
    system_prompt = (
        "당신은 친절하고 유능한 AI 어시스턴트입니다. "
        "사용자의 질문에 답하기 위해 필요한 도구를 적극적으로 활용하세요.\n\n"
        "사용 가능한 도구:\n"
        "- calculator: 수학 계산 (사칙연산, 삼각함수, 로그 등)\n"
        "- get_datetime_info: 현재 날짜, 시간, 요일 조회\n"
        "- read_file: 파일 내용 읽기\n"
        "- list_files: 디렉토리 파일 목록 조회\n\n"
        "항상 한국어로 응답하세요."
    )

    # 대화 히스토리 초기화 (시스템 메시지로 시작)
    messages = [{"role": "system", "content": system_prompt}]

    turn_count = 0

    while True:
        # 사용자 입력 받기
        try:
            user_input = input("\n사용자: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n대화를 종료합니다.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "종료"):
            print("\n대화를 종료합니다.")
            break

        # 특수 명령어
        if user_input == "/tokens":
            tokens = estimate_tokens(messages)
            print(f"현재 컨텍스트 크기: 약 {tokens:,} 토큰, {len(messages)} 메시지")
            continue

        if user_input == "/clear":
            messages = [{"role": "system", "content": system_prompt}]
            turn_count = 0
            print("대화 히스토리가 초기화되었습니다.")
            continue

        if user_input == "/history":
            print(f"\n--- 대화 히스토리 ({len(messages)} 메시지) ---")
            for i, msg in enumerate(messages):
                role = msg["role"]
                content = msg.get("content", "")
                if content:
                    preview = content[:100] + ("..." if len(content) > 100 else "")
                    print(f"  [{i}] {role}: {preview}")
                elif msg.get("tool_calls"):
                    names = [tc["function"]["name"] for tc in msg["tool_calls"]]
                    print(f"  [{i}] {role}: tool_calls -> {names}")
            continue

        # 사용자 메시지 추가
        messages.append({"role": "user", "content": user_input})
        turn_count += 1

        # Agent 실행
        print(f"\nAgent (턴 #{turn_count}):")
        response = agent_turn(messages)

        if response:
            # assistant 응답을 히스토리에 추가
            messages.append({"role": "assistant", "content": response})
            print(f"\n{response}")

        # 컨텍스트 크기 정보 표시
        tokens = estimate_tokens(messages)
        print(f"\n  [컨텍스트: ~{tokens:,} 토큰 / {len(messages)} 메시지]")


if __name__ == "__main__":
    main()

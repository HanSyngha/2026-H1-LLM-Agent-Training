"""
CLI Agent 실습 정답: 파일 시스템 탐색/조작 agent + 안전장치

파일 시스템을 탐색하고 조작하는 Agent를 구현합니다.
경로 제한, 명령어 차단, 위험 작업 확인 등의 안전장치를 포함합니다.

실행 방법:
    python exercise_solution.py

의존성:
    pip install requests
"""

import json
import os
import sys
import subprocess
import glob as glob_module
import requests
from datetime import datetime

# 공통 설정 로드
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 안전장치 설정
# ============================================================

# 허용 디렉토리 (이 경로 하위만 접근 가능합니다)
ALLOWED_BASE_DIR = os.path.expanduser("~")

# 차단 명령어 목록입니다
BLOCKED_COMMANDS = ["rm -rf /", "format", "del /s /q", "shutdown", "reboot", "mkfs"]

# 명령어 실행 타임아웃 (초)
COMMAND_TIMEOUT = 15

# 최대 출력 길이 (글자 수)
MAX_OUTPUT_LENGTH = 5000


def validate_path(path: str) -> str:
    """경로를 검증하고 정규화합니다. 허용 범위 밖이면 예외를 발생시킵니다."""
    abs_path = os.path.abspath(os.path.realpath(path))
    if not abs_path.startswith(os.path.abspath(ALLOWED_BASE_DIR)):
        raise PermissionError(f"접근 거부: '{abs_path}'는 허용 범위 밖입니다. 허용: {ALLOWED_BASE_DIR}")
    return abs_path


def check_command_safety(command: str) -> None:
    """명령어의 안전성을 검사합니다."""
    for blocked in BLOCKED_COMMANDS:
        if blocked.lower() in command.lower():
            raise PermissionError(f"차단된 명령어: '{blocked}' 패턴이 감지되었습니다.")


# ============================================================
# 도구 구현 - 3개 이상의 CLI 도구
# ============================================================

def list_directory(path: str = ".") -> str:
    """디렉토리의 파일/폴더 목록을 반환합니다.

    Args:
        path: 조회할 디렉토리 경로
    """
    try:
        safe_path = validate_path(path)
        if not os.path.isdir(safe_path):
            return f"오류: '{safe_path}'는 디렉토리가 아닙니다."

        entries = []
        for item in sorted(os.listdir(safe_path)):
            full = os.path.join(safe_path, item)
            try:
                if os.path.isdir(full):
                    entries.append(f"  [DIR]  {item}/")
                else:
                    size = os.path.getsize(full)
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.1f} KB"
                    else:
                        size_str = f"{size / (1024 * 1024):.1f} MB"
                    entries.append(f"  [FILE] {item} ({size_str})")
            except OSError:
                entries.append(f"  [????] {item}")

        result = f"디렉토리: {safe_path}\n항목 수: {len(entries)}\n"
        result += "-" * 40 + "\n"
        result += "\n".join(entries) if entries else "  (비어있음)"
        return result
    except PermissionError as e:
        return str(e)


def read_file(file_path: str) -> str:
    """파일 내용을 읽어 반환합니다.

    Args:
        file_path: 읽을 파일 경로
    """
    try:
        safe_path = validate_path(file_path)
        if not os.path.exists(safe_path):
            return f"오류: 파일 없음 - {safe_path}"
        if not os.path.isfile(safe_path):
            return f"오류: '{safe_path}'는 파일이 아닙니다."

        file_size = os.path.getsize(safe_path)
        if file_size > 500_000:
            return f"오류: 파일이 너무 큽니다 ({file_size:,} bytes). 500KB 이하만 가능합니다."

        with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(MAX_OUTPUT_LENGTH)

        result = f"=== {safe_path} ({file_size:,} bytes) ===\n{content}"
        if file_size > MAX_OUTPUT_LENGTH:
            result += f"\n\n... (내용이 {MAX_OUTPUT_LENGTH}자에서 잘렸습니다)"
        return result
    except PermissionError as e:
        return str(e)


def search_files(directory: str, pattern: str) -> str:
    """디렉토리에서 패턴과 일치하는 파일을 검색합니다.

    Args:
        directory: 검색할 디렉토리 경로
        pattern: 검색 패턴 (glob 형식, 예: "*.py", "**/*.txt")
    """
    try:
        safe_dir = validate_path(directory)
        if not os.path.isdir(safe_dir):
            return f"오류: '{safe_dir}'는 디렉토리가 아닙니다."

        search_pattern = os.path.join(safe_dir, pattern)
        matches = glob_module.glob(search_pattern, recursive=True)

        if not matches:
            return f"'{pattern}' 패턴과 일치하는 파일이 없습니다."

        results = []
        for match in sorted(matches)[:50]:
            if os.path.isfile(match):
                size = os.path.getsize(match)
                results.append(f"  {match} ({size:,} bytes)")

        header = f"검색: {pattern} (경로: {safe_dir})\n일치: {len(matches)}개\n"
        return header + "\n".join(results)
    except PermissionError as e:
        return str(e)


def run_command(command: str) -> str:
    """시스템 명령어를 실행합니다. (안전장치 포함)

    Args:
        command: 실행할 명령어
    """
    try:
        check_command_safety(command)

        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=COMMAND_TIMEOUT, cwd=os.path.expanduser("~"),
        )

        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"

        output = output.strip() or f"(실행 완료, 종료 코드: {result.returncode})"
        if len(output) > MAX_OUTPUT_LENGTH:
            output = output[:MAX_OUTPUT_LENGTH] + "\n... (출력이 잘렸습니다)"
        return output

    except PermissionError as e:
        return str(e)
    except subprocess.TimeoutExpired:
        return f"오류: 명령어가 {COMMAND_TIMEOUT}초 내에 완료되지 않았습니다."
    except Exception as e:
        return f"명령어 실행 오류: {e}"


# ============================================================
# OpenAI Tool Schema 정의
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "디렉토리의 파일/폴더 목록을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "조회할 디렉토리 경로"},
                },
                "required": ["path"],
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
                    "file_path": {"type": "string", "description": "읽을 파일 경로"},
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "디렉토리에서 패턴과 일치하는 파일을 검색합니다 (glob 패턴).",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "검색 디렉토리 경로"},
                    "pattern": {"type": "string", "description": "검색 패턴 (예: '*.py', '**/*.txt')"},
                },
                "required": ["directory", "pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "시스템 명령어를 실행합니다 (bash). 안전장치가 적용됩니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "실행할 명령어"},
                },
                "required": ["command"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "list_directory": list_directory,
    "read_file": read_file,
    "search_files": search_files,
    "run_command": run_command,
}


# ============================================================
# Agent Loop + 대화형 인터페이스
# ============================================================

def call_llm(messages, tools=None):
    """LLM API를 호출합니다."""
    url = f"{GATEWAY_BASE_URL}/chat/completions"
    payload = {"model": DEFAULT_MODEL, "messages": messages}
    if tools:
        payload["tools"] = tools
    resp = requests.post(url, headers=get_headers(), json=payload,
                         proxies=PROXIES, timeout=120, verify=SSL_VERIFY)
    resp.raise_for_status()
    return resp.json()


def agent_loop(messages, max_iterations=10):
    """Agent Loop를 실행합니다."""
    for iteration in range(1, max_iterations + 1):
        data = call_llm(messages, tools=TOOLS)
        msg = data["choices"][0]["message"]
        tool_calls = msg.get("tool_calls")

        if not tool_calls:
            content = msg.get("content", "")
            messages.append({"role": "assistant", "content": content})
            return content

        messages.append(msg)
        for tc in tool_calls:
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            print(f"  [{iteration}] {name}({json.dumps(args, ensure_ascii=False)[:80]})")

            result = TOOL_FUNCTIONS.get(name, lambda **kw: "알 수 없는 도구")(**args)
            preview = result[:150].replace("\n", " ")
            print(f"       -> {preview}...")

            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})

    return "오류: 최대 반복 횟수 초과"


def main():
    """대화형 CLI Agent를 실행합니다."""
    print("=" * 60)
    print("  CLI Agent (파일 시스템 탐색/조작)")
    print("=" * 60)
    print(f"허용 경로: {ALLOWED_BASE_DIR}")
    print("'종료'로 끝내기, '초기화'로 대화 초기화\n")

    messages = [{
        "role": "system",
        "content": (
            f"당신은 파일 시스템을 탐색하고 관리하는 AI 어시스턴트입니다. "
            f"허용된 경로: {ALLOWED_BASE_DIR} 하위만 접근 가능합니다. "
            f"사용자의 요청에 따라 도구를 활용하여 파일/디렉토리 작업을 수행하세요. "
            f"결과를 한국어로 정리하여 안내하세요."
        ),
    }]

    while True:
        try:
            user_input = input("\n사용자: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break

        if not user_input:
            continue
        if user_input.lower() in ["종료", "quit", "exit"]:
            break
        if user_input.lower() in ["초기화", "reset"]:
            messages = [messages[0]]
            print("[초기화 완료]")
            continue

        messages.append({"role": "user", "content": user_input})
        try:
            response = agent_loop(messages)
            print(f"\nAI: {response}")
        except Exception as e:
            print(f"\n[오류] {e}")


if __name__ == "__main__":
    main()

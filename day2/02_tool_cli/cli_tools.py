"""
CLI/PowerShell 도구 모음

파일 시스템 조작, 명령어 실행 등 CLI 기반 도구를 제공합니다.
모든 도구는 문자열을 반환합니다 (LLM이 소비할 수 있는 형태).

=== 보안 주의사항 ===
1. 명령어 인젝션(Command Injection):
   - 사용자 입력을 직접 shell 명령어에 넣으면 위험합니다.
   - 예: run_command("ls " + user_input) → user_input이 "; rm -rf /"이면?
   - 대책: 허용 명령어 목록(allowlist), shell=False 사용, 입력 검증

2. 경로 순회(Path Traversal):
   - "../../../etc/passwd" 같은 경로로 민감한 파일에 접근 가능
   - 대책: 허용 디렉토리 범위 제한, 경로 정규화 후 검증

3. 자원 고갈(Resource Exhaustion):
   - 무한 실행, 대용량 출력 등
   - 대책: timeout 설정, 출력 크기 제한
"""

import sys
import os
import subprocess
import glob as glob_module

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 설정: 보안 제한
# ============================================================

# 허용 디렉토리 (이 경로 하위만 접근 가능)
# 실제 운영 시에는 더 엄격하게 설정해야 합니다.
ALLOWED_BASE_DIRS = [
    os.path.expanduser("~"),  # 사용자 홈 디렉토리
]

# 명령어 실행 타임아웃 (초)
COMMAND_TIMEOUT = 30

# 최대 출력 길이 (글자 수)
MAX_OUTPUT_LENGTH = 10_000

# 차단 명령어 패턴 (보안)
BLOCKED_COMMANDS = [
    "rm -rf /",
    "format",
    "del /s /q",
    "shutdown",
    "reboot",
    ":(){:|:&};:",  # fork bomb
]


# ============================================================
# 보안 유틸리티
# ============================================================

def _validate_path(path: str) -> str:
    """
    경로를 검증하고 정규화합니다.
    허용된 디렉토리 범위 밖의 경로는 거부합니다.

    Path Traversal 방지:
    1. 경로를 절대경로로 변환 (os.path.abspath)
    2. 심볼릭 링크 해제 (os.path.realpath)
    3. 허용 디렉토리 하위인지 확인
    """
    abs_path = os.path.abspath(os.path.realpath(path))

    for base_dir in ALLOWED_BASE_DIRS:
        if abs_path.startswith(os.path.abspath(base_dir)):
            return abs_path

    raise PermissionError(
        f"접근 거부: '{abs_path}'는 허용된 디렉토리 범위 밖입니다.\n"
        f"허용 범위: {ALLOWED_BASE_DIRS}"
    )


def _check_command_safety(command: str) -> None:
    """
    명령어의 안전성을 검사합니다.
    위험한 명령어 패턴이 감지되면 예외를 발생시킵니다.
    """
    command_lower = command.lower().strip()
    for blocked in BLOCKED_COMMANDS:
        if blocked.lower() in command_lower:
            raise PermissionError(f"차단된 명령어: '{blocked}' 패턴이 감지되었습니다.")


def _truncate_output(output: str) -> str:
    """출력이 너무 길면 잘라냅니다."""
    if len(output) > MAX_OUTPUT_LENGTH:
        return output[:MAX_OUTPUT_LENGTH] + f"\n\n... (출력이 {MAX_OUTPUT_LENGTH}자에서 잘렸습니다)"
    return output


# ============================================================
# 도구 구현
# ============================================================

def run_command(command: str) -> str:
    """
    시스템 명령어를 실행하고 결과를 반환합니다.

    Args:
        command: 실행할 명령어 문자열

    Returns:
        명령어의 stdout + stderr 출력

    주의: 프로덕션 환경에서는 반드시 허용 명령어 목록(allowlist)을
    사용하여 실행 가능한 명령어를 제한해야 합니다.
    """
    _check_command_safety(command)

    try:
        result = subprocess.run(
            command,
            shell=True,  # shell=True는 편리하지만 보안상 주의!
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT,
            cwd=os.path.expanduser("~"),  # 안전한 작업 디렉토리
        )

        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"

        output = output.strip()
        if not output:
            output = f"(명령어 실행 완료, 종료 코드: {result.returncode})"

        return _truncate_output(output)

    except subprocess.TimeoutExpired:
        return f"오류: 명령어가 {COMMAND_TIMEOUT}초 내에 완료되지 않았습니다."
    except Exception as e:
        return f"명령어 실행 오류: {e}"


def run_powershell(script: str) -> str:
    """
    PowerShell 스크립트를 실행합니다.

    Windows 환경에서 PowerShell을 통해 다양한 시스템 관리 작업이 가능합니다.
    WSL에서 실행 시 powershell.exe를 호출합니다.

    Args:
        script: 실행할 PowerShell 스크립트 문자열

    Returns:
        PowerShell 실행 결과
    """
    _check_command_safety(script)

    # PowerShell 실행 파일 경로 (Windows/WSL 대응)
    ps_executables = [
        "powershell.exe",                                    # WSL에서 Windows PowerShell
        "pwsh.exe",                                          # WSL에서 PowerShell Core
        "pwsh",                                              # Linux에 설치된 PowerShell Core
        "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",  # 직접 경로
    ]

    ps_cmd = None
    for exe in ps_executables:
        # which/where 대신 직접 시도
        try:
            result = subprocess.run(
                [exe, "-Command", "echo test"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                ps_cmd = exe
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    if not ps_cmd:
        return "오류: PowerShell을 찾을 수 없습니다. Windows 환경 또는 pwsh 설치가 필요합니다."

    try:
        result = subprocess.run(
            [ps_cmd, "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT,
        )

        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"

        return _truncate_output(output.strip() or f"(실행 완료, 종료 코드: {result.returncode})")

    except subprocess.TimeoutExpired:
        return f"오류: PowerShell 스크립트가 {COMMAND_TIMEOUT}초 내에 완료되지 않았습니다."
    except Exception as e:
        return f"PowerShell 실행 오류: {e}"


def list_directory(path: str = ".") -> str:
    """
    디렉토리의 파일 및 폴더 목록을 반환합니다.

    Args:
        path: 조회할 디렉토리 경로

    Returns:
        파일/폴더 목록 (타입, 이름, 크기 포함)
    """
    try:
        safe_path = _validate_path(path)

        if not os.path.isdir(safe_path):
            return f"오류: '{safe_path}'는 디렉토리가 아닙니다."

        entries = []
        try:
            items = sorted(os.listdir(safe_path))
        except PermissionError:
            return f"오류: '{safe_path}' 디렉토리 읽기 권한이 없습니다."

        for item in items:
            full = os.path.join(safe_path, item)
            try:
                if os.path.isdir(full):
                    entries.append(f"  [DIR]  {item}/")
                else:
                    size = os.path.getsize(full)
                    # 크기를 읽기 좋은 형태로 변환
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.1f} KB"
                    else:
                        size_str = f"{size / (1024 * 1024):.1f} MB"
                    entries.append(f"  [FILE] {item} ({size_str})")
            except OSError:
                entries.append(f"  [????] {item} (접근 불가)")

        result = f"디렉토리: {safe_path}\n"
        result += f"항목 수: {len(entries)}\n"
        result += "-" * 40 + "\n"
        result += "\n".join(entries) if entries else "  (비어있음)"

        return result

    except PermissionError as e:
        return str(e)
    except Exception as e:
        return f"디렉토리 조회 오류: {e}"


def read_file(path: str) -> str:
    """
    파일의 내용을 읽어 반환합니다.

    Args:
        path: 읽을 파일 경로

    Returns:
        파일 내용 (텍스트)
    """
    try:
        safe_path = _validate_path(path)

        if not os.path.exists(safe_path):
            return f"오류: 파일을 찾을 수 없습니다 - {safe_path}"

        if not os.path.isfile(safe_path):
            return f"오류: '{safe_path}'는 파일이 아닙니다."

        # 파일 크기 확인 (너무 큰 파일 방지)
        file_size = os.path.getsize(safe_path)
        if file_size > 500_000:  # 500KB 이상
            return f"오류: 파일이 너무 큽니다 ({file_size:,} bytes). 500KB 이하만 읽을 수 있습니다."

        # 바이너리 파일 감지
        try:
            with open(safe_path, "r", encoding="utf-8") as f:
                content = f.read(MAX_OUTPUT_LENGTH)
        except UnicodeDecodeError:
            return f"오류: 바이너리 파일은 읽을 수 없습니다 - {safe_path}"

        result = f"=== {safe_path} ({file_size:,} bytes) ===\n{content}"

        if file_size > MAX_OUTPUT_LENGTH:
            result += f"\n\n... (파일이 {MAX_OUTPUT_LENGTH}자에서 잘렸습니다)"

        return result

    except PermissionError as e:
        return str(e)
    except Exception as e:
        return f"파일 읽기 오류: {e}"


def write_file(path: str, content: str) -> str:
    """
    파일에 내용을 씁니다. 기존 파일은 덮어씁니다.

    Args:
        path: 쓸 파일 경로
        content: 파일에 쓸 내용

    Returns:
        성공/실패 메시지
    """
    try:
        safe_path = _validate_path(path)

        # 디렉토리가 없으면 생성
        dir_path = os.path.dirname(safe_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)

        size = os.path.getsize(safe_path)
        return f"파일 저장 완료: {safe_path} ({size:,} bytes)"

    except PermissionError as e:
        return str(e)
    except Exception as e:
        return f"파일 쓰기 오류: {e}"


def search_files(directory: str, pattern: str) -> str:
    """
    디렉토리에서 패턴과 일치하는 파일을 검색합니다.

    Args:
        directory: 검색할 디렉토리 경로
        pattern: 검색 패턴 (glob 형식, 예: "*.py", "**/*.txt")

    Returns:
        검색 결과 (일치하는 파일 목록)
    """
    try:
        safe_dir = _validate_path(directory)

        if not os.path.isdir(safe_dir):
            return f"오류: '{safe_dir}'는 디렉토리가 아닙니다."

        # glob으로 파일 검색
        search_pattern = os.path.join(safe_dir, pattern)
        matches = glob_module.glob(search_pattern, recursive=True)

        if not matches:
            return f"'{pattern}' 패턴과 일치하는 파일이 없습니다. (검색 경로: {safe_dir})"

        # 결과 정리
        results = []
        for match in sorted(matches)[:100]:  # 최대 100개
            try:
                if os.path.isfile(match):
                    size = os.path.getsize(match)
                    results.append(f"  [FILE] {match} ({size:,} bytes)")
                else:
                    results.append(f"  [DIR]  {match}/")
            except OSError:
                results.append(f"  [????] {match}")

        header = f"검색 패턴: {pattern}\n검색 경로: {safe_dir}\n일치: {len(matches)}개\n"
        header += "-" * 40 + "\n"

        if len(matches) > 100:
            header += f"(처음 100개만 표시, 전체 {len(matches)}개)\n"

        return header + "\n".join(results)

    except PermissionError as e:
        return str(e)
    except Exception as e:
        return f"파일 검색 오류: {e}"


# ============================================================
# OpenAI Tool Schema 정의
# ============================================================
# 이 스키마들은 cli_agent.py에서 import하여 사용합니다.

CLI_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "시스템 명령어를 실행합니다. Linux/WSL bash 명령어를 실행할 수 있습니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "실행할 명령어 (예: 'ls -la', 'cat file.txt', 'python script.py')",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_powershell",
            "description": "PowerShell 스크립트를 실행합니다. Windows 시스템 관리 작업에 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "실행할 PowerShell 스크립트 (예: 'Get-Process', 'Get-ChildItem C:\\\\')",
                    },
                },
                "required": ["script"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "디렉토리의 파일 및 폴더 목록을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "조회할 디렉토리 경로. 기본값: 현재 디렉토리",
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
                    "path": {
                        "type": "string",
                        "description": "읽을 파일의 경로",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "파일에 내용을 씁니다. 기존 파일은 덮어씁니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "파일 경로",
                    },
                    "content": {
                        "type": "string",
                        "description": "파일에 쓸 내용",
                    },
                },
                "required": ["path", "content"],
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
                    "directory": {
                        "type": "string",
                        "description": "검색할 디렉토리 경로",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "검색 패턴 (glob 형식, 예: '*.py', '**/*.txt')",
                    },
                },
                "required": ["directory", "pattern"],
            },
        },
    },
]

# 도구 이름 -> 함수 매핑
CLI_TOOL_FUNCTIONS = {
    "run_command": run_command,
    "run_powershell": run_powershell,
    "list_directory": list_directory,
    "read_file": read_file,
    "write_file": write_file,
    "search_files": search_files,
}


# ============================================================
# 테스트
# ============================================================

if __name__ == "__main__":
    print("=== CLI 도구 테스트 ===\n")

    # 명령어 실행
    print("[run_command]")
    print(run_command("echo 'Hello, World!'"))
    print()

    # 디렉토리 목록
    print("[list_directory]")
    print(list_directory("."))
    print()

    # 파일 읽기
    print("[read_file]")
    print(read_file(__file__))
    print()

    # 파일 검색
    print("[search_files]")
    print(search_files(os.path.dirname(__file__), "*.py"))

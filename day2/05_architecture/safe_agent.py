"""
안전장치가 포함된 Agent

프로덕션 환경에서 Agent를 안전하게 운영하기 위한 패턴입니다.

=== 안전 기능 ===
1. 위험 작업 사전 확인 (사용자 승인 필요)
2. 허용/차단 명령어 목록
3. 경로 샌드박싱 (특정 디렉토리만 접근 허용)
4. 속도 제한 (Rate Limiting)
5. 도구 실행 로깅
6. 최대 반복 제한 (무한 루프 방지)
"""

import sys
import os
import json
import time
import logging
import requests
from datetime import datetime
from typing import Any, Callable

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 로깅 설정
# ============================================================

def setup_logger(log_file: str = "agent_log.jsonl") -> logging.Logger:
    """
    도구 실행 로거를 설정합니다.

    JSONL (JSON Lines) 형식으로 로그를 기록합니다.
    각 줄이 독립적인 JSON 객체이므로 파싱이 쉽습니다.
    """
    logger = logging.getLogger("safe_agent")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # 파일 핸들러 (JSONL 형식)
        abs_log_path = os.path.abspath(log_file)
        os.makedirs(os.path.dirname(abs_log_path) if os.path.dirname(abs_log_path) else ".", exist_ok=True)
        fh = logging.FileHandler(abs_log_path, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(fh)

        # 콘솔 핸들러 (읽기 쉬운 형식)
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(ch)

    return logger


# ============================================================
# 안전 정책 설정
# ============================================================

class SafetyPolicy:
    """Agent의 안전 정책을 정의합니다."""

    def __init__(
        self,
        # 경로 샌드박스: 이 디렉토리 하위만 접근 허용
        allowed_paths: list[str] | None = None,
        # 차단 명령어 패턴
        blocked_commands: list[str] | None = None,
        # 위험 도구 목록 (실행 전 사용자 확인 필요)
        dangerous_tools: list[str] | None = None,
        # 최대 반복 횟수
        max_iterations: int = 20,
        # 속도 제한 (초당 도구 호출 횟수)
        rate_limit_per_second: float = 2.0,
        # 최대 도구 호출 횟수 (전체 대화)
        max_total_tool_calls: int = 100,
    ):
        self.allowed_paths = allowed_paths or [os.path.expanduser("~")]
        self.blocked_commands = blocked_commands or [
            "rm -rf",
            "format",
            "del /s /q",
            "shutdown",
            "reboot",
            "mkfs",
            "dd if=",
            "> /dev/sd",
        ]
        self.dangerous_tools = dangerous_tools or [
            "run_command",
            "run_powershell",
            "write_file",
            "click_at",
            "type_text",
        ]
        self.max_iterations = max_iterations
        self.rate_limit_per_second = rate_limit_per_second
        self.max_total_tool_calls = max_total_tool_calls


# ============================================================
# Rate Limiter
# ============================================================

class RateLimiter:
    """
    간단한 토큰 버킷 방식의 속도 제한기입니다.

    일정 시간 내에 너무 많은 도구 호출이 발생하면 대기합니다.
    무한 루프에 빠졌을 때 시스템 부하를 제한하는 역할을 합니다.
    """

    def __init__(self, calls_per_second: float = 2.0):
        self._min_interval = 1.0 / calls_per_second
        self._last_call_time = 0.0

    def wait_if_needed(self):
        """필요한 경우 대기합니다."""
        elapsed = time.time() - self._last_call_time
        if elapsed < self._min_interval:
            wait_time = self._min_interval - elapsed
            time.sleep(wait_time)
        self._last_call_time = time.time()


# ============================================================
# 안전 검사기
# ============================================================

class SafetyChecker:
    """도구 실행 전 안전성을 검사합니다."""

    def __init__(self, policy: SafetyPolicy):
        self.policy = policy

    def check_path(self, path: str) -> tuple[bool, str]:
        """
        경로가 허용된 범위 내인지 검사합니다.

        Returns:
            (허용 여부, 메시지)
        """
        abs_path = os.path.abspath(os.path.realpath(path))

        for allowed in self.policy.allowed_paths:
            allowed_abs = os.path.abspath(allowed)
            if abs_path.startswith(allowed_abs):
                return True, f"경로 허용: {abs_path}"

        return False, (
            f"경로 접근 거부: {abs_path}\n"
            f"허용 경로: {self.policy.allowed_paths}"
        )

    def check_command(self, command: str) -> tuple[bool, str]:
        """
        명령어가 안전한지 검사합니다.

        Returns:
            (허용 여부, 메시지)
        """
        command_lower = command.lower().strip()

        for blocked in self.policy.blocked_commands:
            if blocked.lower() in command_lower:
                return False, f"차단된 명령어: '{blocked}' 패턴이 감지되었습니다."

        return True, "명령어 허용"

    def is_dangerous_tool(self, tool_name: str) -> bool:
        """위험 도구인지 확인합니다."""
        return tool_name in self.policy.dangerous_tools

    def check_tool_arguments(self, tool_name: str, arguments: dict) -> tuple[bool, str]:
        """
        도구의 인자를 검사합니다.

        경로 관련 인자는 샌드박스 검사를,
        명령어 관련 인자는 명령어 안전 검사를 수행합니다.
        """
        # 경로 관련 파라미터 검사
        path_params = ["path", "file_path", "directory"]
        for param in path_params:
            if param in arguments:
                ok, msg = self.check_path(arguments[param])
                if not ok:
                    return False, msg

        # 명령어 관련 파라미터 검사
        command_params = ["command", "script"]
        for param in command_params:
            if param in arguments:
                ok, msg = self.check_command(arguments[param])
                if not ok:
                    return False, msg

        return True, "인자 검사 통과"


# ============================================================
# 안전한 Agent
# ============================================================

class SafeAgent:
    """
    안전장치가 포함된 Agent입니다.

    모든 도구 실행에 대해:
    1. 안전 검사 수행
    2. 위험 도구는 사용자 확인
    3. 속도 제한 적용
    4. 실행 로그 기록
    5. 반복 횟수 제한
    """

    def __init__(
        self,
        tool_schemas: list[dict],
        tool_functions: dict[str, Callable],
        policy: SafetyPolicy | None = None,
        system_prompt: str = "",
        log_file: str = "agent_log.jsonl",
        auto_confirm: bool = False,
    ):
        """
        Args:
            tool_schemas: OpenAI Tool Schema 리스트
            tool_functions: 도구 이름 -> 함수 매핑
            policy: 안전 정책 (기본값 사용)
            system_prompt: 시스템 프롬프트
            log_file: 로그 파일 경로
            auto_confirm: 위험 작업 자동 승인 여부 (테스트용)
        """
        self.tool_schemas = tool_schemas
        self.tool_functions = tool_functions
        self.policy = policy or SafetyPolicy()
        self.system_prompt = system_prompt
        self.auto_confirm = auto_confirm

        self.logger = setup_logger(log_file)
        self.safety_checker = SafetyChecker(self.policy)
        self.rate_limiter = RateLimiter(self.policy.rate_limit_per_second)

        # 통계
        self.total_tool_calls = 0
        self.session_start = datetime.now()

    def _log_event(self, event_type: str, data: dict):
        """이벤트를 JSONL 형식으로 로그에 기록합니다."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            **data,
        }
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

    def _confirm_dangerous_action(self, tool_name: str, arguments: dict) -> bool:
        """
        위험한 작업 실행 전에 사용자 확인을 받습니다.

        Returns:
            True: 실행 허용
            False: 실행 거부
        """
        if self.auto_confirm:
            return True

        print(f"\n{'=' * 50}")
        print(f"[주의] 위험 도구 실행 확인")
        print(f"{'=' * 50}")
        print(f"도구: {tool_name}")
        print(f"인자: {json.dumps(arguments, ensure_ascii=False, indent=2)}")
        print(f"{'=' * 50}")

        try:
            response = input("실행하시겠습니까? (y/n): ").strip().lower()
            approved = response in ("y", "yes")

            self._log_event("confirmation", {
                "tool": tool_name,
                "arguments": arguments,
                "approved": approved,
            })

            return approved
        except (EOFError, KeyboardInterrupt):
            return False

    def execute_tool(self, tool_name: str, arguments: dict) -> str:
        """
        안전 검사를 거쳐 도구를 실행합니다.

        실행 전:
        1. 도구 존재 확인
        2. 인자 안전 검사 (경로, 명령어)
        3. 위험 도구 사용자 확인
        4. 속도 제한 대기
        5. 총 호출 횟수 확인

        실행 후:
        6. 결과 로그 기록
        """
        # 총 호출 횟수 확인
        if self.total_tool_calls >= self.policy.max_total_tool_calls:
            msg = f"도구 호출 한도 초과 ({self.policy.max_total_tool_calls}회)"
            self._log_event("limit_exceeded", {"tool": tool_name, "total_calls": self.total_tool_calls})
            return f"오류: {msg}"

        # 도구 존재 확인
        if tool_name not in self.tool_functions:
            return f"오류: 알 수 없는 도구 '{tool_name}'"

        # 인자 안전 검사
        ok, msg = self.safety_checker.check_tool_arguments(tool_name, arguments)
        if not ok:
            self._log_event("blocked", {"tool": tool_name, "arguments": arguments, "reason": msg})
            return f"안전 검사 실패: {msg}"

        # 위험 도구 확인
        if self.safety_checker.is_dangerous_tool(tool_name):
            if not self._confirm_dangerous_action(tool_name, arguments):
                self._log_event("rejected", {"tool": tool_name, "arguments": arguments})
                return f"사용자가 '{tool_name}' 실행을 거부했습니다."

        # 속도 제한
        self.rate_limiter.wait_if_needed()

        # 도구 실행
        self.total_tool_calls += 1
        start_time = time.time()

        try:
            func = self.tool_functions[tool_name]
            result = str(func(**arguments))

            elapsed = time.time() - start_time

            self._log_event("executed", {
                "tool": tool_name,
                "arguments": arguments,
                "result_length": len(result),
                "elapsed_seconds": round(elapsed, 3),
                "total_calls": self.total_tool_calls,
            })

            return result

        except Exception as e:
            elapsed = time.time() - start_time

            self._log_event("error", {
                "tool": tool_name,
                "arguments": arguments,
                "error": str(e),
                "elapsed_seconds": round(elapsed, 3),
            })

            return f"도구 실행 오류 ({tool_name}): {e}"

    def call_llm(self, messages: list[dict]) -> dict:
        """LLM API를 호출합니다."""
        url = f"{GATEWAY_BASE_URL}/chat/completions"
        headers = get_headers()

        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "tools": self.tool_schemas,
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            proxies=PROXIES,
            timeout=120,
        )
        response.raise_for_status()
        return response.json()

    def run(self, user_message: str, messages: list[dict] | None = None) -> str:
        """
        Agent를 실행합니다.

        Args:
            user_message: 사용자 입력
            messages: 대화 히스토리 (None이면 새로 생성)

        Returns:
            Agent의 최종 응답
        """
        if messages is None:
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})

        messages.append({"role": "user", "content": user_message})

        self._log_event("user_input", {"message": user_message})

        for iteration in range(1, self.policy.max_iterations + 1):
            response_data = self.call_llm(messages)
            assistant_message = response_data["choices"][0]["message"]
            tool_calls = assistant_message.get("tool_calls")

            if not tool_calls:
                content = assistant_message.get("content", "")
                messages.append({"role": "assistant", "content": content})
                self._log_event("final_response", {
                    "iteration": iteration,
                    "response_length": len(content),
                    "total_tool_calls": self.total_tool_calls,
                })
                return content

            messages.append(assistant_message)

            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                arguments = json.loads(tc["function"]["arguments"])
                tool_call_id = tc["id"]

                print(f"  [{iteration}] {tool_name}({json.dumps(arguments, ensure_ascii=False)[:100]})")

                result = self.execute_tool(tool_name, arguments)

                preview = result[:200].replace("\n", " ")
                if len(result) > 200:
                    preview += "..."
                print(f"       → {preview}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result,
                })

        # 최대 반복 초과
        self._log_event("max_iterations", {
            "iterations": self.policy.max_iterations,
            "total_tool_calls": self.total_tool_calls,
        })
        return f"오류: 최대 반복 횟수({self.policy.max_iterations})를 초과했습니다."

    def get_stats(self) -> dict:
        """현재 세션 통계를 반환합니다."""
        elapsed = (datetime.now() - self.session_start).total_seconds()
        return {
            "session_duration_seconds": round(elapsed, 1),
            "total_tool_calls": self.total_tool_calls,
            "remaining_calls": self.policy.max_total_tool_calls - self.total_tool_calls,
        }


# ============================================================
# 사용 예시
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("안전한 Agent 데모")
    print("=" * 60)

    # 간단한 도구 정의 (데모용)
    def calculator(expression: str) -> str:
        """수학 표현식을 계산합니다."""
        import math
        allowed = {"abs": abs, "round": round, "sqrt": math.sqrt, "pi": math.pi}
        try:
            result = eval(expression, {"__builtins__": {}}, allowed)
            return f"계산 결과: {expression} = {result}"
        except Exception as e:
            return f"계산 오류: {e}"

    def read_file_safe(path: str) -> str:
        """파일을 읽습니다."""
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            return f"파일 없음: {abs_path}"
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(5000)
        return content

    tool_schemas = [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "수학 표현식을 계산합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "계산할 수식"},
                    },
                    "required": ["expression"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file_safe",
                "description": "파일 내용을 읽습니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "파일 경로"},
                    },
                    "required": ["path"],
                },
            },
        },
    ]

    tool_functions = {
        "calculator": calculator,
        "read_file_safe": read_file_safe,
    }

    # 안전 정책 설정
    policy = SafetyPolicy(
        allowed_paths=[os.path.expanduser("~")],
        max_iterations=10,
        rate_limit_per_second=5.0,
        max_total_tool_calls=50,
    )

    # Agent 생성
    agent = SafeAgent(
        tool_schemas=tool_schemas,
        tool_functions=tool_functions,
        policy=policy,
        system_prompt="당신은 안전한 AI 어시스턴트입니다. 한국어로 응답하세요.",
        log_file="/tmp/safe_agent_demo.jsonl",
        auto_confirm=True,  # 데모에서는 자동 승인
    )

    # Agent 실행
    print("\n[질문] 1234 * 5678 계산해줘")
    result = agent.run("1234 * 5678 계산해줘")
    print(f"\n[응답] {result}")

    # 통계 확인
    print(f"\n[통계] {json.dumps(agent.get_stats(), ensure_ascii=False)}")

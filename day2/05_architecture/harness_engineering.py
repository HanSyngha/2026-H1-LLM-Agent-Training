"""
Harness Engineering (하네스 엔지니어링)

Agent 시스템의 비모델(non-model) 부분을 체계적으로 설계하는 패턴입니다.

=== 핵심 비유 ===
모델 = 엔진 (LLM이 제공하는 추론 능력)
하네스 = 자동차 (엔진을 감싸서 안전하고 유용하게 만드는 모든 것)

자동차에서 엔진만으로는 달릴 수 없듯이,
LLM만으로는 프로덕션 Agent를 만들 수 없습니다.
핸들, 브레이크, 계기판, 안전벨트 — 이것들이 하네스입니다.

=== 5 Pillars of Harness Engineering ===
1. Tool Orchestration  - 도구 등록, 스키마 자동 생성, 실행 관리
2. Guardrails          - 5단계 방어 (prompt → schema → runtime → tool → hooks)
3. Error Recovery      - 재시도, 루프 감지, 롤백
4. Observability       - 액션 로깅, 토큰 추적
5. Human-in-the-Loop   - 위험 작업 승인 게이트

=== 참고 아키텍처 ===
- Claude Code: 단일 스레드 마스터 루프, 전체 컨텍스트를 하나의 대화로 관리
- Cursor: 모델별 하네스 튜닝 (Claude/GPT 각각 다른 시스템 프롬프트)
"""

import sys
import os
import json
import time
import hashlib
import logging
import inspect
import functools
from datetime import datetime
from typing import Any, Callable
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ╔══════════════════════════════════════════════════════════════╗
# ║  Pillar 1: Tool Orchestration (도구 오케스트레이션)           ║
# ║  - 도구 등록/관리의 중앙 허브                                ║
# ║  - Python 함수 → OpenAI Tool Schema 자동 변환              ║
# ║  - 도구 실행의 단일 진입점                                  ║
# ╚══════════════════════════════════════════════════════════════╝

# Python 타입 → JSON Schema 타입 매핑
_TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


class ToolRegistry:
    """
    도구 등록 및 관리 레지스트리.

    하네스의 첫 번째 기둥: 도구 오케스트레이션.
    모든 도구를 중앙에서 관리하며, 스키마 자동 생성과 실행을 담당합니다.

    사용법:
        registry = ToolRegistry()

        @registry.tool(description="파일을 읽습니다")
        def read_file(path: str) -> str:
            with open(path) as f:
                return f.read()

        # 자동 생성된 OpenAI Tool Schema
        schemas = registry.get_schemas()

        # 도구 실행
        result = registry.execute("read_file", {"path": "test.py"})
    """

    def __init__(self):
        # 등록된 도구: {이름: {"func": callable, "schema": dict}}
        self._tools: dict[str, dict] = {}

    def tool(self, description: str | None = None) -> Callable:
        """
        도구 등록 데코레이터.

        함수의 시그니처와 타입 힌트를 분석하여
        OpenAI Tool Schema를 자동으로 생성합니다.
        """
        def decorator(func: Callable) -> Callable:
            name = func.__name__
            desc = description or (func.__doc__ or "").strip().split("\n")[0]

            # 스키마 자동 생성
            schema = self._generate_schema(func, name, desc)
            self._tools[name] = {"func": func, "schema": schema}
            return func
        return decorator

    def _generate_schema(self, func: Callable, name: str, description: str) -> dict:
        """
        함수 시그니처에서 OpenAI Tool Schema를 자동 생성합니다.

        inspect 모듈로 파라미터 이름, 타입 힌트, 기본값을 추출하고
        JSON Schema 형식으로 변환합니다.
        """
        sig = inspect.signature(func)
        try:
            hints = inspect.get_annotations(func)
        except Exception:
            hints = {}

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            # 타입 힌트 → JSON Schema 타입
            py_type = hints.get(param_name, str)
            json_type = _TYPE_MAP.get(py_type, "string")

            properties[param_name] = {"type": json_type}

            # 기본값이 없는 파라미터는 필수
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def get_schemas(self) -> list[dict]:
        """등록된 모든 도구의 OpenAI Tool Schema를 반환합니다."""
        return [t["schema"] for t in self._tools.values()]

    def get_functions(self) -> dict[str, Callable]:
        """도구 이름 → 함수 매핑을 반환합니다."""
        return {name: t["func"] for name, t in self._tools.items()}

    def execute(self, name: str, arguments: dict) -> str:
        """도구를 실행하고 결과를 문자열로 반환합니다."""
        if name not in self._tools:
            return f"오류: 알 수 없는 도구 '{name}'"
        try:
            result = self._tools[name]["func"](**arguments)
            return str(result)
        except Exception as e:
            return f"도구 실행 오류 ({name}): {e}"

    def list_tools(self) -> list[str]:
        """등록된 도구 이름 목록을 반환합니다."""
        return list(self._tools.keys())


# ╔══════════════════════════════════════════════════════════════╗
# ║  Pillar 2: Guardrails (가드레일 - 5단계 방어)               ║
# ║  1. Prompt 레벨: 시스템 프롬프트에 규칙 명시                  ║
# ║  2. Schema 레벨: 파라미터 유효성 검증                        ║
# ║  3. Runtime 레벨: 실행 시간 제한, 호출 횟수 제한              ║
# ║  4. Tool 레벨: 도구별 접근 제어                              ║
# ║  5. Hook 레벨: 실행 전후 커스텀 로직                         ║
# ╚══════════════════════════════════════════════════════════════╝

@dataclass
class GuardrailConfig:
    """가드레일 설정"""
    # Layer 2: Schema 검증
    max_string_length: int = 10000      # 문자열 파라미터 최대 길이
    max_array_length: int = 100         # 배열 파라미터 최대 길이

    # Layer 3: Runtime 제한
    max_tool_calls: int = 100           # 최대 도구 호출 횟수
    max_iterations: int = 20            # 최대 반복 횟수
    tool_timeout_seconds: float = 30.0  # 도구 실행 시간 제한

    # Layer 4: Tool 접근 제어
    allowed_paths: list[str] = field(default_factory=lambda: [os.path.expanduser("~")])
    blocked_commands: list[str] = field(default_factory=lambda: [
        "rm -rf /", "format", "shutdown", "reboot", "mkfs",
    ])
    dangerous_tools: list[str] = field(default_factory=lambda: [
        "write_file", "run_command", "delete_file",
    ])


class GuardrailSystem:
    """
    5단계 가드레일 시스템.

    각 도구 실행 요청에 대해 5개 레이어를 순차적으로 통과시킵니다.
    어느 레이어에서든 실패하면 실행을 차단합니다.

    방어 순서:
    1. Prompt  → 시스템 프롬프트에 규칙이 이미 포함 (LLM이 자체 준수)
    2. Schema  → 파라미터 유효성 검증 (타입, 길이, 범위)
    3. Runtime → 호출 횟수, 실행 시간 제한
    4. Tool    → 경로 샌드박스, 명령어 차단
    5. Hook    → 커스텀 전/후 처리 로직
    """

    def __init__(self, config: GuardrailConfig | None = None):
        self.config = config or GuardrailConfig()
        self._call_count = 0
        self._pre_hooks: list[Callable] = []
        self._post_hooks: list[Callable] = []

    # --- Layer 2: Schema 검증 ---
    def validate_schema(self, tool_name: str, arguments: dict) -> tuple[bool, str]:
        """
        파라미터 스키마를 검증합니다.

        문자열 길이, 배열 크기 등 기본적인 입력 제약을 확인합니다.
        악의적으로 거대한 입력을 넣어 시스템을 마비시키는 것을 방지합니다.
        """
        for key, value in arguments.items():
            if isinstance(value, str) and len(value) > self.config.max_string_length:
                return False, f"파라미터 '{key}' 길이 초과: {len(value)} > {self.config.max_string_length}"
            if isinstance(value, list) and len(value) > self.config.max_array_length:
                return False, f"파라미터 '{key}' 배열 크기 초과: {len(value)} > {self.config.max_array_length}"
        return True, "스키마 검증 통과"

    # --- Layer 3: Runtime 제한 ---
    def check_runtime_limits(self) -> tuple[bool, str]:
        """
        런타임 제한을 확인합니다.

        도구 호출 횟수가 한계를 넘지 않았는지 확인합니다.
        무한 루프에 빠진 에이전트를 강제로 멈추는 안전장치입니다.
        """
        if self._call_count >= self.config.max_tool_calls:
            return False, f"도구 호출 한도 초과: {self._call_count}/{self.config.max_tool_calls}"
        return True, "런타임 제한 통과"

    # --- Layer 4: Tool 접근 제어 ---
    def check_tool_access(self, tool_name: str, arguments: dict) -> tuple[bool, str]:
        """
        도구별 접근 제어를 수행합니다.

        경로 파라미터는 샌드박스 범위 내인지 확인하고,
        명령어 파라미터는 차단 목록과 대조합니다.
        """
        # 경로 검사
        for param in ("path", "file_path", "directory"):
            if param in arguments:
                abs_path = os.path.abspath(arguments[param])
                allowed = any(
                    abs_path.startswith(os.path.abspath(p))
                    for p in self.config.allowed_paths
                )
                if not allowed:
                    return False, f"경로 접근 거부: {abs_path}"

        # 명령어 검사
        for param in ("command", "script"):
            if param in arguments:
                cmd = arguments[param].lower()
                for blocked in self.config.blocked_commands:
                    if blocked.lower() in cmd:
                        return False, f"차단된 명령어 패턴: '{blocked}'"

        return True, "도구 접근 제어 통과"

    # --- Layer 5: Hook 시스템 ---
    def add_pre_hook(self, hook: Callable):
        """
        도구 실행 전에 호출되는 훅을 등록합니다.

        훅 시그니처: hook(tool_name: str, arguments: dict) -> (bool, str)
        False를 반환하면 실행을 차단합니다.
        """
        self._pre_hooks.append(hook)

    def add_post_hook(self, hook: Callable):
        """
        도구 실행 후에 호출되는 훅을 등록합니다.

        훅 시그니처: hook(tool_name: str, arguments: dict, result: str) -> str
        결과를 변환하거나 필터링할 수 있습니다.
        """
        self._post_hooks.append(hook)

    def run_pre_hooks(self, tool_name: str, arguments: dict) -> tuple[bool, str]:
        """모든 pre-hook을 실행합니다."""
        for hook in self._pre_hooks:
            try:
                ok, msg = hook(tool_name, arguments)
                if not ok:
                    return False, f"Pre-hook 차단: {msg}"
            except Exception as e:
                return False, f"Pre-hook 오류: {e}"
        return True, "Pre-hook 통과"

    def run_post_hooks(self, tool_name: str, arguments: dict, result: str) -> str:
        """모든 post-hook을 실행하여 결과를 변환합니다."""
        for hook in self._post_hooks:
            try:
                result = hook(tool_name, arguments, result)
            except Exception as e:
                # post-hook 실패는 결과에 영향을 주지 않음
                pass
        return result

    def check_all(self, tool_name: str, arguments: dict) -> tuple[bool, str]:
        """
        모든 가드레일 레이어를 순차적으로 확인합니다.

        Layer 1 (Prompt)은 시스템 프롬프트에 포함되므로 여기서는 Layer 2~5를 확인합니다.
        """
        # Layer 2: Schema 검증
        ok, msg = self.validate_schema(tool_name, arguments)
        if not ok:
            return False, f"[Schema] {msg}"

        # Layer 3: Runtime 제한
        ok, msg = self.check_runtime_limits()
        if not ok:
            return False, f"[Runtime] {msg}"

        # Layer 4: Tool 접근 제어
        ok, msg = self.check_tool_access(tool_name, arguments)
        if not ok:
            return False, f"[Tool] {msg}"

        # Layer 5: Pre-hooks
        ok, msg = self.run_pre_hooks(tool_name, arguments)
        if not ok:
            return False, f"[Hook] {msg}"

        self._call_count += 1
        return True, "모든 가드레일 통과"


# ╔══════════════════════════════════════════════════════════════╗
# ║  Pillar 3: Error Recovery (에러 복구)                       ║
# ║  - 지수 백오프 재시도                                       ║
# ║  - 루프 감지 (동일 도구 반복 호출 탐지)                      ║
# ║  - 롤백 메커니즘                                           ║
# ╚══════════════════════════════════════════════════════════════╝

class ErrorRecovery:
    """
    에러 복구 시스템.

    Agent가 실패했을 때 어떻게 복구할지를 관리합니다.
    단순 재시도부터 지능적인 루프 감지, 롤백까지 포함합니다.
    """

    def __init__(self, max_retries: int = 3, max_loop_count: int = 3):
        self.max_retries = max_retries
        self.max_loop_count = max_loop_count
        # 최근 호출 기록 (루프 감지용)
        self._recent_calls: list[str] = []
        # 롤백 스택 (실행 취소를 위한 역작업 저장)
        self._rollback_stack: list[Callable] = []

    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """
        지수 백오프로 함수를 재시도합니다.

        실패 시 대기 시간을 지수적으로 증가시켜 재시도합니다.
        API rate limit, 일시적 네트워크 오류 등에 효과적입니다.

        대기 시간: 1초 → 2초 → 4초 → 8초 → ...
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                wait_time = 2 ** attempt  # 지수 백오프: 1, 2, 4, 8, ...
                print(f"    [재시도] {attempt + 1}/{self.max_retries} - "
                      f"{wait_time}초 후 재시도 (오류: {e})")
                time.sleep(wait_time)

        raise last_error

    def detect_loop(self, tool_name: str, arguments: dict) -> bool:
        """
        루프를 감지합니다.

        동일한 도구를 동일한 인자로 반복 호출하면 루프로 판단합니다.
        Agent가 같은 실수를 반복하는 것을 방지합니다.

        Returns:
            True이면 루프 감지됨 (차단해야 함)
        """
        # 호출 시그니처 생성 (도구명 + 인자의 해시)
        call_signature = f"{tool_name}:{hashlib.md5(json.dumps(arguments, sort_keys=True).encode()).hexdigest()}"

        self._recent_calls.append(call_signature)

        # 최근 N개 호출에서 동일 시그니처가 M번 이상이면 루프
        recent_window = self._recent_calls[-10:]  # 최근 10개 확인
        count = recent_window.count(call_signature)

        if count >= self.max_loop_count:
            print(f"    [루프 감지] '{tool_name}'이(가) {count}번 반복 호출됨")
            return True

        return False

    def push_rollback(self, rollback_fn: Callable):
        """
        롤백 함수를 스택에 추가합니다.

        도구가 파일을 수정하기 전에 원본 백업 함수를 등록하면,
        에러 발생 시 원상 복구할 수 있습니다.
        """
        self._rollback_stack.append(rollback_fn)

    def rollback_all(self):
        """
        모든 롤백을 실행합니다.

        스택의 역순으로 실행하여 가장 최근 작업부터 되돌립니다.
        (undo 순서: 마지막 작업 → 첫 번째 작업)
        """
        print(f"    [롤백] {len(self._rollback_stack)}개 작업 롤백 시작")
        while self._rollback_stack:
            rollback_fn = self._rollback_stack.pop()
            try:
                rollback_fn()
            except Exception as e:
                print(f"    [롤백 실패] {e}")
        print(f"    [롤백] 완료")

    def clear_history(self):
        """호출 기록과 롤백 스택을 초기화합니다."""
        self._recent_calls.clear()
        self._rollback_stack.clear()


# ╔══════════════════════════════════════════════════════════════╗
# ║  Pillar 4: Observability (관측 가능성)                      ║
# ║  - 모든 액션 JSONL 로깅                                    ║
# ║  - 토큰 사용량 추적                                        ║
# ║  - 성능 메트릭 수집                                        ║
# ╚══════════════════════════════════════════════════════════════╝

class ObservabilitySystem:
    """
    관측 가능성 시스템.

    Agent의 모든 행동을 기록하고 추적합니다.
    문제가 발생했을 때 "왜 Agent가 그런 결정을 했는지"를
    사후 분석할 수 있게 해줍니다.

    기록 항목:
    - 도구 호출 내역 (이름, 인자, 결과, 소요 시간)
    - LLM API 호출 (모델, 토큰 사용량, 비용)
    - 에러 및 가드레일 차단 이벤트
    - 전체 세션 통계
    """

    def __init__(self, log_file: str = "/tmp/agent_harness.jsonl"):
        self._log_file = log_file
        self._session_start = datetime.now()

        # 토큰 사용량 추적
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._total_api_calls = 0

        # 도구 호출 추적
        self._tool_call_count = 0
        self._tool_call_durations: list[float] = []

        # 로거 설정
        self._logger = logging.getLogger("harness")
        self._logger.setLevel(logging.INFO)
        if not self._logger.handlers:
            os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(fh)

    def log_event(self, event_type: str, data: dict):
        """이벤트를 JSONL 로그에 기록합니다."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            **data,
        }
        self._logger.info(json.dumps(entry, ensure_ascii=False))

    def log_tool_call(self, tool_name: str, arguments: dict, result: str, elapsed: float):
        """도구 호출을 기록합니다."""
        self._tool_call_count += 1
        self._tool_call_durations.append(elapsed)

        self.log_event("tool_call", {
            "tool": tool_name,
            "arguments": arguments,
            "result_length": len(result),
            "elapsed_seconds": round(elapsed, 3),
            "call_number": self._tool_call_count,
        })

    def log_llm_call(self, model: str, input_tokens: int, output_tokens: int):
        """LLM API 호출을 기록합니다."""
        self._total_api_calls += 1
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens

        self.log_event("llm_call", {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "api_call_number": self._total_api_calls,
        })

    def log_guardrail_block(self, tool_name: str, reason: str):
        """가드레일 차단을 기록합니다."""
        self.log_event("guardrail_block", {
            "tool": tool_name,
            "reason": reason,
        })

    def get_session_stats(self) -> dict:
        """현재 세션의 통계를 반환합니다."""
        elapsed = (datetime.now() - self._session_start).total_seconds()
        avg_tool_duration = (
            sum(self._tool_call_durations) / len(self._tool_call_durations)
            if self._tool_call_durations else 0
        )

        return {
            "session_duration_seconds": round(elapsed, 1),
            "total_api_calls": self._total_api_calls,
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "total_tokens": self._total_input_tokens + self._total_output_tokens,
            "tool_calls": self._tool_call_count,
            "avg_tool_duration_seconds": round(avg_tool_duration, 3),
        }


# ╔══════════════════════════════════════════════════════════════╗
# ║  Pillar 5: Human-in-the-Loop (사람 개입)                    ║
# ║  - 위험 작업에 대한 확인 게이트                              ║
# ║  - 점진적 신뢰 모델 (Progressive Trust)                     ║
# ╚══════════════════════════════════════════════════════════════╝

class HumanGate:
    """
    사람 개입 게이트.

    위험 수준에 따라 자동 승인 / 확인 요청 / 차단을 결정합니다.

    점진적 신뢰 모델 (Progressive Trust):
    ─────────────────────────────────────
    Level 0: 읽기 전용     → 자동 승인 (read_file, search 등)
    Level 1: 안전한 쓰기    → 자동 승인 (write to sandbox)
    Level 2: 일반 작업     → 요약 후 자동 승인
    Level 3: 위험 작업     → 사용자 확인 필요 (delete, execute)
    Level 4: 치명적 작업   → 무조건 차단 (system commands)

    이 모델은 Claude Code의 --allowedTools 옵션과 유사합니다.
    사용자가 한 번 승인한 도구는 이후 자동으로 허용할 수 있습니다.
    """

    # 도구별 위험 수준 매핑
    TRUST_LEVELS = {
        # Level 0: 읽기 전용 (자동 승인)
        "read_file": 0,
        "search_files": 0,
        "list_directory": 0,
        "get_file_info": 0,

        # Level 1: 안전한 쓰기
        "write_file": 1,
        "create_directory": 1,

        # Level 2: 일반 작업
        "run_test": 2,
        "install_package": 2,

        # Level 3: 위험 작업 (확인 필요)
        "run_command": 3,
        "delete_file": 3,
        "modify_config": 3,

        # Level 4: 치명적 작업 (차단)
        "run_as_root": 4,
        "format_disk": 4,
        "shutdown_system": 4,
    }

    def __init__(self, auto_approve_level: int = 1, auto_confirm: bool = False):
        """
        Args:
            auto_approve_level: 이 레벨 이하는 자동 승인 (기본: 1)
            auto_confirm: True면 모든 확인을 자동 승인 (테스트용)
        """
        self.auto_approve_level = auto_approve_level
        self.auto_confirm = auto_confirm
        # 세션 중 사용자가 승인한 도구 (한 번 승인하면 이후 자동 허용)
        self._approved_tools: set[str] = set()

    def check(self, tool_name: str, arguments: dict) -> tuple[bool, str]:
        """
        도구 실행의 승인 여부를 결정합니다.

        Returns:
            (승인 여부, 메시지)
        """
        level = self.TRUST_LEVELS.get(tool_name, 3)  # 알 수 없는 도구는 Level 3

        # Level 4: 무조건 차단
        if level >= 4:
            return False, f"차단: '{tool_name}'은(는) 실행할 수 없는 도구입니다"

        # 자동 승인 레벨 이하
        if level <= self.auto_approve_level:
            return True, f"자동 승인 (Level {level})"

        # 이미 승인된 도구
        if tool_name in self._approved_tools:
            return True, f"이전 승인 재사용: '{tool_name}'"

        # 사용자 확인 필요
        if self.auto_confirm:
            self._approved_tools.add(tool_name)
            return True, f"자동 확인 (테스트 모드)"

        return self._ask_user(tool_name, arguments, level)

    def _ask_user(self, tool_name: str, arguments: dict, level: int) -> tuple[bool, str]:
        """사용자에게 확인을 요청합니다."""
        print(f"\n{'=' * 50}")
        print(f"  [확인 필요] 위험 도구 실행 요청 (Level {level})")
        print(f"{'=' * 50}")
        print(f"  도구: {tool_name}")
        print(f"  인자: {json.dumps(arguments, ensure_ascii=False, indent=4)}")
        print(f"{'=' * 50}")

        try:
            response = input("  실행하시겠습니까? (y=승인/n=거부/a=항상 승인): ").strip().lower()

            if response in ("y", "yes"):
                return True, "사용자 승인"
            elif response in ("a", "always"):
                self._approved_tools.add(tool_name)
                return True, f"항상 승인 등록: '{tool_name}'"
            else:
                return False, "사용자 거부"
        except (EOFError, KeyboardInterrupt):
            return False, "입력 중단"


# ╔══════════════════════════════════════════════════════════════╗
# ║  Context Engineering (컨텍스트 엔지니어링)                   ║
# ║  - 동적 시스템 프롬프트 구성                                 ║
# ║  - 도구 결과 요약                                          ║
# ║  - 컨텍스트 압축 (메시지가 너무 길어질 때)                   ║
# ╚══════════════════════════════════════════════════════════════╝

class ContextManager:
    """
    컨텍스트 엔지니어링 관리자.

    LLM에 전달되는 컨텍스트를 최적으로 관리합니다.
    Claude Code는 대화가 길어지면 자동으로 컨텍스트를 압축하며,
    시스템 프롬프트도 상황에 따라 동적으로 구성합니다.
    """

    def __init__(self, max_context_tokens: int = 100000):
        self.max_context_tokens = max_context_tokens
        self._messages: list[dict] = []

    # --- 동적 시스템 프롬프트 ---
    def build_system_prompt(
        self,
        role: str,
        tools: list[dict],
        safety_rules: list[str],
        project_context: str = "",
    ) -> str:
        """
        상황에 맞는 시스템 프롬프트를 동적으로 구성합니다.

        Claude Code의 시스템 프롬프트는 정적이 아닙니다.
        사용 가능한 도구, 프로젝트 컨텍스트(CLAUDE.md),
        현재 작업 디렉토리 등에 따라 동적으로 구성됩니다.

        Args:
            role: Agent의 역할
            tools: 사용 가능한 도구 목록 (schema)
            safety_rules: 안전 규칙
            project_context: 프로젝트별 컨텍스트 (CLAUDE.md 내용 등)

        Returns:
            완성된 시스템 프롬프트
        """
        sections = [f"## 역할\n{role}"]

        # 도구 목록 자동 생성
        if tools:
            tool_desc = []
            for t in tools:
                func = t.get("function", {})
                name = func.get("name", "")
                desc = func.get("description", "")
                tool_desc.append(f"- {name}: {desc}")
            sections.append("## 사용 가능한 도구\n" + "\n".join(tool_desc))

        # 안전 규칙
        if safety_rules:
            rules = "\n".join(f"{i+1}. {r}" for i, r in enumerate(safety_rules))
            sections.append(f"## 안전 규칙\n{rules}")

        # 프로젝트 컨텍스트 (CLAUDE.md / AGENTS.md 내용)
        if project_context:
            sections.append(f"## 프로젝트 컨텍스트\n{project_context}")

        sections.append("## 기본 지침\n- 항상 한국어로 응답하세요.\n- 정확하고 유용한 응답을 제공하세요.")

        return "\n\n".join(sections)

    # --- 도구 결과 요약 ---
    @staticmethod
    def summarize_tool_result(tool_name: str, result: str, max_length: int = 2000) -> str:
        """
        도구 실행 결과를 요약합니다.

        도구가 매우 긴 결과를 반환할 때 (예: 파일 내용 전체),
        컨텍스트 윈도우를 아끼기 위해 결과를 요약합니다.

        Claude Code도 파일이 너무 길면 관련 부분만 발췌합니다.

        Args:
            tool_name: 도구 이름
            result: 원본 결과
            max_length: 최대 문자 수

        Returns:
            요약된 결과
        """
        if len(result) <= max_length:
            return result

        # 앞부분과 뒷부분을 남기고 중간을 생략
        half = max_length // 2
        truncated = (
            result[:half]
            + f"\n\n... ({len(result) - max_length}자 생략) ...\n\n"
            + result[-half:]
        )

        return truncated

    # --- 컨텍스트 압축 ---
    def compact_messages(self, messages: list[dict]) -> list[dict]:
        """
        대화 메시지를 압축합니다.

        대화가 길어지면 컨텍스트 윈도우를 초과할 수 있습니다.
        이때 오래된 메시지를 요약하여 컨텍스트를 줄입니다.

        압축 전략:
        1. 시스템 프롬프트는 유지
        2. 최근 N개 메시지는 그대로 유지
        3. 오래된 메시지는 요약으로 대체
        4. 도구 결과는 핵심만 남기고 압축

        Args:
            messages: 전체 메시지 리스트

        Returns:
            압축된 메시지 리스트
        """
        if not messages:
            return messages

        # 대략적인 토큰 수 추정 (한국어 기준: 1글자 ≈ 1~2 토큰)
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        estimated_tokens = total_chars  # 한국어는 글자 수 ≈ 토큰 수

        if estimated_tokens <= self.max_context_tokens:
            return messages  # 압축 불필요

        print(f"    [컨텍스트 압축] 추정 토큰: {estimated_tokens} > 한도: {self.max_context_tokens}")

        compacted = []
        keep_recent = 10  # 최근 10개 메시지는 유지

        # 시스템 프롬프트 유지
        if messages and messages[0].get("role") == "system":
            compacted.append(messages[0])
            messages = messages[1:]

        # 오래된 메시지 요약
        if len(messages) > keep_recent:
            old_messages = messages[:-keep_recent]
            recent_messages = messages[-keep_recent:]

            # 오래된 대화 요약
            summary_parts = []
            for m in old_messages:
                role = m.get("role", "?")
                content = str(m.get("content", ""))[:100]
                if role == "user":
                    summary_parts.append(f"- 사용자: {content}")
                elif role == "assistant":
                    summary_parts.append(f"- 어시스턴트: {content}")

            summary = "## 이전 대화 요약\n" + "\n".join(summary_parts[-5:])
            compacted.append({"role": "user", "content": summary})
            compacted.extend(recent_messages)
        else:
            compacted.extend(messages)

        new_chars = sum(len(str(m.get("content", ""))) for m in compacted)
        print(f"    [컨텍스트 압축] {total_chars}자 -> {new_chars}자 (절감: {total_chars - new_chars}자)")

        return compacted


# ╔══════════════════════════════════════════════════════════════╗
# ║  Configuration Files (설정 파일 패턴)                       ║
# ║  - CLAUDE.md: Claude Code 프로젝트 설정                    ║
# ║  - AGENTS.md: Claude Code 서브 에이전트 설정               ║
# ║  - .cursor/rules: Cursor 프로젝트 규칙                     ║
# ╚══════════════════════════════════════════════════════════════╝

# --- CLAUDE.md 패턴 ---
# Claude Code는 프로젝트 루트의 CLAUDE.md를 자동으로 읽어
# 시스템 프롬프트에 포함시킵니다.
# 프로젝트별 규칙, 코딩 스타일, 금지 사항 등을 정의합니다.

CLAUDE_MD_EXAMPLE = """
# CLAUDE.md 예시

## 프로젝트 개요
이 프로젝트는 Python 기반의 AI Agent 프레임워크입니다.

## 코딩 규칙
- 모든 주석은 한국어로 작성
- Type hints 필수
- docstring은 Google 스타일
- 테스트 커버리지 80% 이상 유지

## 금지 사항
- eval(), exec() 사용 금지
- 하드코딩된 비밀키 금지
- print 디버깅 금지 (logging 사용)

## 파일 구조
```
project/
├── src/          # 소스 코드
├── tests/        # 테스트
├── docs/         # 문서
└── CLAUDE.md     # 이 파일
```

## 자주 사용하는 명령어
- 테스트: pytest tests/ -v
- 린트: ruff check src/
- 포매팅: ruff format src/
""".strip()

# --- AGENTS.md 패턴 ---
# 서브 에이전트가 있는 디렉토리에 AGENTS.md를 배치하면
# 해당 서브 에이전트의 행동을 별도로 제어할 수 있습니다.

AGENTS_MD_EXAMPLE = """
# AGENTS.md 예시 (서브 디렉토리별 설정)

## 이 디렉토리의 역할
데이터 전처리 파이프라인을 관리합니다.

## 규칙
- 원본 데이터를 절대 수정하지 마세요
- 출력은 항상 output/ 디렉토리에 저장
- CSV 파일은 UTF-8 인코딩 사용
""".strip()

# --- .cursor/rules 패턴 ---
# Cursor는 .cursor/rules 파일로 프로젝트 규칙을 정의합니다.
# 목적은 CLAUDE.md와 유사하지만 형식이 다릅니다.

CURSOR_RULES_EXAMPLE = """
# .cursor/rules 예시 (또는 .cursorrules)

You are a Python expert.
Always use type hints.
Write docstrings in Korean.
Prefer composition over inheritance.
Use dataclasses for data structures.
Never use global variables.
""".strip()


# ╔══════════════════════════════════════════════════════════════╗
# ║  Full Working Example: SafeHarnessAgent                    ║
# ║  5개 기둥을 모두 통합한 프로덕션 수준 Agent                  ║
# ╚══════════════════════════════════════════════════════════════╝

class SafeHarnessAgent:
    """
    5개 기둥을 모두 갖춘 안전한 하네스 Agent.

    이 클래스는 다음을 통합합니다:
    1. ToolRegistry      → 도구 관리 및 스키마 자동 생성
    2. GuardrailSystem   → 5단계 방어
    3. ErrorRecovery     → 재시도, 루프 감지, 롤백
    4. ObservabilitySystem → 로깅, 토큰 추적
    5. HumanGate         → 위험 작업 승인

    + ContextManager     → 컨텍스트 엔지니어링

    아키텍처 참고:
    - Claude Code처럼 단일 스레드 마스터 루프 방식
    - 매 반복마다 LLM 호출 → 도구 실행 → 결과 반환 사이클
    - 최대 반복 제한(max_iterations)으로 무한 루프 방지
    """

    def __init__(
        self,
        registry: ToolRegistry,
        system_prompt: str = "",
        guardrail_config: GuardrailConfig | None = None,
        max_retries: int = 3,
        auto_confirm: bool = False,
        log_file: str = "/tmp/harness_agent.jsonl",
    ):
        # Pillar 1: 도구 오케스트레이션
        self.registry = registry

        # Pillar 2: 가드레일
        self.guardrails = GuardrailSystem(guardrail_config)

        # Pillar 3: 에러 복구
        self.error_recovery = ErrorRecovery(max_retries=max_retries)

        # Pillar 4: 관측 가능성
        self.observability = ObservabilitySystem(log_file=log_file)

        # Pillar 5: 사람 개입
        self.human_gate = HumanGate(auto_confirm=auto_confirm)

        # 컨텍스트 관리
        self.context_manager = ContextManager()
        self.system_prompt = system_prompt

        # 설정
        self.config = guardrail_config or GuardrailConfig()

    def execute_tool_safely(self, tool_name: str, arguments: dict) -> str:
        """
        모든 안전장치를 거쳐 도구를 실행합니다.

        실행 순서:
        1. 가드레일 확인 (5단계)
        2. 사람 개입 게이트
        3. 루프 감지
        4. 도구 실행 (재시도 포함)
        5. 결과 로깅
        6. 결과 요약 (필요시)
        """
        # 1. 가드레일 확인
        ok, msg = self.guardrails.check_all(tool_name, arguments)
        if not ok:
            self.observability.log_guardrail_block(tool_name, msg)
            return f"가드레일 차단: {msg}"

        # 2. 사람 개입 게이트
        ok, msg = self.human_gate.check(tool_name, arguments)
        if not ok:
            self.observability.log_event("human_gate_block", {
                "tool": tool_name, "reason": msg,
            })
            return f"사용자 거부: {msg}"

        # 3. 루프 감지
        if self.error_recovery.detect_loop(tool_name, arguments):
            self.observability.log_event("loop_detected", {"tool": tool_name})
            return f"루프 감지: '{tool_name}'이(가) 반복적으로 호출되고 있습니다. 다른 접근법을 시도하세요."

        # 4. 도구 실행 (에러 복구 포함)
        start_time = time.time()
        try:
            result = self.error_recovery.retry_with_backoff(
                self.registry.execute, tool_name, arguments
            )
        except Exception as e:
            elapsed = time.time() - start_time
            self.observability.log_event("tool_error", {
                "tool": tool_name, "error": str(e), "elapsed": round(elapsed, 3),
            })
            return f"도구 실행 실패: {e}"

        elapsed = time.time() - start_time

        # 5. 결과 로깅
        self.observability.log_tool_call(tool_name, arguments, result, elapsed)

        # 6. 결과 요약 (너무 길면 압축)
        result = self.context_manager.summarize_tool_result(tool_name, result)

        # post-hook 실행
        result = self.guardrails.run_post_hooks(tool_name, arguments, result)

        return result

    def run(self, user_message: str) -> str:
        """
        Agent 마스터 루프를 실행합니다.

        Claude Code의 메인 루프와 동일한 구조:
        1. 사용자 입력 수신
        2. LLM 호출 (시스템 프롬프트 + 대화 히스토리 + 도구 정의)
        3. LLM이 도구 호출 요청 → 안전하게 실행 → 결과 피드백
        4. LLM이 최종 응답 → 반환
        5. 최대 반복 횟수 초과 시 강제 종료

        Args:
            user_message: 사용자 입력

        Returns:
            Agent의 최종 응답
        """
        import requests

        # 메시지 초기화
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": user_message})

        self.observability.log_event("session_start", {"user_message": user_message})

        # 마스터 루프 (최대 반복 제한 적용)
        for iteration in range(1, self.config.max_iterations + 1):
            # LLM 호출
            url = f"{GATEWAY_BASE_URL}/chat/completions"
            payload = {
                "model": DEFAULT_MODEL,
                "messages": messages,
                "tools": self.registry.get_schemas(),
            }

            try:
                response = requests.post(
                    url,
                    headers=get_headers(),
                    json=payload,
                    proxies=PROXIES,
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                self.observability.log_event("llm_error", {"error": str(e)})
                return f"LLM 호출 오류: {e}"

            assistant_msg = data["choices"][0]["message"]

            # 토큰 사용량 기록
            usage = data.get("usage", {})
            self.observability.log_llm_call(
                DEFAULT_MODEL,
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0),
            )

            tool_calls = assistant_msg.get("tool_calls")

            # 도구 호출이 없으면 최종 응답
            if not tool_calls:
                content = assistant_msg.get("content", "")
                messages.append({"role": "assistant", "content": content})
                self.observability.log_event("session_end", {
                    "iterations": iteration,
                    "stats": self.observability.get_session_stats(),
                })
                return content

            # 도구 호출 처리
            messages.append(assistant_msg)
            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                arguments = json.loads(tc["function"]["arguments"])
                tool_call_id = tc["id"]

                print(f"  [{iteration}] {tool_name}({json.dumps(arguments, ensure_ascii=False)[:80]})")

                # 안전하게 도구 실행 (모든 기둥 적용)
                result = self.execute_tool_safely(tool_name, arguments)

                preview = result[:150].replace("\n", " ")
                print(f"       -> {preview}{'...' if len(result) > 150 else ''}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result,
                })

            # 컨텍스트 압축 (메시지가 너무 길어지면)
            messages = self.context_manager.compact_messages(messages)

        # 최대 반복 초과
        self.observability.log_event("max_iterations_exceeded", {
            "iterations": self.config.max_iterations,
        })
        return f"최대 반복 횟수({self.config.max_iterations})를 초과했습니다."


# ============================================================
# 사용 예시: 5개 기둥이 모두 작동하는 데모
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Harness Engineering - 5 Pillars 통합 데모")
    print("=" * 60)

    # ─── Pillar 1: 도구 등록 ───
    print("\n[Pillar 1] Tool Orchestration")
    print("─" * 40)

    registry = ToolRegistry()

    @registry.tool(description="수학 표현식을 계산합니다")
    def calculator(expression: str) -> str:
        """수학 표현식을 안전하게 계산합니다."""
        import math
        allowed = {"abs": abs, "round": round, "sqrt": math.sqrt, "pi": math.pi}
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"{expression} = {result}"

    @registry.tool(description="파일을 읽습니다")
    def read_file(path: str) -> str:
        """파일 내용을 읽어 반환합니다."""
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(5000)

    @registry.tool(description="디렉토리 내용을 나열합니다")
    def list_directory(directory: str) -> str:
        """디렉토리 내 파일 목록을 반환합니다."""
        entries = os.listdir(directory)
        return "\n".join(sorted(entries))

    print(f"  등록된 도구: {registry.list_tools()}")
    print(f"  자동 생성된 스키마 수: {len(registry.get_schemas())}")

    # ─── Pillar 2: 가드레일 ───
    print("\n[Pillar 2] Guardrails (5단계 방어)")
    print("─" * 40)

    guardrails = GuardrailSystem(GuardrailConfig(
        max_tool_calls=50,
        blocked_commands=["rm -rf", "shutdown"],
        allowed_paths=[os.path.expanduser("~"), "/tmp"],
    ))

    # 커스텀 Pre-hook 등록 (Layer 5)
    def log_hook(tool_name: str, arguments: dict) -> tuple[bool, str]:
        """모든 도구 호출을 콘솔에 출력하는 훅"""
        print(f"    [Hook] {tool_name} 호출 감지")
        return True, "OK"

    guardrails.add_pre_hook(log_hook)

    # 가드레일 테스트
    ok, msg = guardrails.check_all("read_file", {"path": "/tmp/test.txt"})
    print(f"  안전한 호출: {ok} - {msg}")

    ok, msg = guardrails.check_all("run_command", {"command": "rm -rf /"})
    print(f"  위험한 호출: {ok} - {msg}")

    # ─── Pillar 3: 에러 복구 ───
    print("\n[Pillar 3] Error Recovery")
    print("─" * 40)

    recovery = ErrorRecovery(max_retries=3, max_loop_count=3)

    # 루프 감지 테스트
    print("  루프 감지 테스트:")
    for i in range(5):
        is_loop = recovery.detect_loop("read_file", {"path": "/tmp/same_file.txt"})
        print(f"    호출 {i+1}: 루프 감지 = {is_loop}")

    # 롤백 테스트
    print("\n  롤백 테스트:")
    recovery.push_rollback(lambda: print("    -> 롤백 1 실행"))
    recovery.push_rollback(lambda: print("    -> 롤백 2 실행"))
    recovery.rollback_all()

    # ─── Pillar 4: 관측 가능성 ───
    print("\n[Pillar 4] Observability")
    print("─" * 40)

    obs = ObservabilitySystem(log_file="/tmp/harness_demo.jsonl")
    obs.log_tool_call("calculator", {"expression": "1+1"}, "1+1 = 2", 0.01)
    obs.log_llm_call(DEFAULT_MODEL, 500, 200)

    stats = obs.get_session_stats()
    print(f"  세션 통계: {json.dumps(stats, ensure_ascii=False, indent=4)}")

    # ─── Pillar 5: 사람 개입 ───
    print("\n[Pillar 5] Human-in-the-Loop")
    print("─" * 40)

    gate = HumanGate(auto_approve_level=1, auto_confirm=True)

    ok, msg = gate.check("read_file", {"path": "/tmp/test.txt"})
    print(f"  read_file (Level 0): {ok} - {msg}")

    ok, msg = gate.check("run_command", {"command": "ls"})
    print(f"  run_command (Level 3): {ok} - {msg}")

    ok, msg = gate.check("format_disk", {})
    print(f"  format_disk (Level 4): {ok} - {msg}")

    # ─── Context Engineering ───
    print("\n[Context Engineering]")
    print("─" * 40)

    ctx = ContextManager()

    # 동적 시스템 프롬프트 생성
    prompt = ctx.build_system_prompt(
        role="코딩 어시스턴트",
        tools=registry.get_schemas(),
        safety_rules=["시스템 파일 수정 금지", "비밀 정보 노출 금지"],
        project_context="Python 3.11, FastAPI 기반 프로젝트",
    )
    print(f"  시스템 프롬프트 길이: {len(prompt)}자")
    print(f"  시스템 프롬프트 미리보기:\n{prompt[:300]}...")

    # 도구 결과 요약
    long_result = "A" * 5000
    summarized = ctx.summarize_tool_result("read_file", long_result, max_length=200)
    print(f"\n  결과 요약: {len(long_result)}자 -> {len(summarized)}자")

    # ─── 설정 파일 패턴 ───
    print("\n[Configuration Files]")
    print("─" * 40)
    print(f"  CLAUDE.md 예시 (처음 300자):\n{CLAUDE_MD_EXAMPLE[:300]}...")
    print(f"\n  AGENTS.md 예시 (처음 200자):\n{AGENTS_MD_EXAMPLE[:200]}...")
    print(f"\n  .cursor/rules 예시:\n{CURSOR_RULES_EXAMPLE[:200]}...")

    # ─── 통합 Agent 생성 (실행은 API 연결 필요) ───
    print("\n\n[통합 Agent 생성]")
    print("─" * 40)

    agent = SafeHarnessAgent(
        registry=registry,
        system_prompt=ctx.build_system_prompt(
            role="안전한 코딩 어시스턴트",
            tools=registry.get_schemas(),
            safety_rules=["시스템 파일 수정 금지", "위험 명령어 실행 금지"],
        ),
        guardrail_config=GuardrailConfig(max_iterations=10, max_tool_calls=50),
        auto_confirm=True,
        log_file="/tmp/harness_full_demo.jsonl",
    )

    print(f"  등록된 도구: {registry.list_tools()}")
    print(f"  최대 반복: {agent.config.max_iterations}")
    print(f"  최대 도구 호출: {agent.config.max_tool_calls}")
    print(f"  로그 파일: /tmp/harness_full_demo.jsonl")

    # 통합 도구 실행 테스트 (LLM 없이 직접 호출)
    print("\n  [통합 도구 실행 테스트]")
    result = agent.execute_tool_safely("calculator", {"expression": "2 ** 10"})
    print(f"  calculator('2 ** 10') = {result}")

    result = agent.execute_tool_safely("list_directory", {"directory": "/tmp"})
    print(f"  list_directory('/tmp') = {result[:100]}...")

    # 최종 통계
    final_stats = agent.observability.get_session_stats()
    print(f"\n  [최종 세션 통계]")
    print(f"  {json.dumps(final_stats, ensure_ascii=False, indent=4)}")

    print("\n" + "=" * 60)
    print("  데모 완료")
    print("  ")
    print("  핵심 정리:")
    print("  모델 = 엔진,  하네스 = 자동차")
    print("  좋은 엔진(LLM)이 있어도 좋은 자동차(하네스) 없이는")
    print("  프로덕션 Agent를 만들 수 없습니다.")
    print("=" * 60)

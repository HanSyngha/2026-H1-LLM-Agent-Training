"""
아키텍처 실습 정답: ToolRegistry + 안전장치 적용 Agent

tool_registry.py의 ToolRegistry와 safe_agent.py의 안전장치 패턴을
결합하여 프로덕션 수준의 Agent를 구현합니다.

실행 방법:
    python exercise_solution.py

의존성:
    pip install requests
"""

import json
import os
import sys
import math
from datetime import datetime

# 공통 설정 로드
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

# 같은 디렉토리의 모듈을 가져옵니다
sys.path.insert(0, os.path.dirname(__file__))
from tool_registry import ToolRegistry
from safe_agent import SafeAgent, SafetyPolicy


# ============================================================
# 1. ToolRegistry를 사용하여 도구를 등록합니다
# ============================================================

registry = ToolRegistry()


@registry.tool(description="수학 표현식을 계산합니다")
def calculator(expression: str) -> str:
    """수학 표현식을 계산합니다.

    사칙연산, 제곱근, 절대값 등을 지원합니다.

    Args:
        expression: 계산할 수학 표현식 (예: "3+5", "sqrt(16)", "abs(-10)")
    """
    allowed = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
        "pow": pow, "int": int, "float": float,
        "sin": math.sin, "cos": math.cos, "log": math.log,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"{expression} = {result}"
    except Exception as e:
        return f"계산 오류: {e}"


@registry.tool(description="파일 내용을 읽어 반환합니다")
def read_file(file_path: str) -> str:
    """파일의 내용을 읽어 반환합니다.

    텍스트 파일만 읽을 수 있으며, 500KB 이하 파일만 지원합니다.

    Args:
        file_path: 읽을 파일의 경로
    """
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        return f"파일 없음: {abs_path}"
    if not os.path.isfile(abs_path):
        return f"파일이 아닙니다: {abs_path}"

    file_size = os.path.getsize(abs_path)
    if file_size > 500_000:
        return f"파일이 너무 큽니다: {file_size:,} bytes (최대 500KB)"

    try:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(5000)
        return f"=== {abs_path} ({file_size:,} bytes) ===\n{content}"
    except Exception as e:
        return f"파일 읽기 오류: {e}"


@registry.tool(description="디렉토리의 파일/폴더 목록을 조회합니다")
def list_directory(path: str) -> str:
    """디렉토리의 파일 및 폴더 목록을 반환합니다.

    Args:
        path: 조회할 디렉토리 경로
    """
    abs_path = os.path.abspath(path)
    if not os.path.isdir(abs_path):
        return f"디렉토리가 아닙니다: {abs_path}"

    entries = []
    try:
        items = sorted(os.listdir(abs_path))
    except PermissionError:
        return f"읽기 권한이 없습니다: {abs_path}"

    for item in items:
        full = os.path.join(abs_path, item)
        try:
            if os.path.isdir(full):
                entries.append(f"  [DIR]  {item}/")
            else:
                size = os.path.getsize(full)
                entries.append(f"  [FILE] {item} ({size:,} bytes)")
        except OSError:
            entries.append(f"  [????] {item}")

    result = f"디렉토리: {abs_path}\n항목: {len(entries)}개\n"
    result += "\n".join(entries) if entries else "  (비어있음)"
    return result


@registry.tool(description="현재 날짜와 시간을 반환합니다")
def get_current_time() -> str:
    """현재 날짜와 시간을 반환합니다."""
    now = datetime.now()
    return f"현재: {now.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}"


# ============================================================
# 2. 등록된 도구 정보를 확인합니다
# ============================================================

def show_registry_info():
    """ToolRegistry에 등록된 도구 정보를 출력합니다."""
    print("=" * 60)
    print("  등록된 도구 정보 (ToolRegistry)")
    print("=" * 60)

    # 도구 요약을 출력합니다
    print(registry.describe())

    # 자동 생성된 스키마를 확인합니다
    print(f"\n[자동 생성된 Tool Schema]")
    schemas = registry.get_tool_schemas()
    for schema in schemas:
        func = schema["function"]
        params = func["parameters"].get("required", [])
        print(f"  - {func['name']}({', '.join(params)}): {func['description'][:60]}")


# ============================================================
# 3. SafeAgent 설정 및 생성
# ============================================================

def create_safe_agent() -> SafeAgent:
    """안전장치가 적용된 Agent를 생성합니다."""

    # 안전 정책을 설정합니다
    policy = SafetyPolicy(
        # 허용 경로: 프로젝트 디렉토리와 홈 디렉토리만 허용합니다
        allowed_paths=[
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")),
            os.path.expanduser("~"),
        ],
        # 차단 명령어
        blocked_commands=["rm -rf", "format", "del /s", "shutdown"],
        # 위험 도구 (실행 전 확인 필요)
        dangerous_tools=["run_command", "write_file"],
        # 최대 반복 횟수
        max_iterations=15,
        # 속도 제한 (초당 도구 호출 수)
        rate_limit_per_second=3.0,
        # 최대 도구 호출 횟수
        max_total_tool_calls=50,
    )

    # Agent를 생성합니다
    agent = SafeAgent(
        tool_schemas=registry.get_tool_schemas(),
        tool_functions=registry.get_tool_functions(),
        policy=policy,
        system_prompt=(
            "당신은 프로덕션 환경에서 안전하게 운영되는 AI 어시스턴트입니다. "
            "사용 가능한 도구를 활용하여 사용자의 질문에 정확하게 답변하세요. "
            "계산이 필요하면 calculator, 파일 읽기는 read_file, "
            "디렉토리 조회는 list_directory, 시간 확인은 get_current_time을 사용하세요. "
            "한국어로 응답하세요."
        ),
        log_file=os.path.join(os.path.dirname(__file__), "exercise_agent_log.jsonl"),
        auto_confirm=True,  # 데모에서는 자동 승인합니다
    )

    return agent


# ============================================================
# 4. 대화형 인터페이스
# ============================================================

def interactive_mode():
    """대화형 모드를 실행합니다."""
    show_registry_info()

    agent = create_safe_agent()

    print(f"\n{'=' * 60}")
    print("  안전한 Agent 대화 시작")
    print(f"{'=' * 60}")
    print("사용 가능한 도구: calculator, read_file, list_directory, get_current_time")
    print("'종료'로 끝내기, '통계'로 세션 통계 확인\n")

    messages = None  # Agent가 내부적으로 관리합니다

    while True:
        try:
            user_input = input("사용자: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break

        if not user_input:
            continue
        if user_input.lower() in ["종료", "quit", "exit"]:
            break
        if user_input.lower() in ["통계", "stats"]:
            stats = agent.get_stats()
            print(f"[통계] {json.dumps(stats, ensure_ascii=False)}")
            continue

        try:
            response = agent.run(user_input)
            print(f"\nAI: {response}\n")
        except Exception as e:
            print(f"\n[오류] {e}\n")

    # 최종 통계를 출력합니다
    print(f"\n[최종 통계] {json.dumps(agent.get_stats(), ensure_ascii=False)}")


def demo_mode():
    """데모 모드: 미리 정의된 질문으로 Agent를 테스트합니다."""
    show_registry_info()

    agent = create_safe_agent()

    print(f"\n{'=' * 60}")
    print("  안전한 Agent 데모")
    print(f"{'=' * 60}")

    # 데모 질문들입니다
    queries = [
        "sqrt(144) + 3 * 5 를 계산해줘",
        "현재 시간 알려줘",
        f"이 프로젝트의 디렉토리 목록을 보여줘: {os.path.dirname(__file__)}",
    ]

    for query in queries:
        print(f"\n{'─' * 60}")
        print(f"사용자: {query}")
        response = agent.run(query)
        print(f"\nAI: {response}")

    # 세션 통계를 출력합니다
    print(f"\n{'=' * 60}")
    print(f"[세션 통계] {json.dumps(agent.get_stats(), ensure_ascii=False)}")
    print(f"{'=' * 60}")


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo_mode()
    else:
        interactive_mode()

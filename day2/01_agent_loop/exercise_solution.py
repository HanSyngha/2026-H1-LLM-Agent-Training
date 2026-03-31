"""
Agent Loop 실습 정답: requests만으로 2개 tool agent + multi-turn 대화

프레임워크 없이 requests 라이브러리만 사용하여 완전한 Agent Loop를 구현합니다.
2개 이상의 도구와 multi-turn 대화를 지원합니다.

실행 방법:
    python exercise_solution.py

의존성:
    pip install requests
"""

import json
import os
import sys
import requests
from datetime import datetime

# 공통 설정 로드
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 1. 도구(Tool) 구현 - 2개 이상 정의합니다
# ============================================================

def calculator(expression: str) -> str:
    """수학 표현식을 계산합니다.

    사칙연산, 거듭제곱, 나머지 연산 등을 지원합니다.

    Args:
        expression: 계산할 수학 표현식 (예: "3 + 5", "100 * 2.5")
    """
    import math
    # 허용할 함수와 상수를 정의합니다
    allowed = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
        "pow": pow, "int": int, "float": float,
    }
    try:
        # eval을 제한된 환경에서 실행합니다
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"{expression} = {result}"
    except Exception as e:
        return f"계산 오류: {e}"


def get_weather(city: str) -> str:
    """도시의 날씨 정보를 조회합니다. (시뮬레이션)

    Args:
        city: 날씨를 조회할 도시 이름
    """
    weather_data = {
        "서울": {"temp": 18, "condition": "맑음", "humidity": 45, "wind": "3m/s"},
        "부산": {"temp": 21, "condition": "구름 많음", "humidity": 65, "wind": "5m/s"},
        "제주": {"temp": 22, "condition": "흐림", "humidity": 70, "wind": "7m/s"},
        "대전": {"temp": 17, "condition": "맑음", "humidity": 40, "wind": "2m/s"},
        "인천": {"temp": 16, "condition": "안개", "humidity": 80, "wind": "4m/s"},
    }
    if city in weather_data:
        w = weather_data[city]
        return f"{city} 날씨: {w['condition']}, 기온 {w['temp']}°C, 습도 {w['humidity']}%, 바람 {w['wind']}"
    return f"{city}의 날씨 정보를 찾을 수 없습니다. 조회 가능 도시: {list(weather_data.keys())}"


def get_current_time() -> str:
    """현재 날짜와 시간을 반환합니다."""
    now = datetime.now()
    return f"현재: {now.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')} ({now.strftime('%A')})"


# ============================================================
# 2. OpenAI Tool Schema 정의
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "수학 표현식을 계산합니다. 사칙연산, 거듭제곱, 제곱근 등을 지원합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "계산할 수학 표현식 (예: '3+5', '100*2.5', 'sqrt(16)')",
                    },
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "도시의 현재 날씨 정보를 조회합니다. 서울, 부산, 제주, 대전, 인천을 지원합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "날씨를 조회할 도시 이름 (예: 서울, 부산)",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "현재 날짜와 시간을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# 도구 디스패치 테이블
TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_weather": get_weather,
    "get_current_time": get_current_time,
}


# ============================================================
# 3. LLM API 호출 함수
# ============================================================

def call_llm(messages: list[dict], tools: list[dict] | None = None) -> dict:
    """OpenAI 호환 API에 직접 HTTP POST 요청을 보냅니다."""
    url = f"{GATEWAY_BASE_URL}/chat/completions"
    headers = get_headers()

    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
    }
    if tools:
        payload["tools"] = tools

    response = requests.post(
        url, headers=headers, json=payload,
        proxies=PROXIES, timeout=120, verify=SSL_VERIFY,
    )
    response.raise_for_status()
    return response.json()


# ============================================================
# 4. 도구 실행 함수
# ============================================================

def execute_tool(tool_name: str, arguments: dict) -> str:
    """도구를 실행하고 결과를 문자열로 반환합니다."""
    if tool_name not in TOOL_FUNCTIONS:
        return f"오류: 알 수 없는 도구 '{tool_name}'"
    try:
        func = TOOL_FUNCTIONS[tool_name]
        result = func(**arguments)
        return str(result)
    except Exception as e:
        return f"도구 실행 오류 ({tool_name}): {e}"


# ============================================================
# 5. Agent Loop 핵심 구현
# ============================================================

def agent_loop(messages: list[dict], max_iterations: int = 10) -> str:
    """Agent Loop를 실행합니다.

    도구 호출이 없을 때까지 LLM 호출 -> 도구 실행 -> 결과 전달을 반복합니다.

    Args:
        messages: 대화 히스토리
        max_iterations: 최대 반복 횟수 (무한 루프 방지)

    Returns:
        최종 응답 텍스트
    """
    for iteration in range(1, max_iterations + 1):
        # LLM을 호출합니다
        response_data = call_llm(messages, tools=TOOLS)
        assistant_message = response_data["choices"][0]["message"]
        tool_calls = assistant_message.get("tool_calls")

        # 도구 호출이 없으면 최종 응답을 반환합니다
        if not tool_calls:
            content = assistant_message.get("content", "")
            messages.append({"role": "assistant", "content": content})
            return content

        # 도구 호출이 있으면 실행하고 결과를 추가합니다
        print(f"  [루프 #{iteration}] 도구 호출 {len(tool_calls)}개 감지")
        messages.append(assistant_message)

        for tc in tool_calls:
            tool_name = tc["function"]["name"]
            arguments = json.loads(tc["function"]["arguments"])
            tool_call_id = tc["id"]

            print(f"    -> {tool_name}({arguments})")
            result = execute_tool(tool_name, arguments)
            print(f"    <- {result[:100]}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result,
            })

    return "오류: 최대 반복 횟수를 초과했습니다."


# ============================================================
# 6. Multi-turn 대화형 인터페이스
# ============================================================

def interactive_chat():
    """대화형 인터페이스를 실행합니다. multi-turn 대화를 지원합니다."""

    print("=" * 60)
    print("  Agent Loop 대화형 인터페이스")
    print("=" * 60)
    print("사용 가능한 도구:")
    print("  - calculator: 수학 계산")
    print("  - get_weather: 날씨 조회 (서울, 부산, 제주, 대전, 인천)")
    print("  - get_current_time: 현재 시간 조회")
    print("'종료' 또는 'quit'으로 대화를 종료합니다.")
    print("'초기화' 또는 'reset'으로 대화를 초기화합니다.")
    print("-" * 60)

    # 시스템 프롬프트를 포함한 대화 히스토리입니다
    messages = [
        {
            "role": "system",
            "content": (
                "당신은 도움이 되는 AI 어시스턴트입니다. "
                "사용 가능한 도구를 활용하여 사용자의 질문에 정확하게 답변하세요. "
                "계산이 필요하면 calculator, 날씨 정보가 필요하면 get_weather, "
                "현재 시간이 필요하면 get_current_time을 사용하세요. "
                "한국어로 답변하세요."
            ),
        },
    ]

    while True:
        try:
            user_input = input("\n사용자: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n대화를 종료합니다.")
            break

        if not user_input:
            continue

        if user_input.lower() in ["종료", "quit", "exit", "q"]:
            print("대화를 종료합니다.")
            break

        if user_input.lower() in ["초기화", "reset"]:
            messages = [messages[0]]  # 시스템 프롬프트만 유지합니다
            print("[대화가 초기화되었습니다]")
            continue

        # 사용자 메시지를 추가합니다
        messages.append({"role": "user", "content": user_input})

        # Agent Loop를 실행합니다
        try:
            response = agent_loop(messages)
            print(f"\nAI: {response}")
        except Exception as e:
            print(f"\n[오류] {e}")
            # 오류 발생 시 마지막 사용자 메시지를 제거합니다
            if messages[-1]["role"] == "user":
                messages.pop()


# ============================================================
# 7. 데모 모드
# ============================================================

def demo_mode():
    """미리 정의된 질문으로 Agent를 테스트합니다."""
    print("=" * 60)
    print("  Agent Loop 데모 모드")
    print("=" * 60)

    messages = [
        {
            "role": "system",
            "content": (
                "당신은 도움이 되는 AI 어시스턴트입니다. "
                "도구를 활용하여 정확하게 답변하세요. 한국어로 응답하세요."
            ),
        },
    ]

    # 테스트 질문들입니다 (multi-turn으로 진행)
    queries = [
        "123 * 456을 계산해줘",
        "서울이랑 부산 날씨 비교해줘",
        "방금 계산한 결과에 100을 더하면 얼마야?",
    ]

    for query in queries:
        print(f"\n{'─' * 60}")
        print(f"사용자: {query}")
        messages.append({"role": "user", "content": query})

        response = agent_loop(messages)
        print(f"\nAI: {response}")

    print(f"\n{'=' * 60}")
    print("  데모 완료!")
    print(f"{'=' * 60}")


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo_mode()
    else:
        interactive_chat()

"""
기본 Agent Loop 구현 - requests만 사용

이 파일은 OpenAI 호환 API를 직접 호출하여 Agent Loop를 구현합니다.
프레임워크 없이 requests 라이브러리만 사용합니다.

=== Agent Loop 핵심 원리 ===
Claude Code, Cursor, Google ADK 등 모든 AI Agent는 동일한 패턴을 사용합니다:

    사용자 메시지
        ↓
    LLM에 메시지 + 사용 가능한 도구 목록 전송
        ↓
    LLM 응답 확인:
        - tool_calls가 있으면 → 도구 실행 → 결과를 메시지에 추가 → 다시 LLM 호출
        - tool_calls가 없으면 → 최종 응답 (루프 종료)

이것이 Agent Loop의 전부입니다. 나머지는 모두 이 패턴의 변형일 뿐입니다.
"""

import sys
import os
import json
import requests

# 공통 설정 로드 (게이트웨이 URL, API 키 등)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 1단계: 도구(Tool) 정의
# ============================================================
# OpenAI API는 도구를 JSON Schema 형식으로 정의합니다.
# 각 도구는 name, description, parameters를 가집니다.

def add_numbers(a: float, b: float) -> float:
    """두 수를 더합니다."""
    return a + b


def get_weather(city: str) -> str:
    """도시의 날씨 정보를 반환합니다. (시뮬레이션)"""
    # 실제로는 날씨 API를 호출하겠지만, 여기서는 시뮬레이션합니다.
    weather_data = {
        "서울": "맑음, 22°C",
        "부산": "흐림, 19°C",
        "제주": "비, 18°C",
    }
    return weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다.")


def get_current_time() -> str:
    """현재 시각을 반환합니다."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# 2단계: 도구를 OpenAI Tool Schema로 변환
# ============================================================
# OpenAI API가 이해할 수 있는 JSON Schema 형식입니다.
# type은 항상 "function"이고, function 안에 name, description, parameters가 들어갑니다.

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "두 수를 더합니다. 덧셈 계산이 필요할 때 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "첫 번째 숫자",
                    },
                    "b": {
                        "type": "number",
                        "description": "두 번째 숫자",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "도시의 현재 날씨 정보를 조회합니다.",
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
            "description": "현재 시각을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# ============================================================
# 3단계: 도구 이름 -> 실제 함수 매핑 (디스패치 테이블)
# ============================================================
# LLM이 "add_numbers를 호출해줘"라고 하면, 실제 Python 함수를 찾아 실행해야 합니다.

TOOL_FUNCTIONS = {
    "add_numbers": add_numbers,
    "get_weather": get_weather,
    "get_current_time": get_current_time,
}


# ============================================================
# 4단계: LLM API 호출 함수
# ============================================================

def call_llm(messages: list[dict], tools: list[dict] | None = None) -> dict:
    """
    OpenAI 호환 API에 직접 HTTP POST 요청을 보냅니다.

    === API 요청 구조 ===
    POST /v1/chat/completions
    {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "...", "tool_calls": [...]},
            {"role": "tool", "tool_call_id": "...", "content": "..."},
        ],
        "tools": [... tool definitions ...],
    }

    === API 응답 구조 ===
    {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "최종 텍스트 응답" 또는 null,
                "tool_calls": [  # 도구 호출이 필요한 경우
                    {
                        "id": "call_abc123",
                        "type": "function",
                        "function": {
                            "name": "도구이름",
                            "arguments": '{"param": "value"}'  # JSON 문자열!
                        }
                    }
                ]
            },
            "finish_reason": "stop" 또는 "tool_calls"
        }]
    }
    """
    url = f"{GATEWAY_BASE_URL}/chat/completions"
    headers = get_headers()

    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
    }

    # 도구 목록이 있으면 payload에 추가
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
# 5단계: 도구 실행 함수
# ============================================================

def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    도구를 실행하고 결과를 문자열로 반환합니다.

    LLM은 항상 문자열 형태의 결과를 기대하므로,
    모든 반환값을 str로 변환합니다.
    """
    if tool_name not in TOOL_FUNCTIONS:
        return f"오류: 알 수 없는 도구 '{tool_name}'"

    func = TOOL_FUNCTIONS[tool_name]
    try:
        result = func(**arguments)
        return str(result)
    except Exception as e:
        return f"도구 실행 오류: {e}"


# ============================================================
# 6단계: Agent Loop - 핵심!
# ============================================================

def run_agent(user_message: str) -> str:
    """
    Agent Loop의 핵심 구현입니다.

    === 동작 흐름 ===
    1. 사용자 메시지를 messages 리스트에 추가
    2. LLM 호출 (messages + tools 전송)
    3. 응답에서 tool_calls 확인
       - tool_calls가 있으면:
         a. assistant 메시지(tool_calls 포함)를 messages에 추가
         b. 각 tool_call을 실행
         c. 실행 결과를 role="tool" 메시지로 messages에 추가
         d. 2번으로 돌아감 (다시 LLM 호출)
       - tool_calls가 없으면:
         → content를 최종 응답으로 반환 (루프 종료)

    이것이 Claude Code, Cursor 등 모든 AI Agent의 핵심 동작 원리입니다.
    """
    # 시스템 프롬프트: Agent의 역할과 행동 지침을 정의
    messages = [
        {
            "role": "system",
            "content": (
                "당신은 도움이 되는 AI 어시스턴트입니다. "
                "사용 가능한 도구를 활용하여 사용자의 질문에 정확하게 답변하세요. "
                "계산이 필요하면 add_numbers 도구를, "
                "날씨 정보가 필요하면 get_weather 도구를, "
                "현재 시간이 필요하면 get_current_time 도구를 사용하세요."
            ),
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]

    # 무한루프 방지를 위한 최대 반복 횟수
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Agent Loop 반복 #{iteration} ---")

        # LLM 호출
        response_data = call_llm(messages, tools=TOOLS)

        # 응답에서 assistant 메시지 추출
        assistant_message = response_data["choices"][0]["message"]
        finish_reason = response_data["choices"][0]["finish_reason"]

        print(f"  finish_reason: {finish_reason}")

        # tool_calls가 있는지 확인
        tool_calls = assistant_message.get("tool_calls")

        if not tool_calls:
            # ✅ 도구 호출 없음 → 최종 응답
            final_response = assistant_message.get("content", "")
            print(f"  최종 응답 도착! (루프 종료)")
            return final_response

        # 🔧 도구 호출이 있음 → 실행 후 계속
        print(f"  도구 호출 {len(tool_calls)}개 감지")

        # assistant 메시지를 히스토리에 추가 (tool_calls 정보 포함)
        messages.append(assistant_message)

        # 각 tool_call을 실행하고 결과를 messages에 추가
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            # arguments는 JSON 문자열이므로 파싱 필요!
            arguments = json.loads(tool_call["function"]["arguments"])
            tool_call_id = tool_call["id"]

            print(f"  도구 실행: {tool_name}({arguments})")

            # 도구 실행
            result = execute_tool(tool_name, arguments)
            print(f"  도구 결과: {result}")

            # 도구 실행 결과를 messages에 추가
            # role="tool"이고, tool_call_id로 어떤 호출에 대한 결과인지 매칭
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result,
            })

        # 루프의 다음 반복: LLM이 도구 결과를 보고 다시 판단

    return "오류: 최대 반복 횟수를 초과했습니다."


# ============================================================
# 실행 예시
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("기본 Agent Loop 데모")
    print("=" * 60)

    # 예시 1: 단순 계산 (도구 1회 호출)
    print("\n[예시 1] 단순 계산")
    result = run_agent("123과 456을 더하면 얼마인가요?")
    print(f"\n최종 응답: {result}")

    print("\n" + "=" * 60)

    # 예시 2: 여러 도구 호출이 필요한 질문
    print("\n[예시 2] 복합 질문")
    result = run_agent("지금 몇 시야? 그리고 서울 날씨는 어때?")
    print(f"\n최종 응답: {result}")

    print("\n" + "=" * 60)

    # 예시 3: 도구가 필요 없는 질문 (도구 호출 0회)
    print("\n[예시 3] 일반 질문")
    result = run_agent("파이썬에서 리스트와 튜플의 차이점을 알려줘")
    print(f"\n최종 응답: {result}")

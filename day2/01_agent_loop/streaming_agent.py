"""
스트리밍 Agent Loop - requests + SSE 파싱

스트리밍 vs 논스트리밍 차이:
- 논스트리밍: 전체 응답이 완성될 때까지 기다린 후 한꺼번에 수신
- 스트리밍: 토큰이 생성될 때마다 즉시 수신 (실시간 출력 가능)

=== SSE (Server-Sent Events) 형식 ===
OpenAI API의 스트리밍 응답은 SSE 형식을 사용합니다:

    data: {"id":"chatcmpl-xxx","choices":[{"delta":{"content":"안"},...}]}
    data: {"id":"chatcmpl-xxx","choices":[{"delta":{"content":"녕"},...}]}
    data: {"id":"chatcmpl-xxx","choices":[{"delta":{"content":"!"},...}]}
    data: [DONE]

각 줄은 "data: " 접두사로 시작하며, JSON 객체가 뒤따릅니다.
마지막 줄은 "data: [DONE]"으로 스트리밍 종료를 알립니다.

=== 스트리밍에서 tool_calls 처리 ===
tool_calls도 delta 형태로 조각(chunk)이 옵니다.
함수 이름과 인자가 여러 chunk에 걸쳐 전달되므로,
이를 누적(accumulate)하여 완성해야 합니다.
"""

import sys
import os
import json
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 도구 정의 (basic_agent.py와 동일)
# ============================================================

def add_numbers(a: float, b: float) -> float:
    """두 수를 더합니다."""
    return a + b


def get_weather(city: str) -> str:
    """도시의 날씨 정보를 반환합니다. (시뮬레이션)"""
    weather_data = {
        "서울": "맑음, 22°C, 습도 45%",
        "부산": "흐림, 19°C, 습도 65%",
        "제주": "비, 18°C, 습도 80%",
    }
    return weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다.")


def get_current_time() -> str:
    """현재 시각을 반환합니다."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "두 수를 더합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "첫 번째 숫자"},
                    "b": {"type": "number", "description": "두 번째 숫자"},
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
                    "city": {"type": "string", "description": "도시 이름"},
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

TOOL_FUNCTIONS = {
    "add_numbers": add_numbers,
    "get_weather": get_weather,
    "get_current_time": get_current_time,
}


# ============================================================
# SSE 파서
# ============================================================

def parse_sse_stream(response: requests.Response):
    """
    requests Response 객체에서 SSE 이벤트를 파싱하여 yield합니다.

    SSE 형식:
        data: {"json": "data"}\\n
        \\n
        data: {"json": "data2"}\\n
        \\n
        data: [DONE]\\n

    빈 줄로 이벤트가 구분되며, "data: " 접두사를 제거하고 JSON을 파싱합니다.
    """
    # iter_lines()로 한 줄씩 읽기 (스트리밍)
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            # 빈 줄은 이벤트 구분자 → 무시
            continue

        if line.startswith("data: "):
            data_str = line[6:]  # "data: " 제거

            if data_str.strip() == "[DONE]":
                # 스트리밍 종료 신호
                return

            try:
                data = json.loads(data_str)
                yield data
            except json.JSONDecodeError:
                # 파싱 실패한 줄은 건너뜀 (간혹 발생)
                continue


# ============================================================
# 스트리밍 LLM 호출
# ============================================================

def call_llm_streaming(messages: list[dict], tools: list[dict] | None = None):
    """
    스트리밍 모드로 LLM API를 호출합니다.

    stream=True로 요청하면 응답이 SSE 형식으로 조각(chunk)씩 전달됩니다.
    requests.post()에 stream=True를 전달하면 응답 본문을 즉시 다운로드하지 않고,
    iter_lines() / iter_content()로 점진적으로 읽을 수 있습니다.
    """
    url = f"{GATEWAY_BASE_URL}/chat/completions"
    headers = get_headers()

    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "stream": True,  # 스트리밍 활성화!
    }
    if tools:
        payload["tools"] = tools

    # stream=True: 응답을 즉시 다운로드하지 않음
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        proxies=PROXIES,
        timeout=120,
        stream=True,  # requests에게도 스트리밍 모드임을 알림
    )
    response.raise_for_status()
    return response


# ============================================================
# 스트리밍 응답 처리 - 텍스트 응답
# ============================================================

def process_streaming_text(response: requests.Response) -> str:
    """
    스트리밍 텍스트 응답을 처리합니다.
    토큰이 도착할 때마다 즉시 출력합니다.

    === 스트리밍 chunk 구조 ===
    {
        "choices": [{
            "delta": {
                "content": "토"   # 한 토큰씩 전달
            },
            "finish_reason": null
        }]
    }

    마지막 chunk:
    {
        "choices": [{
            "delta": {},
            "finish_reason": "stop"
        }]
    }
    """
    full_content = ""

    for chunk in parse_sse_stream(response):
        choices = chunk.get("choices", [])
        if not choices:
            continue

        delta = choices[0].get("delta", {})
        content_piece = delta.get("content", "")

        if content_piece:
            # 토큰이 도착할 때마다 즉시 출력 (줄바꿈 없이)
            print(content_piece, end="", flush=True)
            full_content += content_piece

    print()  # 마지막에 줄바꿈
    return full_content


# ============================================================
# 스트리밍 응답 처리 - tool_calls 누적
# ============================================================

def process_streaming_response(response: requests.Response) -> dict:
    """
    스트리밍 응답을 처리하고, 텍스트와 tool_calls를 모두 수집합니다.

    === tool_calls 스트리밍 구조 ===
    tool_calls는 delta에 조각(piece)으로 전달됩니다:

    첫 번째 chunk (tool_call 시작):
    {
        "delta": {
            "tool_calls": [{
                "index": 0,
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": ""
                }
            }]
        }
    }

    후속 chunk들 (arguments 조각):
    {
        "delta": {
            "tool_calls": [{
                "index": 0,
                "function": {
                    "arguments": "{\"ci"   # JSON 문자열의 일부
                }
            }]
        }
    }
    {
        "delta": {
            "tool_calls": [{
                "index": 0,
                "function": {
                    "arguments": "ty\": \"서울\"}"
                }
            }]
        }
    }

    → 이 조각들을 누적하여 최종 tool_call을 완성해야 합니다!
    """
    full_content = ""
    # tool_calls 누적 저장소: {index: {"id": ..., "function": {"name": ..., "arguments": ...}}}
    tool_calls_accumulator: dict[int, dict] = {}
    finish_reason = None

    for chunk in parse_sse_stream(response):
        choices = chunk.get("choices", [])
        if not choices:
            continue

        choice = choices[0]
        delta = choice.get("delta", {})
        finish_reason = choice.get("finish_reason") or finish_reason

        # 텍스트 content 처리
        content_piece = delta.get("content", "")
        if content_piece:
            print(content_piece, end="", flush=True)
            full_content += content_piece

        # tool_calls delta 처리
        tool_calls_delta = delta.get("tool_calls", [])
        for tc_delta in tool_calls_delta:
            index = tc_delta.get("index", 0)

            if index not in tool_calls_accumulator:
                # 새 tool_call 시작
                tool_calls_accumulator[index] = {
                    "id": tc_delta.get("id", ""),
                    "type": "function",
                    "function": {
                        "name": tc_delta.get("function", {}).get("name", ""),
                        "arguments": "",
                    },
                }

            # 기존 tool_call에 정보 누적
            tc_accum = tool_calls_accumulator[index]

            if tc_delta.get("id"):
                tc_accum["id"] = tc_delta["id"]

            func_delta = tc_delta.get("function", {})
            if func_delta.get("name"):
                tc_accum["function"]["name"] = func_delta["name"]
            if func_delta.get("arguments"):
                # arguments 문자열을 계속 이어붙임 (핵심!)
                tc_accum["function"]["arguments"] += func_delta["arguments"]

    if full_content:
        print()  # 줄바꿈

    # 누적된 tool_calls를 리스트로 변환
    tool_calls_list = None
    if tool_calls_accumulator:
        tool_calls_list = [
            tool_calls_accumulator[i]
            for i in sorted(tool_calls_accumulator.keys())
        ]

    # assistant 메시지 형태로 반환
    result = {
        "role": "assistant",
        "content": full_content if full_content else None,
    }
    if tool_calls_list:
        result["tool_calls"] = tool_calls_list

    return result


# ============================================================
# 도구 실행
# ============================================================

def execute_tool(tool_name: str, arguments: dict) -> str:
    """도구를 실행하고 결과를 문자열로 반환합니다."""
    if tool_name not in TOOL_FUNCTIONS:
        return f"오류: 알 수 없는 도구 '{tool_name}'"
    try:
        result = TOOL_FUNCTIONS[tool_name](**arguments)
        return str(result)
    except Exception as e:
        return f"도구 실행 오류: {e}"


# ============================================================
# 스트리밍 Agent Loop
# ============================================================

def run_streaming_agent(user_message: str) -> str:
    """
    스트리밍을 사용하는 Agent Loop입니다.

    논스트리밍 Agent Loop와 구조는 동일하지만,
    LLM 응답을 한꺼번에 받는 대신 토큰 단위로 실시간 수신합니다.

    === 논스트리밍 vs 스트리밍 비교 ===

    논스트리밍:
    1. LLM에 요청
    2. (수 초 대기)
    3. 전체 응답 수신
    4. 화면에 출력

    스트리밍:
    1. LLM에 요청
    2. 첫 토큰 수신 → 즉시 출력
    3. 두 번째 토큰 수신 → 즉시 출력
    4. ... (실시간으로 타이핑되는 것처럼 보임)
    5. 전체 응답 완성

    사용자 경험: 스트리밍이 훨씬 빠르게 느껴짐 (첫 토큰 시간, TTFT)
    """
    messages = [
        {
            "role": "system",
            "content": (
                "당신은 도움이 되는 AI 어시스턴트입니다. "
                "필요한 도구를 활용하여 정확하게 답변하세요."
            ),
        },
        {"role": "user", "content": user_message},
    ]

    max_iterations = 10

    for iteration in range(1, max_iterations + 1):
        print(f"\n--- Agent Loop 반복 #{iteration} (스트리밍) ---")

        # 스트리밍으로 LLM 호출
        response = call_llm_streaming(messages, tools=TOOLS)

        # 스트리밍 응답 처리 (텍스트 실시간 출력 + tool_calls 누적)
        print("  LLM 응답: ", end="")
        assistant_message = process_streaming_response(response)

        tool_calls = assistant_message.get("tool_calls")

        if not tool_calls:
            # 최종 텍스트 응답 완료
            return assistant_message.get("content", "")

        # tool_calls가 있으면 실행
        print(f"\n  도구 호출 {len(tool_calls)}개 감지")
        messages.append(assistant_message)

        for tc in tool_calls:
            tool_name = tc["function"]["name"]
            arguments = json.loads(tc["function"]["arguments"])
            tool_call_id = tc["id"]

            print(f"  도구 실행: {tool_name}({json.dumps(arguments, ensure_ascii=False)})")
            result = execute_tool(tool_name, arguments)
            print(f"  도구 결과: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result,
            })

    return "오류: 최대 반복 횟수를 초과했습니다."


# ============================================================
# 논스트리밍 vs 스트리밍 비교 데모
# ============================================================

def run_non_streaming(user_message: str) -> str:
    """비교를 위한 논스트리밍 버전"""
    url = f"{GATEWAY_BASE_URL}/chat/completions"
    headers = get_headers()

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": "도움이 되는 AI 어시스턴트입니다."},
            {"role": "user", "content": user_message},
        ],
        # stream 키 없음 → 논스트리밍
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        proxies=PROXIES,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def compare_streaming():
    """스트리밍과 논스트리밍의 차이를 보여주는 데모"""
    import time

    question = "인공지능의 역사를 간략하게 설명해줘"

    # 논스트리밍
    print("=" * 60)
    print("[논스트리밍] 전체 응답을 기다린 후 한꺼번에 출력")
    print("=" * 60)
    start = time.time()
    result = run_non_streaming(question)
    elapsed = time.time() - start
    print(result)
    print(f"\n총 소요 시간: {elapsed:.2f}초 (전체 응답까지 대기)")

    print()

    # 스트리밍
    print("=" * 60)
    print("[스트리밍] 토큰이 도착할 때마다 실시간 출력")
    print("=" * 60)
    start = time.time()
    response = call_llm_streaming(
        messages=[
            {"role": "system", "content": "도움이 되는 AI 어시스턴트입니다."},
            {"role": "user", "content": question},
        ]
    )
    first_token_time = None
    full = ""
    for chunk in parse_sse_stream(response):
        choices = chunk.get("choices", [])
        if not choices:
            continue
        content = choices[0].get("delta", {}).get("content", "")
        if content:
            if first_token_time is None:
                first_token_time = time.time() - start
            print(content, end="", flush=True)
            full += content
    print()
    elapsed = time.time() - start

    if first_token_time:
        print(f"\n첫 토큰까지: {first_token_time:.2f}초 (TTFT)")
    print(f"전체 완료: {elapsed:.2f}초")


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="스트리밍 Agent 데모")
    parser.add_argument(
        "--compare",
        action="store_true",
        help="스트리밍/논스트리밍 비교 실행",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Agent에게 보낼 질문",
    )
    args = parser.parse_args()

    if args.compare:
        compare_streaming()
    elif args.query:
        print("=" * 60)
        print("스트리밍 Agent Loop 데모")
        print("=" * 60)
        result = run_streaming_agent(args.query)
        print(f"\n{'=' * 60}")
        print(f"최종 응답: {result}")
    else:
        # 기본 데모
        print("=" * 60)
        print("스트리밍 Agent Loop 데모")
        print("=" * 60)

        print("\n[예시] 도구 호출이 포함된 스트리밍")
        result = run_streaming_agent("서울 날씨 알려주고, 123 + 456도 계산해줘")
        print(f"\n최종 응답: {result}")

"""
MCP 클라이언트 예제

FastMCP의 Client를 사용하여 MCP 서버에 연결하고,
도구(Tool), 리소스(Resource), 프롬프트(Prompt)를 호출하는 방법을 보여줍니다.

이 클라이언트는 mcp_server.py를 stdio 방식으로 실행하여 통신합니다.

실행 방법:
    python mcp_client.py

의존성:
    pip install mcp
"""

import asyncio
import json
import os
import sys

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ──────────────────────────────────────────────
# 결과를 보기 좋게 출력하는 헬퍼 함수
# ──────────────────────────────────────────────
def pretty_print(title: str, data):
    """제목과 데이터를 보기 좋게 출력합니다."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    if isinstance(data, (dict, list)):
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(data)
    print()


async def main():
    """MCP 클라이언트 메인 함수"""

    # ──────────────────────────────────────────
    # 서버 연결 설정
    # ──────────────────────────────────────────
    # StdioServerParameters: mcp_server.py를 subprocess로 실행하여 연결
    # command: 실행할 명령어 (python)
    # args: 명령어 인자 (서버 스크립트 경로)
    server_script = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    server_params = StdioServerParameters(
        command=sys.executable,  # 현재 Python 인터프리터 사용
        args=[server_script],
    )

    print("MCP 서버에 연결 중...")

    # stdio_client: 서버를 subprocess로 실행하고 stdio로 통신
    # ClientSession: MCP 프로토콜 세션 관리
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 세션 초기화 (프로토콜 핸드셰이크)
            await session.initialize()
            print("서버 연결 완료!")

            # ──────────────────────────────────
            # 1. 도구(Tool) 목록 조회 및 호출
            # ──────────────────────────────────
            # list_tools(): 서버에 등록된 모든 도구 목록을 가져옵니다.
            tools_result = await session.list_tools()
            tool_names = [tool.name for tool in tools_result.tools]
            pretty_print("등록된 도구 (Tools) 목록", tool_names)

            # 각 도구의 상세 정보 출력 (이름, 설명, 파라미터 스키마)
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
                if tool.inputSchema:
                    params = tool.inputSchema.get("properties", {})
                    param_info = ", ".join(
                        f"{k}: {v.get('type', '?')}" for k, v in params.items()
                    )
                    print(f"    파라미터: ({param_info})")

            # 도구 호출 예제: add (더하기)
            print("\n--- add(3, 5) 호출 ---")
            result = await session.call_tool("add", arguments={"a": 3, "b": 5})
            # result.content는 TextContent 객체의 리스트
            for content in result.content:
                pretty_print("add(3, 5) 결과", content.text)

            # 도구 호출 예제: get_weather (날씨 조회)
            print("--- get_weather('서울') 호출 ---")
            result = await session.call_tool(
                "get_weather", arguments={"city": "서울"}
            )
            for content in result.content:
                pretty_print("서울 날씨", content.text)

            # 도구 호출 예제: search_employee (직원 검색)
            print("--- search_employee('김철수') 호출 ---")
            result = await session.call_tool(
                "search_employee", arguments={"name": "김철수"}
            )
            for content in result.content:
                pretty_print("직원 검색 결과", content.text)

            # ──────────────────────────────────
            # 2. 리소스(Resource) 목록 조회 및 읽기
            # ──────────────────────────────────
            # list_resources(): 서버에 등록된 모든 리소스 목록을 가져옵니다.
            resources_result = await session.list_resources()
            resource_uris = [str(r.uri) for r in resources_result.resources]
            pretty_print("등록된 리소스 (Resources) 목록", resource_uris)

            # 리소스 읽기: config://app
            print("--- config://app 리소스 읽기 ---")
            resource_data = await session.read_resource("config://app")
            for content in resource_data.contents:
                pretty_print("앱 설정 (config://app)", content.text)

            # ──────────────────────────────────
            # 3. 프롬프트(Prompt) 목록 조회 및 사용
            # ──────────────────────────────────
            # list_prompts(): 서버에 등록된 모든 프롬프트 목록을 가져옵니다.
            prompts_result = await session.list_prompts()
            prompt_names = [p.name for p in prompts_result.prompts]
            pretty_print("등록된 프롬프트 (Prompts) 목록", prompt_names)

            # 프롬프트 호출: code_review_prompt
            sample_code = """
def calculate_total(items):
    total = 0
    for i in range(len(items)):
        total = total + items[i]['price'] * items[i]['qty']
    return total
"""
            print("--- code_review_prompt 호출 ---")
            prompt_result = await session.get_prompt(
                "code_review_prompt", arguments={"code": sample_code}
            )
            # 프롬프트 결과는 messages 리스트로 반환됩니다.
            for msg in prompt_result.messages:
                pretty_print(
                    f"프롬프트 결과 (role: {msg.role})",
                    msg.content.text,
                )

            print("\n모든 테스트가 완료되었습니다!")


if __name__ == "__main__":
    asyncio.run(main())

"""
Google ADK + MCP 연동 예제

ADK 에이전트에서 MCP 서버의 도구를 직접 사용하는 방법을 보여줍니다.
ADK는 MCPToolset을 통해 MCP 서버와의 연동을 기본 지원합니다.

전체 흐름:
1. MCP 서버를 stdio로 연결하여 MCPToolset 생성
2. MCPToolset에서 도구 목록을 가져와 ADK Agent에 등록
3. Runner를 통해 에이전트 실행
4. 에이전트가 필요 시 MCP 도구를 자동 호출

실행 방법:
    python adk_mcp_agent.py

의존성:
    pip install google-adk litellm mcp

주의:
    day1/01_mcp/mcp_server.py가 있어야 합니다.
"""

import asyncio
import os
import sys

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

# LiteLLM 프록시 설정
os.environ["HTTPS_PROXY"] = PROXY_URL
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["OPENAI_API_KEY"] = GATEWAY_API_KEY
os.environ["OPENAI_API_BASE"] = GATEWAY_BASE_URL

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import MCPToolset, StdioServerParameters
from google.genai import types


async def main():
    """ADK + MCP 연동 메인 함수"""

    print("=" * 60)
    print("  Google ADK + MCP 서버 연동 데모")
    print("=" * 60)

    # ──────────────────────────────────────────
    # 1단계: MCP 서버 연결 설정
    # ──────────────────────────────────────────
    # MCPToolset: ADK에서 MCP 서버의 도구를 사용할 수 있게 해주는 어댑터
    # StdioServerParameters: MCP 서버를 stdio 방식으로 실행
    mcp_server_script = os.path.join(
        os.path.dirname(__file__), "..", "01_mcp", "mcp_server.py"
    )

    print(f"\n[1단계] MCP 서버 연결 설정")
    print(f"  서버 스크립트: {mcp_server_script}")

    # MCPToolset 생성 - MCP 서버의 도구를 ADK 도구로 변환
    mcp_toolset = MCPToolset(
        connection_params=StdioServerParameters(
            command=sys.executable,
            args=[mcp_server_script],
        ),
    )

    # ──────────────────────────────────────────
    # 2단계: MCP 도구를 포함한 ADK 에이전트 생성
    # ──────────────────────────────────────────
    print("\n[2단계] MCP 도구를 포함한 ADK 에이전트 생성")

    model = LiteLlm(model=f"openai/{DEFAULT_MODEL}")

    # MCPToolset을 tools에 직접 전달
    # ADK가 MCP 서버에 연결하여 도구를 자동으로 가져옵니다.
    agent = Agent(
        name="mcp-assistant",
        model=model,
        instruction="""당신은 MCP 서버의 도구를 활용하는 AI 어시스턴트입니다.
사용자의 질문에 답하기 위해 사용 가능한 도구를 적극 활용하세요.

사용 가능한 도구:
- add: 두 숫자를 더합니다
- get_weather: 도시의 날씨를 조회합니다
- search_employee: 직원 정보를 검색합니다

답변은 항상 한국어로 해주세요.""",
        tools=[mcp_toolset],
        description="MCP 서버 도구를 사용하는 어시스턴트",
    )

    # ──────────────────────────────────────────
    # 3단계: Runner 설정 및 실행
    # ──────────────────────────────────────────
    print("\n[3단계] Runner 설정 및 에이전트 실행")

    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="mcp-demo",
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="mcp-demo",
        user_id="user-001",
    )

    # ──────────────────────────────────────────
    # 4단계: 테스트 질문 실행
    # ──────────────────────────────────────────
    queries = [
        "서울 날씨 알려줘",
        "3과 5를 더해줘",
        "김철수 직원 정보 찾아줘",
    ]

    for query in queries:
        print(f"\n{'─'*60}")
        print(f"사용자: {query}")
        print(f"{'─'*60}")

        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)],
        )

        response_events = runner.run_async(
            user_id="user-001",
            session_id=session.id,
            new_message=content,
        )

        async for event in response_events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"에이전트: {part.text}")
                    elif part.function_call:
                        print(f"  [MCP 도구 호출] {part.function_call.name}({dict(part.function_call.args)})")
                    elif part.function_response:
                        print(f"  [MCP 도구 응답] {part.function_response.name}: {dict(part.function_response.response)}")

    print(f"\n{'='*60}")
    print("  ADK + MCP 연동 데모 완료!")
    print(f"{'='*60}")
    print("\n[핵심 정리]")
    print("  - MCPToolset: MCP 서버의 도구를 ADK 에이전트에서 사용할 수 있게 변환")
    print("  - StdioServerParameters: MCP 서버를 subprocess로 실행하여 통신")
    print("  - Agent의 tools에 MCPToolset을 전달하면 자동으로 도구 등록")
    print("  - 에이전트가 MCP 도구를 마치 네이티브 도구처럼 호출 가능")


if __name__ == "__main__":
    asyncio.run(main())

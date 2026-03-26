"""
MCP (Model Context Protocol) 서버 예제

MCP는 LLM이 외부 도구, 리소스, 프롬프트에 접근할 수 있도록 하는 표준 프로토콜입니다.
이 서버는 FastMCP를 사용하여 세 가지 핵심 개념을 구현합니다:

1. Tool (도구): LLM이 호출할 수 있는 함수 (계산, API 호출 등)
2. Resource (리소스): LLM이 읽을 수 있는 데이터 소스 (설정, 파일 등)
3. Prompt (프롬프트): 재사용 가능한 프롬프트 템플릿

실행 방법:
    python mcp_server.py

의존성:
    pip install mcp
"""

import os
import sys

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

from mcp.server.fastmcp import FastMCP

# ──────────────────────────────────────────────
# FastMCP 서버 인스턴스 생성
# ──────────────────────────────────────────────
# name: 서버 이름 (클라이언트에서 식별용)
mcp = FastMCP("demo-server")


# ══════════════════════════════════════════════
# Tool (도구) 정의
# ══════════════════════════════════════════════
# @mcp.tool() 데코레이터로 LLM이 호출할 수 있는 도구를 등록합니다.
# LLM은 함수의 이름, 파라미터 타입, docstring을 보고 언제/어떻게 호출할지 결정합니다.
# 따라서 docstring을 명확하게 작성하는 것이 중요합니다.


@mcp.tool()
def add(a: float, b: float) -> float:
    """두 숫자를 더합니다.

    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자

    Returns:
        두 숫자의 합
    """
    return a + b


@mcp.tool()
def get_weather(city: str) -> dict:
    """주어진 도시의 현재 날씨 정보를 조회합니다.

    실제 프로덕션에서는 외부 날씨 API를 호출하겠지만,
    이 예제에서는 더미 데이터를 반환합니다.

    Args:
        city: 날씨를 조회할 도시 이름 (예: "서울", "부산")

    Returns:
        날씨 정보가 담긴 딕셔너리 (온도, 상태, 습도 등)
    """
    # 더미 날씨 데이터 (실제로는 API 호출)
    weather_data = {
        "서울": {"temperature": 15, "condition": "맑음", "humidity": 45},
        "부산": {"temperature": 18, "condition": "구름 많음", "humidity": 60},
        "제주": {"temperature": 20, "condition": "흐림", "humidity": 70},
        "대전": {"temperature": 14, "condition": "맑음", "humidity": 40},
        "인천": {"temperature": 13, "condition": "안개", "humidity": 80},
    }

    if city in weather_data:
        result = weather_data[city]
        result["city"] = city
        return result
    else:
        return {
            "city": city,
            "temperature": 16,
            "condition": "정보 없음 (기본값)",
            "humidity": 50,
        }


@mcp.tool()
def search_employee(name: str) -> dict:
    """사내 직원 정보를 이름으로 검색합니다.

    직원 이름을 입력하면 소속 부서, 직급, 연락처 등의 정보를 반환합니다.

    Args:
        name: 검색할 직원 이름

    Returns:
        직원 정보가 담긴 딕셔너리
    """
    # 더미 직원 데이터베이스
    employees = {
        "김철수": {
            "name": "김철수",
            "department": "개발팀",
            "position": "시니어 엔지니어",
            "email": "chulsoo.kim@company.com",
            "phone": "010-1234-5678",
        },
        "이영희": {
            "name": "이영희",
            "department": "기획팀",
            "position": "팀장",
            "email": "younghee.lee@company.com",
            "phone": "010-2345-6789",
        },
        "박민수": {
            "name": "박민수",
            "department": "데이터팀",
            "position": "ML 엔지니어",
            "email": "minsoo.park@company.com",
            "phone": "010-3456-7890",
        },
    }

    if name in employees:
        return employees[name]
    else:
        # 부분 일치 검색
        matches = [emp for key, emp in employees.items() if name in key]
        if matches:
            return {"results": matches, "count": len(matches)}
        return {"error": f"'{name}' 직원을 찾을 수 없습니다.", "count": 0}


# ══════════════════════════════════════════════
# Resource (리소스) 정의
# ══════════════════════════════════════════════
# @mcp.resource() 데코레이터로 LLM이 읽을 수 있는 데이터 소스를 등록합니다.
# 리소스는 URI 형식으로 식별되며, 설정 파일, DB 스키마, 문서 등을 제공할 수 있습니다.
# 도구(tool)와 달리 리소스는 부작용(side effect) 없이 데이터만 제공합니다.


@mcp.resource("config://app")
def get_app_config() -> str:
    """애플리케이션 설정 정보를 반환합니다.

    현재 서버의 설정값들을 JSON 형태의 문자열로 제공합니다.
    LLM이 시스템 설정을 이해하는 데 활용할 수 있습니다.
    """
    import json

    config = {
        "app_name": "MCP 데모 서버",
        "version": "1.0.0",
        "environment": "development",
        "supported_cities": ["서울", "부산", "제주", "대전", "인천"],
        "max_search_results": 10,
        "features": {
            "weather_api": True,
            "employee_search": True,
            "calculator": True,
        },
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════════
# Prompt (프롬프트) 정의
# ══════════════════════════════════════════════
# @mcp.prompt() 데코레이터로 재사용 가능한 프롬프트 템플릿을 등록합니다.
# 프롬프트는 특정 작업에 최적화된 지시문을 미리 정의해 두는 것입니다.
# 클라이언트가 프롬프트를 요청하면 인자를 받아 완성된 메시지를 반환합니다.


@mcp.prompt()
def code_review_prompt(code: str) -> str:
    """코드 리뷰를 위한 프롬프트 템플릿입니다.

    주어진 코드를 분석하여 개선점, 버그, 보안 이슈 등을 리뷰합니다.

    Args:
        code: 리뷰할 코드 문자열
    """
    return f"""다음 코드를 리뷰해주세요. 아래 항목들을 중심으로 분석해주세요:

1. **코드 품질**: 가독성, 네이밍 컨벤션, 코드 구조
2. **버그 가능성**: 잠재적 버그나 에러 처리 누락
3. **보안 이슈**: SQL 인젝션, XSS 등 보안 취약점
4. **성능**: 비효율적인 로직이나 최적화 가능한 부분
5. **개선 제안**: 리팩토링 또는 더 나은 패턴 제안

리뷰할 코드:
```
{code}
```

각 항목별로 구체적인 피드백을 한국어로 작성해주세요.
"""


# ──────────────────────────────────────────────
# 서버 실행
# ──────────────────────────────────────────────
if __name__ == "__main__":
    # stdio 전송 방식으로 서버를 실행합니다.
    # stdio: 표준 입출력을 통해 통신 (클라이언트가 subprocess로 실행)
    # 다른 옵션: sse (Server-Sent Events), streamable-http
    print("MCP 서버를 시작합니다...", file=sys.stderr)
    mcp.run(transport="stdio")

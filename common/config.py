"""
공통 설정 모듈

LLM 게이트웨이, 프록시, 모델 설정 등을 관리합니다.
환경 변수 또는 .env 파일에서 설정값을 로드합니다.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일 로드
_project_root = Path(__file__).resolve().parent.parent
_dotenv_path = _project_root / ".env"
if _dotenv_path.exists():
    load_dotenv(_dotenv_path)

# ──────────────────────────────────────────────
# LLM 게이트웨이 설정
# ──────────────────────────────────────────────
GATEWAY_BASE_URL: str = os.getenv(
    "LLM_GATEWAY_URL", "http://your-gateway-host:port/v1"
)
GATEWAY_API_KEY: str = os.getenv(
    "LLM_GATEWAY_API_KEY", "your-api-key"
)

# ──────────────────────────────────────────────
# 모델 설정
# ──────────────────────────────────────────────
DEFAULT_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# ──────────────────────────────────────────────
# 프록시 설정 (사내 프록시를 통해 외부 다운로드)
# ──────────────────────────────────────────────
PROXY_URL: str = os.getenv("HTTP_PROXY", "http://your-proxy-host:8000")

PROXIES: dict[str, str] = {
    "http": PROXY_URL,
    "https": PROXY_URL,
}

# 프록시를 우회할 내부 도메인/호스트 목록
NO_PROXY: str = os.getenv(
    "NO_PROXY",
    "localhost,127.0.0.1,.your-company.net"
)

# 사내 인증서 이슈로 SSL 검증 비활성화 (사내망 전용)
SSL_VERIFY: bool = os.getenv("SSL_VERIFY", "false").lower() == "true"

# 사내망 환경 프록시 자동 설정 (subprocess, requests 등에서 사용)
def setup_proxy_env():
    """프록시 관련 환경 변수를 일괄 설정합니다."""
    os.environ["HTTP_PROXY"] = PROXY_URL
    os.environ["HTTPS_PROXY"] = PROXY_URL
    os.environ["http_proxy"] = PROXY_URL
    os.environ["https_proxy"] = PROXY_URL
    os.environ["NO_PROXY"] = NO_PROXY
    os.environ["no_proxy"] = NO_PROXY
    os.environ["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"


def get_headers() -> dict[str, str]:
    """LLM 게이트웨이 요청에 필요한 HTTP 헤더를 반환합니다."""
    return {
        "Authorization": f"Bearer {GATEWAY_API_KEY}",
        "Content-Type": "application/json",
    }


def get_openai_client():
    """
    게이트웨이에 연결된 OpenAI 클라이언트를 반환합니다.

    base_url과 api_key가 게이트웨이 설정으로 구성되며,
    프록시가 필요한 경우 httpx 클라이언트를 통해 설정됩니다.

    Returns:
        openai.OpenAI: 설정이 완료된 OpenAI 클라이언트 인스턴스
    """
    try:
        import httpx
        from openai import OpenAI

        # 프록시를 경유하는 httpx 클라이언트 생성
        # SSL 검증 비활성화: 사내 프록시 인증서 이슈 대응
        http_client = httpx.Client(
            proxies=PROXY_URL,
            timeout=httpx.Timeout(60.0, connect=10.0),
            verify=SSL_VERIFY,
        )

        client = OpenAI(
            base_url=GATEWAY_BASE_URL,
            api_key=GATEWAY_API_KEY,
            http_client=http_client,
        )
        return client

    except ImportError as e:
        raise ImportError(
            "openai 또는 httpx 패키지가 설치되지 않았습니다. "
            "'pip install openai httpx'를 실행하세요."
        ) from e


def get_async_openai_client():
    """
    비동기 OpenAI 클라이언트를 반환합니다.

    Returns:
        openai.AsyncOpenAI: 설정이 완료된 비동기 OpenAI 클라이언트 인스턴스
    """
    try:
        import httpx
        from openai import AsyncOpenAI

        # 프록시를 경유하는 비동기 httpx 클라이언트 생성
        http_client = httpx.AsyncClient(
            proxies=PROXY_URL,
            timeout=httpx.Timeout(60.0, connect=10.0),
            verify=SSL_VERIFY,
        )

        client = AsyncOpenAI(
            base_url=GATEWAY_BASE_URL,
            api_key=GATEWAY_API_KEY,
            http_client=http_client,
        )
        return client

    except ImportError as e:
        raise ImportError(
            "openai 또는 httpx 패키지가 설치되지 않았습니다. "
            "'pip install openai httpx'를 실행하세요."
        ) from e

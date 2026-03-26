"""
연결 테스트 스크립트

LLM 게이트웨이, 임베딩 엔드포인트, 프록시 연결을 테스트합니다.
사용법: python setup/test_connection.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from common.config import (
    DEFAULT_MODEL,
    EMBEDDING_MODEL,
    GATEWAY_API_KEY,
    GATEWAY_BASE_URL,
    PROXIES,
    PROXY_URL,
    get_openai_client,
)

from rich.console import Console
from rich.panel import Panel

console = Console()


def test_llm_gateway() -> bool:
    """LLM 게이트웨이 연결을 테스트합니다. (간단한 채팅 완성 요청)"""
    console.print("\n[bold blue][1/3] LLM 게이트웨이 연결 테스트[/bold blue]")
    console.print(f"      URL: {GATEWAY_BASE_URL}")
    console.print(f"      모델: {DEFAULT_MODEL}")

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "user", "content": "Hello, respond with just 'OK'."}
            ],
            max_tokens=10,
            timeout=30,
        )

        # 응답 내용 확인
        reply = response.choices[0].message.content
        console.print(f"      응답: {reply}")
        console.print("      [bold green]SUCCESS[/bold green] - LLM 게이트웨이 연결 성공")
        return True

    except Exception as e:
        console.print(f"      [bold red]FAIL[/bold red] - LLM 게이트웨이 연결 실패: {e}")
        return False


def test_embedding() -> bool:
    """임베딩 엔드포인트 연결을 테스트합니다."""
    console.print("\n[bold blue][2/3] 임베딩 엔드포인트 테스트[/bold blue]")
    console.print(f"      URL: {GATEWAY_BASE_URL}")
    console.print(f"      모델: {EMBEDDING_MODEL}")

    try:
        client = get_openai_client()
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input="테스트 문장입니다.",
        )

        # 임베딩 벡터 차원 확인
        embedding_dim = len(response.data[0].embedding)
        console.print(f"      임베딩 차원: {embedding_dim}")
        console.print("      [bold green]SUCCESS[/bold green] - 임베딩 엔드포인트 연결 성공")
        return True

    except Exception as e:
        console.print(f"      [bold red]FAIL[/bold red] - 임베딩 엔드포인트 연결 실패: {e}")
        return False


def test_proxy() -> bool:
    """프록시 연결을 테스트합니다. (외부 URL에 접근 가능한지 확인)"""
    console.print("\n[bold blue][3/3] 프록시 연결 테스트[/bold blue]")
    console.print(f"      프록시: {PROXY_URL}")

    try:
        import requests

        # 프록시를 통해 외부 연결 테스트
        test_url = "https://www.google.com"
        response = requests.get(
            test_url,
            proxies=PROXIES,
            timeout=15,
            allow_redirects=True,
        )

        console.print(f"      대상 URL: {test_url}")
        console.print(f"      상태 코드: {response.status_code}")
        console.print("      [bold green]SUCCESS[/bold green] - 프록시 연결 성공")
        return True

    except Exception as e:
        console.print(f"      [bold red]FAIL[/bold red] - 프록시 연결 실패: {e}")
        return False


def main():
    """모든 연결 테스트를 실행합니다."""
    console.print(
        Panel(
            "[bold]연결 테스트를 시작합니다[/bold]\n"
            "LLM 게이트웨이, 임베딩, 프록시 연결을 확인합니다.",
            title="Connection Test",
            border_style="cyan",
        )
    )

    # 현재 설정값 표시
    console.print("\n[dim]현재 설정:[/dim]")
    console.print(f"  [dim]GATEWAY_BASE_URL  = {GATEWAY_BASE_URL}[/dim]")
    console.print(f"  [dim]GATEWAY_API_KEY   = {GATEWAY_API_KEY[:8]}...[/dim]" if len(GATEWAY_API_KEY) > 8 else f"  [dim]GATEWAY_API_KEY   = {GATEWAY_API_KEY}[/dim]")
    console.print(f"  [dim]DEFAULT_MODEL     = {DEFAULT_MODEL}[/dim]")
    console.print(f"  [dim]EMBEDDING_MODEL   = {EMBEDDING_MODEL}[/dim]")
    console.print(f"  [dim]PROXY_URL         = {PROXY_URL}[/dim]")

    # 테스트 실행
    results = {
        "LLM 게이트웨이": test_llm_gateway(),
        "임베딩 엔드포인트": test_embedding(),
        "프록시 연결": test_proxy(),
    }

    # 최종 결과 요약
    console.print("\n")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    if passed == total:
        style = "bold green"
        status = "ALL PASSED"
    elif passed > 0:
        style = "bold yellow"
        status = "PARTIAL"
    else:
        style = "bold red"
        status = "ALL FAILED"

    summary_lines = []
    for name, ok in results.items():
        icon = "[green]PASS[/green]" if ok else "[red]FAIL[/red]"
        summary_lines.append(f"  {icon}  {name}")

    console.print(
        Panel(
            "\n".join(summary_lines) + f"\n\n결과: {passed}/{total} 성공",
            title=f"테스트 결과 - {status}",
            border_style=style,
        )
    )

    # 실패한 테스트가 있으면 종료 코드 1로 종료
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()

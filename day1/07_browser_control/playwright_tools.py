"""
브라우저 자동화 도구 - Playwright 기반

Playwright를 사용하여 브라우저를 제어하는 도구 모음입니다.
CDP(Chrome DevTools Protocol)를 통해 브라우저와 통신합니다.

=== Playwright vs Selenium ===
- Playwright: Microsoft 개발, 최신 브라우저 지원, 빠른 속도, auto-wait
- Selenium: 오래된 표준, 넓은 브라우저 호환성
- CDP 직접 사용: 가장 Low-level, Electron 앱 제어에도 사용 가능

=== 설치 ===
pip install playwright
playwright install chromium

=== CDP (Chrome DevTools Protocol) ===
Chrome 계열 브라우저의 내부 통신 프로토콜입니다.
VS Code, Slack 등 Electron 앱도 CDP로 제어할 수 있습니다.
--remote-debugging-port 옵션으로 CDP 포트를 열 수 있습니다.
"""

import sys
import os
import json
import asyncio
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

# Playwright는 비동기 API를 주로 사용하지만,
# 동기(sync) API도 제공합니다. Agent 도구에서는 동기 API가 편리합니다.
try:
    from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("경고: playwright가 설치되지 않았습니다.")
    print("설치: pip install playwright && playwright install chromium")


# ============================================================
# 브라우저 매니저
# ============================================================

class BrowserManager:
    """
    브라우저 생명주기를 관리하는 싱글톤 클래스입니다.

    브라우저 인스턴스를 재사용하여 매번 새로 시작하는 오버헤드를 줄입니다.
    Agent가 여러 번 브라우저 도구를 호출해도 같은 브라우저를 사용합니다.
    """

    _instance: Optional["BrowserManager"] = None
    _playwright = None
    _browser: Optional["Browser"] = None
    _context: Optional["BrowserContext"] = None
    _page: Optional["Page"] = None

    @classmethod
    def get_instance(cls) -> "BrowserManager":
        """싱글톤 인스턴스를 반환합니다."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_browser(self):
        """브라우저가 실행 중인지 확인하고, 없으면 시작합니다."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError(
                "playwright가 설치되지 않았습니다. "
                "'pip install playwright && playwright install chromium'을 실행하세요."
            )

        if self._page is not None and not self._page.is_closed():
            return

        # Playwright 시작
        if self._playwright is None:
            self._playwright = sync_playwright().start()

        # 브라우저 시작 (headless: 화면 없이 실행)
        # headless=False로 변경하면 브라우저 창이 보입니다 (디버깅용)
        if self._browser is None or not self._browser.is_connected():
            self._browser = self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )

        # 브라우저 컨텍스트 (독립된 세션: 쿠키, 스토리지 분리)
        if self._context is None:
            self._context = self._browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            )

        # 페이지 (탭)
        if self._page is None or self._page.is_closed():
            self._page = self._context.new_page()

    @property
    def page(self) -> "Page":
        """현재 페이지 객체를 반환합니다."""
        self._ensure_browser()
        return self._page

    def close(self):
        """브라우저를 종료합니다."""
        try:
            if self._page and not self._page.is_closed():
                self._page.close()
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None
            BrowserManager._instance = None


# ============================================================
# 브라우저 도구 함수
# ============================================================

def navigate(url: str) -> str:
    """
    지정된 URL로 이동합니다.

    Args:
        url: 이동할 URL (https://example.com)

    Returns:
        이동 결과 (페이지 타이틀, URL)
    """
    try:
        bm = BrowserManager.get_instance()
        page = bm.page

        # goto: 페이지 이동 + 로딩 완료까지 대기
        response = page.goto(url, wait_until="domcontentloaded", timeout=30000)

        status = response.status if response else "알 수 없음"
        title = page.title()
        current_url = page.url

        return (
            f"페이지 이동 완료\n"
            f"  URL: {current_url}\n"
            f"  타이틀: {title}\n"
            f"  HTTP 상태: {status}"
        )
    except Exception as e:
        return f"페이지 이동 오류: {e}"


def get_page_content() -> str:
    """
    현재 페이지의 텍스트 내용을 추출합니다.

    HTML 태그를 제거하고 순수 텍스트만 반환합니다.
    LLM이 웹 페이지 내용을 이해할 수 있도록 정리합니다.

    Returns:
        페이지의 텍스트 내용 (최대 10,000자)
    """
    try:
        bm = BrowserManager.get_instance()
        page = bm.page

        title = page.title()
        url = page.url

        # inner_text(): 모든 HTML 태그를 제거하고 보이는 텍스트만 추출
        text = page.inner_text("body")

        # 연속 공백/줄바꿈 정리
        import re
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        text = text.strip()

        # 크기 제한 (LLM 컨텍스트 보호)
        max_length = 10_000
        if len(text) > max_length:
            text = text[:max_length] + "\n\n... (텍스트가 잘렸습니다)"

        return (
            f"=== 페이지 내용 ===\n"
            f"URL: {url}\n"
            f"타이틀: {title}\n"
            f"{'=' * 40}\n"
            f"{text}"
        )
    except Exception as e:
        return f"페이지 내용 추출 오류: {e}"


def click_element(selector: str) -> str:
    """
    CSS 셀렉터로 요소를 찾아 클릭합니다.

    Args:
        selector: CSS 셀렉터 (예: '#submit-button', '.nav-link', 'a[href="/about"]')

    Returns:
        클릭 결과
    """
    try:
        bm = BrowserManager.get_instance()
        page = bm.page

        # click(): 요소를 찾고, 보일 때까지 기다린 후 클릭
        page.click(selector, timeout=10000)

        # 클릭 후 페이지 변화 대기
        page.wait_for_load_state("domcontentloaded", timeout=10000)

        return (
            f"클릭 완료: {selector}\n"
            f"현재 URL: {page.url}\n"
            f"현재 타이틀: {page.title()}"
        )
    except Exception as e:
        return f"요소 클릭 오류 (selector: {selector}): {e}"


def fill_input(selector: str, value: str) -> str:
    """
    입력 필드에 텍스트를 입력합니다.

    Args:
        selector: CSS 셀렉터 (예: '#search-input', 'input[name="q"]')
        value: 입력할 텍스트

    Returns:
        입력 결과
    """
    try:
        bm = BrowserManager.get_instance()
        page = bm.page

        # fill(): 기존 값을 지우고 새 값을 입력
        page.fill(selector, value, timeout=10000)

        return f"입력 완료: {selector} ← '{value}'"
    except Exception as e:
        return f"입력 오류 (selector: {selector}): {e}"


def screenshot(path: str = "screenshot.png") -> str:
    """
    현재 페이지의 스크린샷을 저장합니다.

    Args:
        path: 저장할 파일 경로 (기본: screenshot.png)

    Returns:
        저장 결과
    """
    try:
        bm = BrowserManager.get_instance()
        page = bm.page

        # 절대경로로 변환
        abs_path = os.path.abspath(path)

        page.screenshot(path=abs_path, full_page=False)

        size = os.path.getsize(abs_path)
        return (
            f"스크린샷 저장 완료\n"
            f"  경로: {abs_path}\n"
            f"  크기: {size:,} bytes\n"
            f"  URL: {page.url}"
        )
    except Exception as e:
        return f"스크린샷 오류: {e}"


def get_links() -> str:
    """
    현재 페이지의 모든 링크를 추출합니다.

    Returns:
        링크 목록 (텍스트와 URL 포함)
    """
    try:
        bm = BrowserManager.get_instance()
        page = bm.page

        # JavaScript를 실행하여 모든 <a> 태그에서 href와 텍스트를 추출
        links = page.evaluate("""
            () => {
                const anchors = document.querySelectorAll('a[href]');
                return Array.from(anchors).map(a => ({
                    text: a.innerText.trim().substring(0, 100),
                    href: a.href
                })).filter(l => l.text && l.href);
            }
        """)

        if not links:
            return "현재 페이지에 링크가 없습니다."

        # 중복 제거
        seen = set()
        unique_links = []
        for link in links:
            key = link["href"]
            if key not in seen:
                seen.add(key)
                unique_links.append(link)

        result = f"=== 페이지 링크 ({len(unique_links)}개) ===\n"
        result += f"URL: {page.url}\n"
        result += "=" * 40 + "\n"

        for i, link in enumerate(unique_links[:50], 1):  # 최대 50개
            text = link["text"].replace("\n", " ")
            result += f"  {i}. [{text}] → {link['href']}\n"

        if len(unique_links) > 50:
            result += f"\n  ... 외 {len(unique_links) - 50}개"

        return result
    except Exception as e:
        return f"링크 추출 오류: {e}"


def search_google(query: str) -> str:
    """
    구글에서 검색하고 결과를 반환합니다.

    Args:
        query: 검색어

    Returns:
        검색 결과 (타이틀, URL, 설명)
    """
    try:
        bm = BrowserManager.get_instance()
        page = bm.page

        # 구글 검색 페이지로 이동
        page.goto(
            f"https://www.google.com/search?q={query}&hl=ko",
            wait_until="domcontentloaded",
            timeout=30000,
        )

        # 검색 결과 추출 (JavaScript 실행)
        results = page.evaluate("""
            () => {
                const items = document.querySelectorAll('div.g');
                return Array.from(items).slice(0, 10).map(item => {
                    const titleEl = item.querySelector('h3');
                    const linkEl = item.querySelector('a');
                    const descEl = item.querySelector('div[data-sncf], div.VwiC3b');
                    return {
                        title: titleEl ? titleEl.innerText : '',
                        url: linkEl ? linkEl.href : '',
                        description: descEl ? descEl.innerText : ''
                    };
                }).filter(r => r.title && r.url);
            }
        """)

        if not results:
            # 대체 추출 방법
            text = page.inner_text("body")
            return f"검색 결과를 구조화하여 추출하지 못했습니다.\n\n페이지 텍스트:\n{text[:5000]}"

        output = f"=== 구글 검색 결과: '{query}' ===\n"
        output += "=" * 40 + "\n"

        for i, r in enumerate(results, 1):
            output += f"\n{i}. {r['title']}\n"
            output += f"   URL: {r['url']}\n"
            if r["description"]:
                output += f"   설명: {r['description'][:200]}\n"

        return output
    except Exception as e:
        return f"구글 검색 오류: {e}"


def close_browser() -> str:
    """브라우저를 종료합니다."""
    try:
        BrowserManager.get_instance().close()
        return "브라우저가 종료되었습니다."
    except Exception as e:
        return f"브라우저 종료 오류: {e}"


# ============================================================
# OpenAI Tool Schema 정의
# ============================================================

BROWSER_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "navigate",
            "description": "웹 페이지로 이동합니다. URL을 지정하면 해당 페이지를 엽니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "이동할 URL (예: 'https://www.naver.com')",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_page_content",
            "description": "현재 열린 페이지의 텍스트 내용을 추출합니다. HTML 태그 없이 순수 텍스트만 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click_element",
            "description": "CSS 셀렉터로 웹 페이지의 요소를 클릭합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "클릭할 요소의 CSS 셀렉터 (예: '#submit-btn', '.nav-item', 'a[href=\"/about\"]')",
                    },
                },
                "required": ["selector"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fill_input",
            "description": "웹 페이지의 입력 필드에 텍스트를 입력합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "입력 필드의 CSS 셀렉터 (예: '#search-input', 'input[name=\"q\"]')",
                    },
                    "value": {
                        "type": "string",
                        "description": "입력할 텍스트",
                    },
                },
                "required": ["selector", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "screenshot",
            "description": "현재 페이지의 스크린샷을 PNG 파일로 저장합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "저장할 파일 경로 (기본: screenshot.png)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_links",
            "description": "현재 페이지의 모든 하이퍼링크(a 태그)를 추출합니다.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_google",
            "description": "구글에서 검색하고 상위 결과를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색어",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_browser",
            "description": "브라우저를 종료합니다.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# 도구 이름 -> 함수 매핑
BROWSER_TOOL_FUNCTIONS = {
    "navigate": navigate,
    "get_page_content": get_page_content,
    "click_element": click_element,
    "fill_input": fill_input,
    "screenshot": screenshot,
    "get_links": get_links,
    "search_google": search_google,
    "close_browser": close_browser,
}


# ============================================================
# 테스트
# ============================================================

if __name__ == "__main__":
    if not PLAYWRIGHT_AVAILABLE:
        print("playwright가 설치되지 않아 테스트를 건너뜁니다.")
        sys.exit(1)

    print("=== 브라우저 도구 테스트 ===\n")

    try:
        # 페이지 이동
        print("[navigate]")
        print(navigate("https://www.example.com"))
        print()

        # 페이지 내용 추출
        print("[get_page_content]")
        print(get_page_content())
        print()

        # 링크 추출
        print("[get_links]")
        print(get_links())
        print()

        # 스크린샷
        print("[screenshot]")
        print(screenshot("/tmp/test_screenshot.png"))
        print()

    finally:
        # 브라우저 종료
        print("[close_browser]")
        print(close_browser())

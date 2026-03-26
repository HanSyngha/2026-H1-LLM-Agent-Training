"""
Playwright 브라우저 자동화 예제

Playwright는 Microsoft가 개발한 브라우저 자동화 프레임워크입니다.
내부적으로 CDP(Chrome DevTools Protocol)를 사용하여 브라우저와 통신합니다.

=== Playwright 특징 ===
- 크로스 브라우저: Chromium, Firefox, WebKit 지원
- Auto-wait: 요소가 준비될 때까지 자동 대기
- 네트워크 인터셉션: 요청/응답 가로채기
- 다중 탭/컨텍스트: 독립된 세션 관리
- 모바일 에뮬레이션: 디바이스 시뮬레이션

=== Sync vs Async ===
Playwright는 두 가지 API를 제공합니다:
- sync_api: 동기식 (순차적, 간단, Agent 도구에 적합)
- async_api: 비동기식 (asyncio 기반, 고성능, 병렬 작업)

=== Headless vs Headed ===
- headless=True: 화면 없이 실행 (서버 환경, CI/CD, 자동화)
- headless=False: 브라우저 창 표시 (디버깅, 데모)

=== 설치 ===
pip install playwright
playwright install chromium
"""

import sys
import os
import json
import asyncio
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("경고: playwright가 설치되지 않았습니다.")
    print("설치: pip install playwright && playwright install chromium")


# ============================================================
# 동기(Sync) API 예제
# ============================================================

def sync_basic_navigation():
    """
    동기 API로 기본적인 페이지 이동 및 내용 추출을 수행합니다.

    sync_playwright()는 컨텍스트 매니저로 사용합니다:
    - __enter__: Playwright 시작
    - __exit__: Playwright 종료 (브라우저 포함)
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[Sync] playwright를 사용할 수 없습니다")
        return

    print("[Sync] 기본 네비게이션 예제")
    print("-" * 40)

    # sync_playwright()는 Playwright 인스턴스를 생성합니다
    with sync_playwright() as p:
        # 브라우저 시작
        # headless=True: 화면 없이 실행 (기본값)
        # headless=False: 브라우저 창이 보임 (디버깅용)
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        # 브라우저 컨텍스트: 독립된 세션 (쿠키, 스토리지 분리)
        # 시크릿 모드와 유사
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",  # 한국어 로케일
        )

        # 페이지(탭) 생성
        page = context.new_page()

        # 1. 페이지 이동
        print("\n  [1] 페이지 이동")
        response = page.goto(
            "https://www.example.com",
            wait_until="domcontentloaded",  # DOM 로딩 완료까지 대기
            timeout=30000,  # 30초 타임아웃
        )
        print(f"  URL: {page.url}")
        print(f"  타이틀: {page.title()}")
        print(f"  HTTP 상태: {response.status}")

        # 2. 페이지 텍스트 추출
        print("\n  [2] 페이지 텍스트")
        # inner_text(): 보이는 텍스트만 추출 (display:none 제외)
        text = page.inner_text("body")
        print(f"  텍스트 (처음 200자): {text[:200]}...")

        # 3. HTML 추출
        print("\n  [3] HTML 내용")
        # content(): 전체 HTML 소스
        html = page.content()
        print(f"  HTML 길이: {len(html)}자")

        # 4. JavaScript 실행
        print("\n  [4] JavaScript 실행")
        # evaluate(): 브라우저에서 JS 실행하고 결과 반환
        js_result = page.evaluate("""
            () => {
                return {
                    title: document.title,
                    url: window.location.href,
                    links: document.querySelectorAll('a').length,
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    }
                };
            }
        """)
        print(f"  JS 결과: {json.dumps(js_result, ensure_ascii=False, indent=4)}")

        # 5. 스크린샷
        print("\n  [5] 스크린샷")
        screenshot_path = os.path.join(
            os.path.dirname(__file__), "playwright_screenshot.png"
        )
        page.screenshot(
            path=screenshot_path,
            full_page=False,  # True: 전체 페이지 (스크롤 포함)
        )
        print(f"  저장: {screenshot_path}")

        # 리소스 정리 (컨텍스트 매니저가 자동으로 하지만 명시적으로도 가능)
        context.close()
        browser.close()

    print("\n[Sync] 완료!")


# ============================================================
# 동기 API - 폼 입력 및 클릭
# ============================================================

def sync_form_interaction():
    """
    동기 API로 폼 입력, 클릭, 대기 등을 수행합니다.

    Playwright의 핵심 장점인 auto-wait를 보여줍니다:
    - 요소가 DOM에 추가될 때까지 대기
    - 요소가 보일 때까지 대기
    - 요소가 안정적일 때까지 대기 (애니메이션 완료)
    - 요소가 활성화될 때까지 대기
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[Sync] playwright를 사용할 수 없습니다")
        return

    print("[Sync] 폼 입력 및 클릭 예제")
    print("-" * 40)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )
        page = browser.new_page()

        # 예시: 검색 사이트에서 검색
        page.goto("https://www.google.com", wait_until="domcontentloaded")
        print(f"  페이지: {page.title()}")

        # --- 셀렉터 종류 ---
        # CSS 셀렉터: "input[name='q']", "#submit", ".nav-item"
        # 텍스트 셀렉터: "text=로그인", "text=검색"
        # XPath: "xpath=//input[@name='q']"
        # Playwright 셀렉터: "role=button[name='검색']"

        # fill(): 기존 값을 지우고 새 값 입력
        # type(): 한 글자씩 입력 (키보드 이벤트 발생)
        try:
            # 검색어 입력
            page.fill('textarea[name="q"], input[name="q"]', "Playwright 자동화")
            print("  검색어 입력 완료")

            # Enter 키 입력
            page.keyboard.press("Enter")
            print("  Enter 키 입력")

            # 검색 결과 페이지 로딩 대기
            page.wait_for_load_state("domcontentloaded")
            print(f"  결과 페이지: {page.title()}")

        except PlaywrightTimeout:
            print("  타임아웃: 요소를 찾지 못했습니다")
        except Exception as e:
            print(f"  오류: {e}")

        browser.close()

    print("\n[Sync] 완료!")


# ============================================================
# 동기 API - 네이버 검색 자동화
# ============================================================

def sync_naver_search(query: str = "인공지능"):
    """
    네이버에서 검색을 자동화합니다.

    실제 업무에서 자주 사용되는 패턴:
    1. 사이트 접속
    2. 검색어 입력
    3. 결과 추출
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[네이버] playwright를 사용할 수 없습니다")
        return []

    print(f'[네이버] 검색: "{query}"')
    print("-" * 40)

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="ko-KR",
        )
        page = context.new_page()

        try:
            # 1. 네이버 접속
            page.goto("https://www.naver.com", wait_until="domcontentloaded")
            print(f"  네이버 접속: {page.title()}")

            # 2. 검색어 입력
            # 네이버 검색창 셀렉터
            search_input = page.locator("#query")
            search_input.fill(query)
            print(f"  검색어 입력: {query}")

            # 3. 검색 실행
            search_input.press("Enter")

            # 4. 검색 결과 페이지 대기
            page.wait_for_load_state("domcontentloaded")
            time.sleep(1)  # 동적 콘텐츠 로딩 대기
            print(f"  검색 결과 페이지: {page.url}")

            # 5. 검색 결과 추출 (JavaScript 실행)
            results = page.evaluate("""
                () => {
                    const items = [];

                    // 통합 검색 결과에서 링크 추출
                    const links = document.querySelectorAll(
                        '.total_wrap a.link_tit, .api_txt_lines a, .total_tit a'
                    );
                    links.forEach(a => {
                        const title = a.innerText.trim();
                        const href = a.href;
                        if (title && href) {
                            items.push({title, href});
                        }
                    });

                    return items.slice(0, 10);
                }
            """)

            print(f"\n  검색 결과 ({len(results)}개):")
            for i, r in enumerate(results, 1):
                title = r.get("title", "").replace("\n", " ")[:60]
                href = r.get("href", "")[:80]
                print(f"    {i}. {title}")
                print(f"       {href}")

            # 6. 스크린샷 저장
            screenshot_path = os.path.join(
                os.path.dirname(__file__), "naver_search.png"
            )
            page.screenshot(path=screenshot_path)
            print(f"\n  스크린샷: {screenshot_path}")

        except PlaywrightTimeout:
            print("  타임아웃: 네이버 접속이 느립니다")
        except Exception as e:
            print(f"  오류: {e}")

        finally:
            context.close()
            browser.close()

    print("\n[네이버] 완료!")
    return results


# ============================================================
# 페이지 콘텐츠 추출 (텍스트, 링크, 테이블)
# ============================================================

def sync_extract_content(url: str = "https://www.example.com"):
    """
    페이지에서 다양한 콘텐츠를 추출합니다.

    실무에서 자주 필요한 추출 패턴:
    - 텍스트: 페이지의 보이는 텍스트
    - 링크: 모든 하이퍼링크 (a 태그)
    - 테이블: HTML 테이블 데이터
    - 이미지: 이미지 URL 목록
    - 메타 정보: title, description, og 태그
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[추출] playwright를 사용할 수 없습니다")
        return {}

    print(f"[추출] URL: {url}")
    print("-" * 40)

    extracted = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )
        page = browser.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # 1. 메타 정보 추출
            print("\n  [1] 메타 정보")
            meta = page.evaluate("""
                () => ({
                    title: document.title,
                    description: document.querySelector('meta[name="description"]')
                        ?.getAttribute('content') || '',
                    ogTitle: document.querySelector('meta[property="og:title"]')
                        ?.getAttribute('content') || '',
                    ogDescription: document.querySelector('meta[property="og:description"]')
                        ?.getAttribute('content') || '',
                    ogImage: document.querySelector('meta[property="og:image"]')
                        ?.getAttribute('content') || '',
                    canonical: document.querySelector('link[rel="canonical"]')
                        ?.getAttribute('href') || '',
                })
            """)
            extracted["meta"] = meta
            print(f"  타이틀: {meta['title']}")
            if meta['description']:
                print(f"  설명: {meta['description'][:100]}")

            # 2. 텍스트 추출
            print("\n  [2] 텍스트 추출")
            text = page.inner_text("body")
            # 연속 줄바꿈/공백 정리
            import re
            text = re.sub(r"\n{3,}", "\n\n", text)
            text = re.sub(r" {2,}", " ", text).strip()
            extracted["text"] = text
            print(f"  텍스트 길이: {len(text)}자")
            print(f"  미리보기: {text[:200]}...")

            # 3. 링크 추출
            print("\n  [3] 링크 추출")
            links = page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('a[href]'))
                        .map(a => ({
                            text: a.innerText.trim().substring(0, 100),
                            href: a.href,
                        }))
                        .filter(l => l.text && l.href);
                }
            """)
            extracted["links"] = links
            print(f"  링크 수: {len(links)}개")
            for link in links[:5]:
                print(f"    - [{link['text'][:40]}] → {link['href'][:60]}")

            # 4. 테이블 추출
            print("\n  [4] 테이블 추출")
            tables = page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('table')).map(table => {
                        const rows = Array.from(table.querySelectorAll('tr'));
                        return rows.map(row => {
                            const cells = Array.from(
                                row.querySelectorAll('th, td')
                            );
                            return cells.map(cell => cell.innerText.trim());
                        });
                    });
                }
            """)
            extracted["tables"] = tables
            if tables:
                print(f"  테이블 수: {len(tables)}개")
                for i, table in enumerate(tables[:3]):
                    print(f"    테이블 {i+1}: {len(table)}행")
                    for row in table[:3]:
                        print(f"      {row}")
            else:
                print("  테이블 없음")

            # 5. 이미지 추출
            print("\n  [5] 이미지 추출")
            images = page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('img[src]'))
                        .map(img => ({
                            src: img.src,
                            alt: img.alt || '',
                            width: img.naturalWidth,
                            height: img.naturalHeight,
                        }))
                        .filter(img => img.src);
                }
            """)
            extracted["images"] = images
            print(f"  이미지 수: {len(images)}개")
            for img in images[:5]:
                print(f"    - {img['alt'][:30] or '(alt 없음)'}: {img['src'][:60]}")

        except Exception as e:
            print(f"  오류: {e}")

        finally:
            browser.close()

    print("\n[추출] 완료!")
    return extracted


# ============================================================
# 셀렉터 대기 및 타임아웃 처리
# ============================================================

def sync_wait_and_timeout():
    """
    셀렉터 대기 및 타임아웃 처리 패턴을 보여줍니다.

    Playwright의 대기(wait) 전략:
    1. auto-wait: click(), fill() 등이 자동으로 요소 대기
    2. wait_for_selector(): 명시적 대기
    3. wait_for_load_state(): 페이지 로딩 상태 대기
    4. wait_for_url(): URL 변경 대기
    5. wait_for_function(): JavaScript 조건 대기
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[대기] playwright를 사용할 수 없습니다")
        return

    print("[대기] 셀렉터 대기 및 타임아웃 예제")
    print("-" * 40)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )
        page = browser.new_page()
        page.goto("https://www.example.com", wait_until="domcontentloaded")

        # 1. wait_for_selector: 특정 요소가 나타날 때까지 대기
        print("\n  [1] wait_for_selector")
        try:
            # state 옵션:
            # "attached": DOM에 추가 (기본값)
            # "visible": 보이는 상태
            # "hidden": 숨겨진 상태
            # "detached": DOM에서 제거
            element = page.wait_for_selector(
                "h1",
                state="visible",
                timeout=5000,  # 5초
            )
            if element:
                print(f"  h1 요소 발견: {element.inner_text()}")
        except PlaywrightTimeout:
            print("  h1 요소를 찾지 못했습니다 (5초 타임아웃)")

        # 2. wait_for_load_state: 페이지 상태 대기
        print("\n  [2] wait_for_load_state")
        # "load": 모든 리소스 로딩 완료
        # "domcontentloaded": DOM 파싱 완료
        # "networkidle": 네트워크 요청이 500ms 동안 없음
        page.wait_for_load_state("domcontentloaded")
        print("  DOM 로딩 완료")

        # 3. locator 사용 (권장 방식)
        print("\n  [3] locator (권장)")
        # locator는 lazy하게 동작합니다
        # 실제 액션(click, fill 등)을 호출할 때 요소를 찾습니다
        heading = page.locator("h1")
        # count(): 매칭되는 요소 수
        count = heading.count()
        print(f"  h1 요소 수: {count}")

        if count > 0:
            # first: 첫 번째 요소
            text = heading.first.inner_text()
            print(f"  첫 번째 h1: {text}")

        # 4. 여러 요소 순회
        print("\n  [4] 여러 요소 순회")
        paragraphs = page.locator("p")
        p_count = paragraphs.count()
        print(f"  p 요소 수: {p_count}")
        for i in range(min(p_count, 3)):
            text = paragraphs.nth(i).inner_text()
            print(f"    p[{i}]: {text[:80]}...")

        # 5. 존재하지 않는 요소 처리
        print("\n  [5] 존재하지 않는 요소 처리")
        try:
            page.wait_for_selector(
                "#non-existent-element",
                timeout=2000,  # 2초만 대기
            )
        except PlaywrightTimeout:
            print("  예상대로 요소를 찾지 못했습니다 (정상)")

        # 6. is_visible / is_enabled 체크
        print("\n  [6] 요소 상태 체크")
        h1_visible = page.locator("h1").is_visible()
        print(f"  h1 보임: {h1_visible}")

        browser.close()

    print("\n[대기] 완료!")


# ============================================================
# 비동기(Async) API 예제
# ============================================================

async def async_basic_example():
    """
    비동기 API로 브라우저를 제어합니다.

    비동기 API의 장점:
    - 여러 페이지를 동시에 처리 (asyncio.gather)
    - I/O 대기 시간 동안 다른 작업 수행
    - 대량 크롤링에 적합

    비동기 API의 주의점:
    - 모든 호출에 await 필요
    - asyncio 이벤트 루프 내에서만 실행
    - Agent 도구로 사용하기에는 동기 API가 더 편리
    """
    print("[Async] 비동기 API 예제")
    print("-" * 40)

    # async_playwright()도 컨텍스트 매니저
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )
        page = await browser.new_page()

        # 모든 호출에 await 필요
        await page.goto("https://www.example.com", wait_until="domcontentloaded")
        title = await page.title()
        print(f"  타이틀: {title}")

        text = await page.inner_text("body")
        print(f"  텍스트 (100자): {text[:100]}...")

        await browser.close()

    print("[Async] 완료!")


async def async_parallel_pages():
    """
    비동기 API로 여러 페이지를 동시에 처리합니다.

    asyncio.gather()를 사용하면 여러 페이지를
    병렬로 로딩하고 내용을 추출할 수 있습니다.
    """
    print("[Async] 병렬 페이지 처리 예제")
    print("-" * 40)

    urls = [
        "https://www.example.com",
        "https://httpbin.org/html",
        "https://httpbin.org/json",
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )

        async def fetch_page(url: str) -> dict:
            """단일 페이지를 비동기로 처리합니다."""
            page = await browser.new_page()
            try:
                response = await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=15000,
                )
                title = await page.title()
                text = await page.inner_text("body")
                return {
                    "url": url,
                    "title": title,
                    "status": response.status if response else 0,
                    "text_length": len(text),
                    "text_preview": text[:100],
                }
            except Exception as e:
                return {"url": url, "error": str(e)}
            finally:
                await page.close()

        # 병렬 실행: 모든 페이지를 동시에 로딩
        start_time = time.time()
        results = await asyncio.gather(
            *[fetch_page(url) for url in urls],
            return_exceptions=True,
        )
        elapsed = time.time() - start_time

        print(f"\n  {len(urls)}개 페이지 병렬 처리 완료 ({elapsed:.2f}초)")
        for result in results:
            if isinstance(result, dict):
                if "error" in result:
                    print(f"    오류: {result['url']} → {result['error']}")
                else:
                    print(f"    {result['title']} ({result['status']}) - {result['text_length']}자")
            else:
                print(f"    예외: {result}")

        await browser.close()

    print("[Async] 완료!")


# ============================================================
# Sync vs Async 비교
# ============================================================

def sync_vs_async_comparison():
    """
    동기/비동기 API 코드 비교를 출력합니다.
    """
    print("=" * 60)
    print("Playwright Sync vs Async 비교")
    print("=" * 60)

    comparison = """
    ┌────────────────────────────────┬────────────────────────────────┐
    │         Sync API               │         Async API              │
    ├────────────────────────────────┼────────────────────────────────┤
    │ from playwright.sync_api       │ from playwright.async_api      │
    │   import sync_playwright       │   import async_playwright      │
    ├────────────────────────────────┼────────────────────────────────┤
    │ with sync_playwright() as p:   │ async with async_playwright()  │
    │                                │   as p:                        │
    ├────────────────────────────────┼────────────────────────────────┤
    │ browser = p.chromium.launch()  │ browser = await               │
    │                                │   p.chromium.launch()          │
    ├────────────────────────────────┼────────────────────────────────┤
    │ page.goto(url)                 │ await page.goto(url)           │
    ├────────────────────────────────┼────────────────────────────────┤
    │ title = page.title()           │ title = await page.title()     │
    ├────────────────────────────────┼────────────────────────────────┤
    │ text = page.inner_text("body") │ text = await                   │
    │                                │   page.inner_text("body")      │
    ├────────────────────────────────┼────────────────────────────────┤
    │ 사용 시나리오:                  │ 사용 시나리오:                  │
    │ - 단순 스크립트                 │ - 대량 크롤링                   │
    │ - Agent 도구 함수               │ - 병렬 페이지 처리             │
    │ - 순차적 작업                   │ - 서버 애플리케이션             │
    └────────────────────────────────┴────────────────────────────────┘
    """
    print(comparison)


# ============================================================
# 네트워크 인터셉션 예제
# ============================================================

def sync_network_interception():
    """
    네트워크 요청/응답을 인터셉트합니다.

    Playwright로 네트워크를 모니터링하거나
    요청을 수정/차단할 수 있습니다.
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[네트워크] playwright를 사용할 수 없습니다")
        return

    print("[네트워크] 네트워크 인터셉션 예제")
    print("-" * 40)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )
        page = browser.new_page()

        # 네트워크 이벤트 리스너 등록
        requests_log = []
        responses_log = []

        def on_request(request):
            """요청 발생 시 호출됩니다."""
            requests_log.append({
                "url": request.url[:80],
                "method": request.method,
                "type": request.resource_type,
            })

        def on_response(response):
            """응답 수신 시 호출됩니다."""
            responses_log.append({
                "url": response.url[:80],
                "status": response.status,
            })

        # 이벤트 핸들러 등록
        page.on("request", on_request)
        page.on("response", on_response)

        # 페이지 로딩
        page.goto("https://www.example.com", wait_until="networkidle")

        # 결과 출력
        print(f"\n  요청 수: {len(requests_log)}")
        for req in requests_log[:10]:
            print(f"    {req['method']} [{req['type']}] {req['url']}")

        print(f"\n  응답 수: {len(responses_log)}")
        for resp in responses_log[:10]:
            print(f"    {resp['status']} {resp['url']}")

        # 라우트(route)를 사용한 요청 차단/수정
        print("\n  [라우트] 이미지 요청 차단 예시:")
        print("    page.route('**/*.{png,jpg,jpeg,gif}', lambda route: route.abort())")
        print("    → 이미지 리소스 로딩을 차단하여 페이지 로딩 속도 향상")

        browser.close()

    print("\n[네트워크] 완료!")


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Playwright 브라우저 자동화 예제")
    print("=" * 60)

    if not PLAYWRIGHT_AVAILABLE:
        print("\nplaywright가 설치되지 않았습니다.")
        print("설치: pip install playwright && playwright install chromium")
        print("\nSync vs Async 비교만 출력합니다:")
        sync_vs_async_comparison()
        sys.exit(0)

    # 1. Sync vs Async 비교
    print("\n[1] Sync vs Async 비교")
    sync_vs_async_comparison()

    # 2. 동기 API - 기본 네비게이션
    print("\n[2] 동기 API - 기본 네비게이션")
    sync_basic_navigation()

    # 3. 동기 API - 폼 입력 및 클릭
    print("\n\n[3] 동기 API - 폼 입력 및 클릭")
    sync_form_interaction()

    # 4. 셀렉터 대기 및 타임아웃
    print("\n\n[4] 셀렉터 대기 및 타임아웃")
    sync_wait_and_timeout()

    # 5. 페이지 콘텐츠 추출
    print("\n\n[5] 페이지 콘텐츠 추출")
    sync_extract_content("https://www.example.com")

    # 6. 네트워크 인터셉션
    print("\n\n[6] 네트워크 인터셉션")
    sync_network_interception()

    # 7. 네이버 검색 자동화
    print("\n\n[7] 네이버 검색 자동화")
    sync_naver_search("인공지능")

    # 8. 비동기 API 예제
    print("\n\n[8] 비동기 API 예제")
    asyncio.run(async_basic_example())

    # 9. 비동기 병렬 처리
    print("\n\n[9] 비동기 병렬 처리")
    asyncio.run(async_parallel_pages())

    print("\n" + "=" * 60)
    print("모든 Playwright 예제 완료!")
    print("=" * 60)

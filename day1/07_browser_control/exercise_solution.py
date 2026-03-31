"""
브라우저 자동화 실습 정답: Playwright로 웹페이지 자동화 및 데이터 추출

Playwright를 사용하여 웹페이지에 접속하고,
데이터를 추출하여 JSON 파일로 저장합니다.

실행 방법:
    python exercise_solution.py

의존성:
    pip install playwright
    playwright install chromium
"""

import json
import os
import sys
import time

# 공통 설정 로드
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("경고: playwright가 설치되지 않았습니다.")
    print("설치: pip install playwright && playwright install chromium")


# ============================================================
# 실습 1: 네이버 검색 자동화 + 결과 추출
# ============================================================

def search_and_extract(query: str = "인공지능 에이전트") -> list[dict]:
    """네이버에서 검색하고 결과를 추출합니다.

    Args:
        query: 검색할 키워드

    Returns:
        검색 결과 리스트 (제목, URL 포함)
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[오류] Playwright가 설치되지 않았습니다.")
        return []

    print(f"[실습 1] 네이버 검색 자동화: '{query}'")
    print("-" * 50)

    results = []
    output_dir = os.path.dirname(__file__)

    with sync_playwright() as p:
        # 브라우저를 시작합니다 (headless 모드)
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="ko-KR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        try:
            # 1. 네이버에 접속합니다
            print("  1. 네이버 접속 중...")
            page.goto("https://www.naver.com", wait_until="domcontentloaded", timeout=30000)
            print(f"     타이틀: {page.title()}")

            # 2. 검색어를 입력합니다
            print(f"  2. 검색어 입력: '{query}'")
            search_input = page.locator("#query")
            search_input.fill(query)

            # 3. 검색을 실행합니다
            print("  3. 검색 실행...")
            search_input.press("Enter")
            page.wait_for_load_state("domcontentloaded")
            time.sleep(2)  # 동적 콘텐츠 로딩을 대기합니다

            # 4. 검색 결과를 추출합니다 (JavaScript 실행)
            print("  4. 검색 결과 추출 중...")
            results = page.evaluate("""
                () => {
                    const items = [];

                    // 통합 검색 결과에서 링크를 추출합니다
                    const selectors = [
                        '.total_wrap a.link_tit',
                        '.api_txt_lines a',
                        '.total_tit a',
                        '.news_tit',
                        'a.news_tit',
                    ];

                    for (const selector of selectors) {
                        document.querySelectorAll(selector).forEach(a => {
                            const title = a.innerText.trim();
                            const href = a.href;
                            if (title && href && !items.find(i => i.title === title)) {
                                items.push({title, url: href});
                            }
                        });
                    }

                    return items.slice(0, 5);
                }
            """)

            # 검색 결과를 출력합니다
            print(f"\n  검색 결과 (상위 {len(results)}개):")
            for i, r in enumerate(results, 1):
                print(f"    {i}. {r['title'][:60]}")
                print(f"       URL: {r['url'][:80]}")

            # 5. 결과를 JSON 파일로 저장합니다
            json_path = os.path.join(output_dir, "search_results.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"query": query, "results": results, "count": len(results)},
                    f, ensure_ascii=False, indent=2,
                )
            print(f"\n  5. JSON 저장: {json_path}")

            # 6. 스크린샷을 저장합니다
            screenshot_path = os.path.join(output_dir, "search_screenshot.png")
            page.screenshot(path=screenshot_path)
            print(f"  6. 스크린샷 저장: {screenshot_path}")

        except PlaywrightTimeout:
            print("  [오류] 타임아웃이 발생했습니다.")
        except Exception as e:
            print(f"  [오류] {e}")
        finally:
            context.close()
            browser.close()

    print("\n[실습 1] 완료!")
    return results


# ============================================================
# 실습 2: 웹페이지 데이터 추출 (범용)
# ============================================================

def extract_page_data(url: str = "https://www.example.com") -> dict:
    """웹페이지에서 다양한 데이터를 추출합니다.

    Args:
        url: 추출할 웹페이지 URL

    Returns:
        추출된 데이터 딕셔너리
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[오류] Playwright가 설치되지 않았습니다.")
        return {}

    print(f"\n[실습 2] 웹페이지 데이터 추출: {url}")
    print("-" * 50)

    extracted = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page()

        try:
            # 페이지에 접속합니다
            response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            print(f"  HTTP 상태: {response.status if response else 'N/A'}")

            # 1. 메타 정보를 추출합니다
            print("\n  [1] 메타 정보 추출")
            meta = page.evaluate("""
                () => ({
                    title: document.title,
                    description: document.querySelector('meta[name="description"]')
                        ?.getAttribute('content') || '',
                    ogTitle: document.querySelector('meta[property="og:title"]')
                        ?.getAttribute('content') || '',
                    charset: document.characterSet,
                    language: document.documentElement.lang || '',
                })
            """)
            extracted["meta"] = meta
            print(f"     타이틀: {meta['title']}")

            # 2. 텍스트를 추출합니다
            print("\n  [2] 텍스트 추출")
            text = page.inner_text("body")
            import re
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            extracted["text"] = text[:2000]
            print(f"     텍스트 길이: {len(text)}자")

            # 3. 링크를 추출합니다
            print("\n  [3] 링크 추출")
            links = page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]'))
                    .map(a => ({text: a.innerText.trim().substring(0, 100), url: a.href}))
                    .filter(l => l.text && l.url)
                    .slice(0, 20)
            """)
            extracted["links"] = links
            print(f"     링크 수: {len(links)}개")

            # 4. 이미지를 추출합니다
            print("\n  [4] 이미지 추출")
            images = page.evaluate("""
                () => Array.from(document.querySelectorAll('img[src]'))
                    .map(img => ({src: img.src, alt: img.alt || ''}))
                    .filter(img => img.src)
                    .slice(0, 10)
            """)
            extracted["images"] = images
            print(f"     이미지 수: {len(images)}개")

            # 5. 결과를 JSON으로 저장합니다
            output_path = os.path.join(os.path.dirname(__file__), "extracted_data.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(extracted, f, ensure_ascii=False, indent=2)
            print(f"\n  결과 저장: {output_path}")

        except Exception as e:
            print(f"  [오류] {e}")
        finally:
            browser.close()

    print("\n[실습 2] 완료!")
    return extracted


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  브라우저 자동화 실습 정답")
    print("=" * 60)

    if not PLAYWRIGHT_AVAILABLE:
        print("\nPlaywright가 설치되지 않았습니다.")
        print("설치 방법:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)

    # 실습 1: 네이버 검색 자동화
    results = search_and_extract("인공지능 에이전트")

    # 실습 2: 웹페이지 데이터 추출
    data = extract_page_data("https://www.example.com")

    print(f"\n{'=' * 60}")
    print("  모든 실습 완료!")
    print(f"{'=' * 60}")

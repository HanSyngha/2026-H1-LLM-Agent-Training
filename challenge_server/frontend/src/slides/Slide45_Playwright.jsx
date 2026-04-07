import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide45_Playwright() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">브라우저 자동화</Badge>
        <SlideH2>Playwright 사용법 핵심</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="python">{`from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 네비게이션
    page.goto("https://search.example.com")

    # 요소 조작
    page.fill("input[name='query']", "LLM Agent")
    page.click("button[type='submit']")

    # 대기 (자동 재시도)
    page.wait_for_selector(".results")

    # 데이터 추출
    titles = page.query_selector_all(".result-title")
    for t in titles:
        print(t.text_content())

    browser.close()`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

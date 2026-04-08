import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide48_BrowserAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">브라우저 실습</Badge>
        <SlideH2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="prompt">{`Python으로 브라우저 자동화하여 JS 렌더링 페이지에서 비밀 키를 추출해줘.

대상 페이지: http://a2g.samsungds.net:47777/browser-target
- 이 페이지는 JavaScript로 1초 후 비밀 키를 렌더링함
- requests.get()으로는 "로딩 중..."만 보임
- 브라우저를 실제로 열어서 JS 실행 후 텍스트를 읽어야 함

방법 1 (Playwright 추천):
  pip install playwright && playwright install chromium
  from playwright.sync_api import sync_playwright
  페이지 열고 → #secret-key 요소의 텍스트 추출

방법 2 (CDP 직접):
  Chrome을 --remote-debugging-port=9222로 실행
  CDP WebSocket 연결 → Page.navigate → Runtime.evaluate
  document.getElementById('secret-key').textContent 로 추출

추출한 키를 아래로 제출:
  POST http://a2g.samsungds.net:47777/challenges/browser/submit
  {"token":"SSO토큰","answer":{"secret_key":"추출한키"}}`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

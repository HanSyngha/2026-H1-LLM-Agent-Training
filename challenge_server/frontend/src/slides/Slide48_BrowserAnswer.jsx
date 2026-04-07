import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide48_BrowserAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">브라우저 실습</Badge>
        <SlideH2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="prompt">{`Chrome CDP로 웹페이지에서 데이터를 추출해줘.

1. Chrome을 --remote-debugging-port=9222로 실행
   (Windows: chrome.exe --remote-debugging-port=9222)
2. CDP WebSocket으로 연결
3. http://a2g.samsungds.net:47777/browser-target 로 이동
4. JS 렌더링 대기 후 테이블에서 제품명/가격 추출
5. POST /challenges/browser/submit 에 제출
   {"token":"SSO토큰","answer":{"products":[{"name":"...","price":123000}]}}

CDP: Page.navigate, Runtime.evaluate 사용
가격은 숫자만 (쉼표, '원' 제거)`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

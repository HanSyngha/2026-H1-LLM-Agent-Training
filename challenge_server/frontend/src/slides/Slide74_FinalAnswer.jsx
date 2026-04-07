import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide74_FinalAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">종합 실습</Badge>
        <SlideH2 day2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="text">{`브라우저로 검색하고 결과를 추출하는 코드를 만들어줘.

1. GET /challenges/final/mission 에서 검색 키워드 확인
2. Chrome CDP로 네이버/구글에서 키워드 검색
3. 검색 결과 상위 5개의 제목과 링크 추출
4. POST /challenges/final/submit 에 제출
   {"token":"SSO토큰","answer":{"items":[{"title":"...","link":"https://..."}]}}

Chrome --remote-debugging-port=9222 로 실행
CDP로 검색 → 결과 대기 → DOM에서 추출`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide36_StructuredAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Structured Output 실습</Badge>
        <SlideH2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="prompt">{`LLM의 Structured Output으로 뉴스 기사를 분석해줘.

GET /challenges/structured/mission 에서 기사 받기
response_format: {"type": "json_object"} 사용
필요 필드: title, category(기술/경제/정치/사회/스포츠),
  sentiment(긍정/부정/중립), keywords(3~5개 배열), summary(2문장)

POST /challenges/structured/submit 에 제출
{"token":"SSO토큰","answer":{title,category,sentiment,keywords,summary}}`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

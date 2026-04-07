import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide30_EndpointAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Endpoint 실습</Badge>
        <SlideH2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="prompt">{`Python requests로 사내 LLM Gateway에 연결해줘.

- URL: .env의 LLM_GATEWAY_URL (OpenAI Compatible)
- /v1/chat/completions 에 POST
- 미션 질문을 보내고 응답을 받아서
- POST /challenges/endpoint/submit 에 제출
  {"token":"SSO토큰","answer":{"response":"LLM 응답 텍스트"}}`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

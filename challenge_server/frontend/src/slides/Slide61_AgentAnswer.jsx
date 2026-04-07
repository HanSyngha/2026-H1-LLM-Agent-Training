import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide61_AgentAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agentic Loop 실습</Badge>
        <SlideH2 day2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="text">{`Python requests만 사용해서 Agent Loop를 구현해줘.

1. GET /challenges/agent_loop/mission 에서 미션 확인
2. 도구 정의: get_weather(city), calculate(expression)
3. Agent Loop:
   - 질문 + tools를 LLM에 전송
   - tool_calls 있으면 → 실행 → 결과를 messages에 추가 → 재호출
   - tool_calls 없으면 → 최종 답변
4. POST /challenges/agent_loop/submit 에 제출
   {"token":"SSO토큰","answer":{"response":"섭씨: X°C, 화씨: Y°F"}}

/v1/chat/completions에 tools 파라미터로 정의
choices[0].message.tool_calls 파싱`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

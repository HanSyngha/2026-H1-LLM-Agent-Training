import { motion } from 'framer-motion';
import { Badge, SlideH2, Box, CodeBlock } from './SlideLayout';

export default function Slide19_Prompt2() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">프롬프트</Badge>
        <SlideH2>system / user / assistant 역할</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="python">{`# OpenAI 호환 메시지 구조
messages = [
    {"role": "system",    # 시스템 지시문 (성격, 규칙, 형식)
     "content": "당신은 사내 업무 도우미입니다. 한국어로 답변하세요."},

    {"role": "user",      # 사용자 입력
     "content": "오늘 회의실 예약 현황 알려줘"},

    {"role": "assistant", # AI 응답 (또는 few-shot 예시)
     "content": "3층 A회의실: 10:00-11:00 예약됨..."}
]`}</CodeBlock>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Box color="blue" style={{ fontSize: '.92em' }}>
            <strong>핵심:</strong> system 메시지에 역할, 제약조건, 출력 형식을 명확히 정의하면 일관된 결과를 얻을 수 있습니다.
          </Box>
        </motion.div>
      </div>
    </div>
  );
}

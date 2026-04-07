import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';

export default function Slide60_AgentTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agentic Loop 실습</Badge>
        <SlideH2 day2>바이브 코딩: Agent Loop 구현</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Box color="blue" style={{ marginTop: '0.6em', fontSize: '.95em', padding: '20px 28px' }}>
            <BoxTitle>문제</BoxTitle>
            <strong>requests만</strong> 사용하여 Agent Loop를 구현하세요. <strong style={{ color: '#dc2626' }}>프레임워크 사용 금지.</strong><br /><br />
            <strong>질문:</strong> "서울의 현재 기온은 섭씨 몇 도이며, 이를 화씨로 변환하면 몇 도인가요?"<br />
            <strong>도구:</strong> <code>get_weather(city)</code>, <code>calculate(expression)</code> — LLM tool_calls로 정의
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}>
          <Box color="yellow" style={{ marginTop: '0.4em', fontSize: '.88em', padding: '14px 24px' }}>
            <strong>성공 조건:</strong> 응답에 <strong>섭씨 값(°C)</strong>과 <strong>화씨 값(°F)</strong>이 모두 포함되어야 합니다.<br />
            <strong>제출:</strong> <code>POST http://a2g.samsungds.net:47777/challenges/agent_loop/submit</code><br />
            <code>{`{"token":"SSO토큰", "answer":{"response":"섭씨: 22°C, 화씨: 71.6°F"}}`}</code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Box color="green" style={{ marginTop: '0.4em', fontSize: '1em', textAlign: 'center' }}>
            <strong>성공:</strong> 홍길동님, Agentic Loop 통과!
          </Box>
        </motion.div>
      </div>
    </div>
  );
}

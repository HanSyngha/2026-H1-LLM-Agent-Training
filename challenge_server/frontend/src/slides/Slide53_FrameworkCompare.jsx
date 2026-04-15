import { motion } from 'framer-motion';
import { Badge, SlideH2, Box, BoxTitle } from './SlideLayout';

export default function Slide53_FrameworkCompare() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agent Framework</Badge>
        <SlideH2 day2>프레임워크 비교 + 생태계</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <table style={{ fontSize: '.85em', marginTop: '0.6em' }}>
            <thead>
              <tr>
                <th>프레임워크</th>
                <th>핵심 특징</th>
                <th>적합한 상황</th>
              </tr>
            </thead>
            <tbody>
              <tr><td><strong style={{ color: '#3b82f6' }}>Google ADK</strong></td><td>간결한 API, Gemini 최적화</td><td>빠른 프로토타이핑</td></tr>
              <tr><td><strong style={{ color: '#10b981' }}>LangGraph</strong></td><td>그래프 기반, 상태 관리</td><td>복잡한 워크플로우</td></tr>
              <tr><td><strong style={{ color: '#8b5cf6' }}>OpenAI Agents SDK</strong></td><td>Handoff, Guardrail 내장</td><td>OpenAI 생태계</td></tr>
              <tr><td><strong style={{ color: '#ea580c' }}>CrewAI</strong></td><td>역할 기반 멀티에이전트</td><td>팀 시뮬레이션</td></tr>
              <tr><td><strong style={{ color: '#d97706' }}>Agno</strong></td><td>경량, 모듈형</td><td>커스텀 빌드</td></tr>
            </tbody>
          </table>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Box color="yellow" style={{ marginTop: '0.8em', fontSize: '.9em' }}>
            <strong>핵심:</strong> Agent Framework의 진짜 가치는 <strong style={{ color: '#3b82f6' }}>history 관리법, loop 관리법, multi-agent 관리법</strong>입니다.
            프레임워크를 통째로 가져오기보다, 이 아이디어를 우리 환경에 맞게 경량 구현하세요.
          </Box>
        </motion.div>
      </div>
    </div>
  );
}

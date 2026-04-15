import { motion } from 'framer-motion';
import { Badge, SlideH2, Box, BoxTitle, Grid, Quote } from './SlideLayout';

export default function Slide54_Trend() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">트렌드</Badge>
        <SlideH2 day2>Multi-Agent에서 Single Agent로</SlideH2>
        <p>프레임워크를 통째로 쓰지 않고, history/loop/orchestration 아이디어만 가져와서 경량 구현합니다</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Grid cols={2} gap={20}>
            <Box color="red" style={{ textAlign: 'center' }}>
              <BoxTitle color="#dc2626">1세대 (2024-2025)</BoxTitle>
              <p style={{ fontSize: '1.05em', fontWeight: 600, margin: '.5em 0' }}>다수의 전문 Agent 협업</p>
              <ul style={{ fontSize: '.95em', textAlign: 'left' }}>
                <li>A2A, CrewAI, ADK, AutoGen</li>
                <li>Agent 간 역할 분담</li>
                <li>복잡한 오케스트레이션</li>
                <li>오버헤드 큼, 디버깅 어려움</li>
              </ul>
            </Box>
            <Box color="green" style={{ textAlign: 'center' }}>
              <BoxTitle color="#059669">현재 트렌드 (2025-2026)</BoxTitle>
              <p style={{ fontSize: '1.05em', fontWeight: 600, margin: '.5em 0' }}>하나의 유능한 Agent + 효율적 Tool</p>
              <ul style={{ fontSize: '.95em', textAlign: 'left' }}>
                <li>OpenAI Agents SDK, Claude Code</li>
                <li>단일 Agent + Tool Calling</li>
                <li>경량 오케스트레이션</li>
                <li>디버깅 쉬움, 예측 가능</li>
              </ul>
            </Box>
          </Grid>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Quote borderColor="#7c3aed">
            "진짜 남는 가치는 그 기술이 <strong style={{ color: '#3b82f6' }}>풀려고 한 문제의식</strong>과 <strong style={{ color: '#8b5cf6' }}>아이디어</strong>입니다."
          </Quote>
        </motion.div>
      </div>
    </div>
  );
}

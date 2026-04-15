import { motion } from 'framer-motion';
import { SlideTitle, Divider, Quote, Grid, Card } from './SlideLayout';

export default function Slide76_Message() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <h1 className="slide-title" style={{ fontSize: '2.2em' }}>핵심 메시지</h1>
        </motion.div>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Quote borderColor="#7c3aed">
            "MCP, Harness Engineering, OpenAI Compatible, Agent Framework 모두 같습니다.<br />
            <strong style={{ color: '#3b82f6' }}>왜 이 아이디어가 나왔는지</strong> 먼저 이해하고,<br />
            <strong style={{ color: '#8b5cf6' }}>프레임워크가 아니라 아이디어만 경량 구현</strong>하세요."
          </Quote>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Grid cols={3} gap={20}>
            <Card borderColor="#2563eb">
              <h4>평가</h4>
              <p style={{ fontSize: '.92em' }}>기술이 <strong>왜</strong> 만들어졌는지<br />보고, 남길 아이디어와<br />버릴 복잡도를 구분하세요</p>
            </Card>
            <Card borderColor="#10b981">
              <h4 style={{ color: '#10b981' }}>추출</h4>
              <p style={{ fontSize: '.92em' }}>REST의 표준화, history 관리,<br />loop 관리처럼 <strong>핵심 아이디어만</strong><br />가져오세요</p>
            </Card>
            <Card borderColor="#8b5cf6">
              <h4 style={{ color: '#8b5cf6' }}>단순화</h4>
              <p style={{ fontSize: '.92em' }}>우리 조직 문제에 맞게<br />작게 구현하고, 필요할 때만<br />구조를 추가하세요</p>
            </Card>
          </Grid>
        </motion.div>
      </div>
    </div>
  );
}

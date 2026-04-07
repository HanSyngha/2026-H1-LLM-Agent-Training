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
            "오픈소스를 통째로 도입할 필요성은 줄어들고 있습니다.<br />
            <strong style={{ color: '#3b82f6' }}>왜 만들었는지</strong> 고민하시고,<br />
            <strong style={{ color: '#8b5cf6' }}>아이디어만 경량화로 도입</strong>하세요."
          </Quote>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Grid cols={3} gap={20}>
            <Card borderColor="#2563eb">
              <h4>평가</h4>
              <p style={{ fontSize: '.92em' }}>기술이 <strong>왜</strong> 만들어졌는지<br />고민하고, 우리 조직에<br />맞는지 판단하세요</p>
            </Card>
            <Card borderColor="#10b981">
              <h4 style={{ color: '#10b981' }}>추출</h4>
              <p style={{ fontSize: '.92em' }}>통째로 도입하지 말고<br /><strong>핵심 아이디어만</strong><br />경량화로 가져와라</p>
            </Card>
            <Card borderColor="#8b5cf6">
              <h4 style={{ color: '#8b5cf6' }}>단순화</h4>
              <p style={{ fontSize: '.92em' }}>하나의 유능한 Agent +<br />효율적 Tool 호출이<br />답입니다</p>
            </Card>
          </Grid>
        </motion.div>
      </div>
    </div>
  );
}

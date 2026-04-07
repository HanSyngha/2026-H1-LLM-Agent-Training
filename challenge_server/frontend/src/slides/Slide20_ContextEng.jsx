import { motion } from 'framer-motion';
import { Badge, SlideH2, Quote, Grid, Card } from './SlideLayout';

export default function Slide20_ContextEng() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">프롬프트</Badge>
        <SlideH2>컨텍스트 엔지니어링</SlideH2>
        <motion.p initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          2026 트렌드 -- "프롬프트"를 넘어 "컨텍스트"를 설계하세요
        </motion.p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Quote author="Andrej Karpathy">
            "The art of filling the context window with the right information<br />for the next step."
          </Quote>
        </motion.div>

        <Grid cols={4} gap={16}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card borderColor="#2563eb">
              <h4>System<br />Prompt</h4>
              <p style={{ fontSize: '.82em' }}>역할과 규칙</p>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card borderColor="#059669">
              <h4 style={{ color: '#10b981' }}>RAG<br />결과</h4>
              <p style={{ fontSize: '.82em' }}>검색된 문서</p>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
            <Card borderColor="#d97706">
              <h4 style={{ color: '#d97706' }}>Tool<br />결과</h4>
              <p style={{ fontSize: '.82em' }}>API 응답 데이터</p>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
            <Card borderColor="#7c3aed">
              <h4 style={{ color: '#8b5cf6' }}>대화<br />히스토리</h4>
              <p style={{ fontSize: '.82em' }}>이전 맥락 유지</p>
            </Card>
          </motion.div>
        </Grid>

        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          style={{ marginTop: '.8em', fontSize: '.95em' }}>
          무엇을 넣고, 무엇을 <strong style={{ color: '#dc2626' }}>빼는지</strong>가 성능을 결정합니다
        </motion.p>
      </div>
    </div>
  );
}

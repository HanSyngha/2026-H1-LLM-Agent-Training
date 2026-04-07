import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Quote, Grid, Card } from './SlideLayout';

export default function Slide17_AILearning2() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">AI 기초</Badge>
        <SlideH2>사내에서의 AI 활용</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Quote>
            "우리는 모델을 만드는 것이 아니라,<br />
            모델을 <strong style={{ color: '#2563eb' }}>잘 사용하는 방법</strong>을 만드는 것입니다."
          </Quote>
        </motion.div>

        <Grid cols={3} gap={20}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card borderColor="#059669">
              <h4 style={{ color: '#10b981' }}>RAG</h4>
              <p>사내 문서/DB에서<br />관련 정보를 검색해<br />LLM에 주입</p>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card borderColor="#2563eb">
              <h4>프롬프트 엔지니어링</h4>
              <p>정확한 지시문으로<br />원하는 출력 형태<br />유도</p>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
            <Card borderColor="#7c3aed">
              <h4 style={{ color: '#8b5cf6' }}>Tool 연동</h4>
              <p>API/DB/파일 등<br />외부 도구와<br />LLM 연결</p>
            </Card>
          </motion.div>
        </Grid>
      </div>
    </div>
  );
}

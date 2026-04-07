import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider } from './SlideLayout';

export default function Slide16_AILearning1() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">AI 기초</Badge>
        <SlideH2>"학습"이라는 단어의 모호성</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <table style={{ marginTop: '1em' }}>
            <thead>
              <tr>
                <th>구분</th>
                <th>의미</th>
                <th>우리가 하는 것?</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong style={{ color: '#2563eb' }}>모델 학습 (Pre-training)</strong></td>
                <td>수조 토큰으로 처음부터 훈련<br />수억 달러 + 수천 GPU</td>
                <td style={{ color: '#dc2626' }}>X</td>
              </tr>
              <tr>
                <td><strong style={{ color: '#2563eb' }}>파인튜닝 (Fine-tuning)</strong></td>
                <td>기존 모델에 추가 데이터로 조정<br />전문성 부여</td>
                <td style={{ color: '#d97706' }}>드물게</td>
              </tr>
              <tr>
                <td><strong style={{ color: '#2563eb' }}>RAG + 프롬프트</strong></td>
                <td>외부 지식 주입 + 지시문 설계<br />코드로 구현</td>
                <td style={{ color: '#059669', fontWeight: 700, fontSize: '1.1em' }}>&#10004; 이것!</td>
              </tr>
            </tbody>
          </table>
        </motion.div>
      </div>
    </div>
  );
}

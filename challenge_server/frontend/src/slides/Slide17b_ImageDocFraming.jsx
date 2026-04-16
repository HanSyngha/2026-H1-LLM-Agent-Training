import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Quote, Grid, Card } from './SlideLayout';

export default function Slide17b_ImageDocFraming() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">AI 기초</Badge>
        <SlideH2>문제 정의가 솔루션을 결정한다</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Quote>
            "AI로 <strong style={{ color: '#2563eb' }}>이미지 문서</strong>를 처리해주세요" — 그 다음 질문이 제일 중요합니다.<br />
            <span style={{ fontSize: '.85em', color: '#64748b' }}>무엇을 원하는지에 따라 완전히 다른 기술이 필요합니다.</span>
          </Quote>
        </motion.div>

        <Grid cols={3} gap={20}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <Card borderColor="#2563eb">
              <h4>📄 글자만 뽑아내기</h4>
              <p style={{ fontSize: '.9em', color: '#475569', marginBottom: 8 }}>
                스캔 문서, 영수증, 사진 속 텍스트를<br />구조화된 텍스트로 변환
              </p>
              <div style={{ fontSize: '.82em', fontWeight: 700, color: '#2563eb' }}>→ OCR</div>
              <div style={{ fontSize: '.78em', color: '#64748b', marginTop: 4 }}>
                Tesseract · PaddleOCR<br />Google Vision · Clova OCR
              </div>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55 }}>
            <Card borderColor="#7c3aed">
              <h4 style={{ color: '#8b5cf6' }}>✂️ 객체 분리 (누끼)</h4>
              <p style={{ fontSize: '.9em', color: '#475569', marginBottom: 8 }}>
                이미지 속 특정 객체의 윤곽을<br />픽셀 단위로 정확히 분리
              </p>
              <div style={{ fontSize: '.82em', fontWeight: 700, color: '#8b5cf6' }}>→ 세그멘테이션</div>
              <div style={{ fontSize: '.78em', color: '#64748b', marginTop: 4 }}>
                SAM (Segment Anything)<br />YOLO-seg · Mask R-CNN
              </div>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
            <Card borderColor="#059669">
              <h4 style={{ color: '#10b981' }}>🖼️ 이미지 설명 생성</h4>
              <p style={{ fontSize: '.9em', color: '#475569', marginBottom: 8 }}>
                이미지 전체 의미/맥락을<br />자연어로 설명 · 추론
              </p>
              <div style={{ fontSize: '.82em', fontWeight: 700, color: '#10b981' }}>→ VL 모델</div>
              <div style={{ fontSize: '.78em', color: '#64748b', marginTop: 4 }}>
                GPT-4V · Claude 3 · Gemini<br />Qwen-VL · LLaVA
              </div>
            </Card>
          </motion.div>
        </Grid>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}>
          <div style={{
            marginTop: 20, padding: '14px 22px', borderRadius: 10,
            background: '#fffbeb', border: '1px solid #fde68a',
            fontSize: '.88em', color: '#92400e', lineHeight: 1.7,
          }}>
            💡 솔루션을 고르기 전에 <strong>문제를 쪼개는 것</strong>이 먼저입니다.
            "이미지 처리해줘"를 "무엇을, 어떤 형태로, 얼마나 정확하게" 원하는지로 바꾸면
            엔지니어링 난이도와 비용이 10배 이상 달라질 수 있습니다.
          </div>
        </motion.div>
      </div>
    </div>
  );
}

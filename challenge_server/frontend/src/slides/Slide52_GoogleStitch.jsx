import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box } from './SlideLayout';

const features = [
  { icon: '💬', title: 'Text → UI', desc: '텍스트로 설명하면 UI 디자인 생성', color: '#3b82f6' },
  { icon: '✏️', title: 'Sketch → UI', desc: '손그림/와이어프레임 업로드 → 디지털 변환', color: '#059669' },
  { icon: '🎤', title: 'Voice Canvas', desc: '음성으로 디자인 피드백, 실시간 수정', color: '#d97706' },
  { icon: '🔗', title: 'Stitch Flow', desc: '화면 연결 → 인터랙티브 프로토타입', color: '#7c3aed' },
  { icon: '📤', title: 'Export', desc: 'Figma 내보내기 / 프론트엔드 코드 생성', color: '#dc2626' },
  { icon: '🆓', title: 'Free', desc: '무료 사용, 가입 없이 바로 시작', color: '#0891b2' },
];

export default function Slide52_GoogleStitch() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Google Stitch</Badge>
        <SlideH2>Google Stitch — AI 네이티브 디자인 캔버스</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ textAlign: 'center', marginBottom: 16 }}>
          <code style={{ fontSize: '1.1em', padding: '6px 16px', background: '#f1f5f9', borderRadius: 8,
            color: '#2563eb', fontWeight: 600 }}>
            stitch.withgoogle.com
          </code>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
          {features.map((f, i) => (
            <motion.div key={f.title}
              initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
              style={{
                padding: '16px 14px', borderRadius: 12, textAlign: 'center',
                background: `${f.color}08`, border: `1.5px solid ${f.color}25`,
              }}>
              <div style={{ fontSize: '1.6em', marginBottom: 6 }}>{f.icon}</div>
              <div style={{ fontWeight: 700, fontSize: '.9em', color: f.color, marginBottom: 4 }}>{f.title}</div>
              <div style={{ fontSize: '.78em', color: '#64748b', lineHeight: 1.4 }}>{f.desc}</div>
            </motion.div>
          ))}
        </div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}>
          <Box color="blue" style={{ marginTop: 12, fontSize: '.92em' }}>
            <strong>Gemini 2.5 Flash</strong> (350회/월) 또는 <strong>Gemini 2.5 Pro</strong> (50회/월) 선택 가능
          </Box>
        </motion.div>
      </div>
    </div>
  );
}

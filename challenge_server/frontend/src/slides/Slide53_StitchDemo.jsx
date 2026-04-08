import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box } from './SlideLayout';

const steps = [
  { num: '1', title: '아이디어 입력', desc: '"쇼핑몰 메인 페이지, 미니멀 디자인, 다크 모드"', icon: '💡' },
  { num: '2', title: 'AI가 디자인 생성', desc: 'Gemini가 레이아웃, 색상, 타이포 자동 결정', icon: '🎨' },
  { num: '3', title: '음성으로 수정', desc: '"메뉴를 3개로 줄여줘", "색상을 더 밝게"', icon: '🎤' },
  { num: '4', title: '화면 연결 & 프로토타입', desc: '여러 화면을 Stitch → 인터랙티브 플로우', icon: '🔗' },
  { num: '5', title: '코드 또는 Figma 내보내기', desc: 'HTML/CSS/JS 코드 또는 Figma 파일', icon: '📦' },
];

export default function Slide53_StitchDemo() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Google Stitch</Badge>
        <SlideH2>Stitch 워크플로우</SlideH2>
        <Divider />

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
          {steps.map((s, i) => (
            <motion.div key={s.num}
              initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 + i * 0.12 }}
              style={{
                display: 'flex', alignItems: 'center', gap: 16,
                padding: '14px 20px', borderRadius: 12,
                background: i === steps.length - 1 ? 'rgba(5,150,105,.06)' : '#fafbfc',
                border: `1.5px solid ${i === steps.length - 1 ? '#059669' : '#e2e8f0'}`,
              }}>
              <div style={{
                width: 40, height: 40, borderRadius: '50%', display: 'flex',
                alignItems: 'center', justifyContent: 'center', fontSize: '1.3em',
                background: 'rgba(124,58,237,.1)', flexShrink: 0,
              }}>{s.icon}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: '.95em', color: '#1e293b' }}>
                  <span style={{ color: '#7c3aed', marginRight: 6 }}>Step {s.num}</span>
                  {s.title}
                </div>
                <div style={{ fontSize: '.82em', color: '#64748b', marginTop: 2 }}>{s.desc}</div>
              </div>
              {i < steps.length - 1 && (
                <div style={{ color: '#cbd5e1', fontSize: '1.2em', flexShrink: 0 }}>→</div>
              )}
            </motion.div>
          ))}
        </div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}>
          <Box color="green" style={{ marginTop: 12, textAlign: 'center', fontSize: '1em' }}>
            <strong>라이브 데모:</strong> 지금 바로 <code>stitch.withgoogle.com</code> 에서 해봅시다!
          </Box>
        </motion.div>
      </div>
    </div>
  );
}

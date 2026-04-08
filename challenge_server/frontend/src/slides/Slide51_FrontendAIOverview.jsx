import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Grid, Box, BoxTitle } from './SlideLayout';

const timeline = [
  { year: '2023', label: '수동 코딩', desc: 'Figma → 개발자가 HTML/CSS 수작업', color: '#94a3b8' },
  { year: '2024', label: 'AI 코드 생성', desc: 'Copilot, Cursor로 코드 보조', color: '#3b82f6' },
  { year: '2025', label: 'AI 디자인+코드', desc: 'v0, Bolt로 프롬프트→UI 생성', color: '#7c3aed' },
  { year: '2026', label: 'AI 네이티브', desc: 'Stitch: 말하면 디자인, 코드, 프로토타입', color: '#059669' },
];

export default function Slide51_FrontendAIOverview() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Frontend AI</Badge>
        <SlideH2>프론트엔드 개발의 진화</SlideH2>
        <Divider />

        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
          style={{ fontSize: '1.05em', color: '#475569', marginBottom: 20 }}>
          <strong>디자인 → 코드</strong>의 경계가 사라지고 있습니다.<br />
          이제 <strong style={{ color: '#7c3aed' }}>말이나 스케치</strong>만으로 완성된 UI를 만들 수 있습니다.
        </motion.p>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
          {timeline.map((t, i) => (
            <motion.div key={t.year}
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.15 }}
              style={{
                flex: 1, padding: '18px 14px', borderRadius: 12, textAlign: 'center',
                background: `${t.color}08`, border: `2px solid ${t.color}30`,
                position: 'relative',
              }}>
              <div style={{ fontSize: '1.4em', fontWeight: 900, color: t.color }}>{t.year}</div>
              <div style={{ fontWeight: 700, fontSize: '.9em', color: '#1e293b', margin: '6px 0 4px' }}>{t.label}</div>
              <div style={{ fontSize: '.78em', color: '#64748b', lineHeight: 1.4 }}>{t.desc}</div>
            </motion.div>
          ))}
        </div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}>
          <Box color="purple" style={{ marginTop: 16, textAlign: 'center', fontSize: '1em' }}>
            <strong>핵심 질문:</strong> 이 도구들을 <strong>우리 조직에서 어떻게 활용</strong>할 수 있을까?
          </Box>
        </motion.div>
      </div>
    </div>
  );
}

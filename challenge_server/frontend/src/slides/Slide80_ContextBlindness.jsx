import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';

export default function Slide80_ContextBlindness() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Context Engineering</Badge>
        <SlideH2>Context Blindness란?</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="red" style={{ fontSize: '1.05em', padding: '20px 28px' }}>
            LLM은 긴 문서를 넣어도 <strong>중간 부분을 놓칩니다.</strong><br />
            이것을 <strong style={{ color: '#dc2626' }}>Lost in the Middle</strong> 현상이라고 합니다.
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          style={{ display: 'flex', gap: 12, marginTop: 12 }}>
          {[
            { pos: '앞부분', pct: '95%', color: '#22c55e', desc: '잘 기억' },
            { pos: '중간부분', pct: '60%', color: '#ef4444', desc: '자주 놓침' },
            { pos: '뒷부분', pct: '90%', color: '#3b82f6', desc: '비교적 기억' },
          ].map((item, i) => (
            <motion.div key={item.pos}
              initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 + i * 0.15 }}
              style={{
                flex: 1, padding: '16px 14px', borderRadius: 12, textAlign: 'center',
                background: `${item.color}10`, border: `2px solid ${item.color}30`,
              }}>
              <div style={{ fontSize: '1.8em', fontWeight: 900, color: item.color }}>{item.pct}</div>
              <div style={{ fontWeight: 700, fontSize: '.9em', marginTop: 4 }}>{item.pos}</div>
              <div style={{ fontSize: '.78em', color: '#64748b' }}>{item.desc}</div>
            </motion.div>
          ))}
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}>
          <Box color="blue" style={{ marginTop: 12, fontSize: '.95em' }}>
            <strong>해결법:</strong> 긴 문서를 그대로 넣지 말고, <strong style={{ color: '#2563eb' }}>핵심만 압축</strong>하여 넣으세요.<br />
            뭘 남기고 뭘 버릴지 — 이것이 <strong>Context Engineering</strong>의 핵심입니다.
          </Box>
        </motion.div>
      </div>
    </div>
  );
}

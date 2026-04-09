import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box } from './SlideLayout';

export default function Slide82_FewshotTheory() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Context Engineering</Badge>
        <SlideH2>Few-shot Learning — 예시의 힘</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ display: 'flex', gap: 14, marginTop: 8 }}>
          {[
            { title: 'Zero-shot', desc: '예시 없이 지시만', acc: '60~70%', color: '#ef4444',
              ex: 'System: "분류하세요"\nUser: "배송 느려요"\n→ ???' },
            { title: 'One-shot', desc: '예시 1개', acc: '75~85%', color: '#f59e0b',
              ex: 'System: "분류하세요"\nUser: "좋아요" → 만족\nUser: "느려요"\n→ 불만 ✓' },
            { title: 'Few-shot', desc: '예시 3~5개', acc: '90%+', color: '#22c55e',
              ex: 'System: "분류하세요"\n3개 예시...\nUser: "느려요"\n→ 불만 ✓✓' },
          ].map((item, i) => (
            <motion.div key={item.title}
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.15 }}
              style={{
                flex: 1, padding: '18px 16px', borderRadius: 12, textAlign: 'center',
                background: `${item.color}08`, border: `2px solid ${item.color}25`,
              }}>
              <div style={{ fontSize: '1.2em', fontWeight: 900, color: item.color }}>{item.title}</div>
              <div style={{ fontSize: '.82em', color: '#64748b', margin: '4px 0' }}>{item.desc}</div>
              <div style={{ fontSize: '1.4em', fontWeight: 900, color: item.color }}>{item.acc}</div>
              <pre style={{
                marginTop: 10, padding: 8, borderRadius: 6, background: 'rgba(0,0,0,.04)',
                fontSize: '.7em', textAlign: 'left', lineHeight: 1.5, whiteSpace: 'pre-wrap',
                color: '#475569',
              }}>{item.ex}</pre>
            </motion.div>
          ))}
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
          <Box color="blue" style={{ marginTop: 12, fontSize: '.95em' }}>
            <strong>핵심:</strong> 예시의 <strong>수</strong>보다 <strong>질</strong>이 중요합니다.
            잘 고른 1~2개가 대충 고른 10개보다 낫습니다.
          </Box>
        </motion.div>
      </div>
    </div>
  );
}

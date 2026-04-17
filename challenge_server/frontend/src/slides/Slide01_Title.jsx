import { motion } from 'framer-motion';

const tags = [
  { label: 'Tool Calling', color: '#1d4ed8', bg: 'rgba(29,78,216,.08)' },
  { label: 'MCP', color: '#0f766e', bg: 'rgba(15,118,110,.08)' },
  { label: 'Agentic Loop', color: '#0b5cad', bg: 'rgba(11,92,173,.08)' },
  { label: 'Harness', color: '#b45309', bg: 'rgba(180,83,9,.08)' },
];

export default function Slide01_Title() {
  return (
    <div className="slide-container" style={{ paddingTop: 64 }}>
      <div className="slide-inner" style={{ maxWidth: 1180 }}>
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 12,
            padding: '10px 16px',
            borderRadius: 999,
            border: '1px solid rgba(88,72,49,.12)',
            background: 'rgba(255,255,255,.74)',
            boxShadow: '0 10px 26px rgba(23,34,51,.08)',
            marginBottom: 14,
          }}
        >
          <span style={{ fontSize: '.72em', color: '#b45309', letterSpacing: 2.4, fontWeight: 800, textTransform: 'uppercase' }}>
            AI Agent Workshop
          </span>
          <span style={{ width: 1, height: 14, background: 'rgba(88,72,49,.14)' }} />
          <span style={{ fontSize: '.78em', color: '#55606f', fontWeight: 700 }}>
            Intranet Workshop Deck
          </span>
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          style={{ fontSize: '.84em', color: '#7a8697', letterSpacing: 2.8, textTransform: 'uppercase', marginBottom: 10, fontWeight: 800 }}
        >
          2-Day Intensive Workshop
        </motion.p>

        <motion.h1
          className="slide-title"
          initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ fontSize: '3.5em' }}
        >
          LLM Agent 개발 실습
        </motion.h1>

        <motion.div className="slide-divider" initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ delay: 0.3 }} />

        <motion.p
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
          style={{ fontSize: '1.16em', color: '#182230', fontWeight: 700 }}
        >
          원리 이해 · 실습 중심 · 경량 구현
        </motion.p>

        <motion.p
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
          style={{ fontSize: '1.02em', color: '#55606f', marginTop: 8, maxWidth: 760, marginInline: 'auto', lineHeight: 1.8 }}
        >
          어떤 프레임워크를 쓸지 외우는 수업이 아니라, 왜 그런 아이디어가 나왔는지 이해하고
          우리 조직에 맞게 작게 구현하는 능력을 기르는 수업입니다.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}
          style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap', marginTop: 34 }}
        >
          {tags.map((t, i) => (
            <motion.span
              key={t.label}
              initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.7 + i * 0.1 }}
              style={{
                padding: '10px 18px', borderRadius: 999, background: t.bg,
                border: `1px solid ${t.color}26`, fontSize: '.88em', color: t.color, fontWeight: 800,
                boxShadow: '0 8px 18px rgba(23,34,51,.05)',
              }}
            >
              {t.label}
            </motion.span>
          ))}
        </motion.div>
      </div>
    </div>
  );
}

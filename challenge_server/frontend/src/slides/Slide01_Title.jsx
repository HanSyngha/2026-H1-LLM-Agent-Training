import { motion } from 'framer-motion';

const tags = [
  { label: 'Tool Calling', color: '#1d4ed8', bg: 'rgba(37,99,235,.08)' },
  { label: 'MCP', color: '#6d28d9', bg: 'rgba(124,58,237,.08)' },
  { label: 'Agentic Loop', color: '#047857', bg: 'rgba(5,150,105,.08)' },
  { label: 'Harness', color: '#92400e', bg: 'rgba(245,158,11,.08)' },
];

export default function Slide01_Title() {
  return (
    <div className="slide-container" style={{ paddingTop: 80 }}>
      <div className="slide-inner">
        <motion.p
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          style={{ fontSize: '.9em', color: '#94a3b8', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 8 }}
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
          style={{ fontSize: '1.2em', color: '#1e293b' }}
        >
          2일 과정 &bull; 실습 중심 &bull; 원리 이해
        </motion.p>

        <motion.p
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
          style={{ fontSize: '1em', color: '#475569', fontStyle: 'italic', marginTop: 4 }}
        >
          "어떤 기술을 배울 것인가"가 아니라, "기술의 효용성을 평가하는 방법"을 배웁니다
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}
          style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap', marginTop: 32 }}
        >
          {tags.map((t, i) => (
            <motion.span
              key={t.label}
              initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.7 + i * 0.1 }}
              style={{
                padding: '8px 20px', borderRadius: 20, background: t.bg,
                border: `1px solid ${t.color}30`, fontSize: '.95em', color: t.color, fontWeight: 600,
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

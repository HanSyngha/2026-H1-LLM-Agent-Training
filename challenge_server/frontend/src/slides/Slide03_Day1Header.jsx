import { motion } from 'framer-motion';

const tags = ['SSO', '프롬프트', 'API', 'Structured Output', 'MCP', '브라우저 자동화'];

export default function Slide03_Day1Header() {
  return (
    <div className="slide-day-header">
      <motion.div
        className="day-bg-number"
        animate={{ opacity: [0.03, 0.06, 0.03], scale: [1, 1.02, 1] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      >
        1
      </motion.div>

      <div style={{ position: 'relative', zIndex: 1 }}>
        <motion.div className="day-label" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          DAY 1
        </motion.div>

        <motion.div className="day-title" initial={{ opacity: 0, scale: 0.85, y: 30 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ delay: 0.2, duration: 0.8 }}>
          기초 이해
        </motion.div>

        <motion.div
          className="day-sub"
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          style={{ background: 'linear-gradient(135deg, #06b6d4, #3b82f6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}
        >
          LLM 제어 + Tool 개념
        </motion.div>

        <motion.div style={{ width: 80, height: 3, background: 'linear-gradient(90deg, #3b82f6, #06b6d4)', margin: '20px auto', borderRadius: 2 }}
          initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ delay: 0.5 }} />

        <motion.div className="day-desc" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
          각 기술이 <strong style={{ color: '#60a5fa' }}>왜 만들어졌는지</strong> 이해하고, 핵심 아이디어를 추출하는 능력을 기릅니다
        </motion.div>

        <motion.div className="day-tags" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
          {tags.map((t, i) => (
            <motion.span key={t} className="day-tag"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 + i * 0.08 }}>
              {t}
            </motion.span>
          ))}
        </motion.div>
      </div>

      {/* 라이트 스트릭 효과 */}
      <motion.div
        style={{
          position: 'absolute', top: 0, left: '-100%', width: '100%', height: '100%',
          background: 'linear-gradient(105deg, transparent 40%, rgba(96,165,250,.04) 45%, rgba(167,139,250,.06) 50%, transparent 60%)',
          zIndex: 0, pointerEvents: 'none',
        }}
        animate={{ left: ['−100%', '100%'] }}
        transition={{ delay: 0.3, duration: 1.8, ease: 'easeOut' }}
      />
    </div>
  );
}

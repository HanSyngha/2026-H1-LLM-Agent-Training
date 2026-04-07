import { motion } from 'framer-motion';

const tags = ['Framework', 'Agentic Loop', 'bash Agent', 'Vector DB', '하네스', '종합 실습'];

export default function Slide50_Day2Header() {
  return (
    <div className="slide-day-header">
      <motion.div
        className="day-bg-number"
        animate={{ opacity: [0.03, 0.06, 0.03], scale: [1, 1.02, 1] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      >
        2
      </motion.div>

      <div style={{ position: 'relative', zIndex: 1 }}>
        <motion.div className="day-label" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          DAY 2
        </motion.div>

        <motion.div className="day-title" initial={{ opacity: 0, scale: 0.85, y: 30 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ delay: 0.2, duration: 0.8 }}
          style={{ background: 'linear-gradient(135deg, #a78bfa, #10b981, #06b6d4)', backgroundSize: '200% 200%', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Agent 아키텍처
        </motion.div>

        <motion.div
          className="day-sub"
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          style={{ background: 'linear-gradient(135deg, #10b981, #06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}
        >
          실전 구현
        </motion.div>

        <motion.div style={{ width: 80, height: 3, background: 'linear-gradient(90deg, #8b5cf6, #10b981)', margin: '20px auto', borderRadius: 2 }}
          initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ delay: 0.5 }} />

        <motion.div className="day-desc" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
          프레임워크를 직접 써보고, <strong style={{ color: '#34d399' }}>핵심 아이디어만 추출</strong>하여 경량 구현합니다
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
          background: 'linear-gradient(105deg, transparent 40%, rgba(167,139,250,.04) 45%, rgba(16,185,129,.06) 50%, transparent 60%)',
          zIndex: 0, pointerEvents: 'none',
        }}
        animate={{ left: ['-100%', '100%'] }}
        transition={{ delay: 0.3, duration: 1.8, ease: 'easeOut' }}
      />
    </div>
  );
}

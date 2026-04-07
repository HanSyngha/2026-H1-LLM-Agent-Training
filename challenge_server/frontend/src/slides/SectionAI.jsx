import { motion } from 'framer-motion';

export default function SectionAI() {
  return (
    <div className="slide-section-header" style={{ '--section-color': '#f59e0b' }}>
      <div style={{ maxWidth: 900, width: '100%', textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
        <motion.div className="section-number" initial={{ opacity: 0, scale: 0.4, rotate: -10 }} animate={{ opacity: 1, scale: 1, rotate: 0 }} transition={{ delay: 0.15, duration: 0.6, type: 'spring' }}>
          #2
        </motion.div>
        <motion.div className="section-title" initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2, duration: 0.55 }}>
          AI '학습'이란?
        </motion.div>
        <motion.div className="section-subtitle" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4, duration: 0.5 }}>
          학습의 모호성 제거, 사내 AI의 실체
        </motion.div>
        <motion.div className="section-time" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55, duration: 0.5 }}>
          09:40 - 10:00
        </motion.div>
      </div>
    </div>
  );
}

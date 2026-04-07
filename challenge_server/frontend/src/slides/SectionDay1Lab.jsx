import { motion } from 'framer-motion';

export default function SectionDay1Lab() {
  return (
    <div className="slide-section-header" style={{ '--section-color': '#0891b2' }}>
      <div style={{ maxWidth: 900, width: '100%', textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
        <motion.div className="section-number" initial={{ opacity: 0, scale: 0.4, rotate: -10 }} animate={{ opacity: 1, scale: 1, rotate: 0 }} transition={{ delay: 0.15, duration: 0.6, type: 'spring' }}
          style={{ borderStyle: 'dashed' }}
        >
          !
        </motion.div>
        <motion.div className="section-title" initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2, duration: 0.55 }}>
          Day 1 실습 과제
        </motion.div>
        <motion.div className="section-subtitle" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4, duration: 0.5 }}>
          오늘 배운 내용을 직접 구현해 보겠습니다
        </motion.div>
        <motion.div className="section-time" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55, duration: 0.5 }}>
          16:30 -
        </motion.div>
      </div>
    </div>
  );
}

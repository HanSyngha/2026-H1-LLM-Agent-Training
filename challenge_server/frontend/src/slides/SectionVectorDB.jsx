import { motion } from 'framer-motion';

export default function SectionVectorDB() {
  return (
    <div className="slide-section-header" style={{ '--section-color': '#059669' }}>
      <div style={{ maxWidth: 900, width: '100%', textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
        <motion.div className="section-number" initial={{ opacity: 0, scale: 0.4, rotate: -10 }} animate={{ opacity: 1, scale: 1, rotate: 0 }} transition={{ delay: 0.15, duration: 0.6, type: 'spring' }}>
          #11
        </motion.div>
        <motion.div className="section-title" initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2, duration: 0.55 }}>
          Vector DB vs Index Explore
        </motion.div>
        <motion.div className="section-subtitle" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4, duration: 0.5 }}>
          Semantic Search vs Claude Code 방식
        </motion.div>
        <motion.div className="section-time" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55, duration: 0.5 }}>
          13:00 - 14:00
        </motion.div>
      </div>
    </div>
  );
}

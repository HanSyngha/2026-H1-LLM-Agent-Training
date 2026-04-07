import { motion } from 'framer-motion';

export default function SectionBash() {
  return (
    <div className="slide-section-header" style={{ '--section-color': '#f59e0b' }}>
      <div style={{ maxWidth: 900, width: '100%', textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
        <motion.div className="section-number" initial={{ opacity: 0, scale: 0.4, rotate: -10 }} animate={{ opacity: 1, scale: 1, rotate: 0 }} transition={{ delay: 0.15, duration: 0.6, type: 'spring' }}>
          #10
        </motion.div>
        <motion.div className="section-title" initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2, duration: 0.55 }}>
          bash/powershell Agent
        </motion.div>
        <motion.div className="section-subtitle" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4, duration: 0.5 }}>
          CLI로 환경을 제어하는 Agent
        </motion.div>
        <motion.div className="section-time" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55, duration: 0.5 }}>
          11:15 - 12:00
        </motion.div>
      </div>
    </div>
  );
}

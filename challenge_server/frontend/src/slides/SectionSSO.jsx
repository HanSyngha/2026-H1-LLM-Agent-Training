import { motion } from 'framer-motion';

export default function SectionSSO() {
  return (
    <div className="slide-section-header" style={{ '--section-color': '#64748b' }}>
      <div style={{ maxWidth: 900, width: '100%', textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
        <motion.div className="section-number" initial={{ opacity: 0, scale: 0.4, rotate: -10 }} animate={{ opacity: 1, scale: 1, rotate: 0 }} transition={{ delay: 0.15, duration: 0.6, type: 'spring' }}>
          #0
        </motion.div>
        <motion.div className="section-title" initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2, duration: 0.55 }}>
          SSO란?
        </motion.div>
        <motion.div className="section-subtitle" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4, duration: 0.5 }}>
          Single Sign-On 개념과 사내 연동
        </motion.div>
        <motion.div className="section-time" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55, duration: 0.5 }}>
          09:00 - 09:40
        </motion.div>
      </div>
    </div>
  );
}

import { motion } from 'framer-motion';

export default function SectionContextEng() {
  return (
    <div className="slide-container" style={{ background: '#0f172a', '--section-color': '#f59e0b' }}>
      <div className="slide-inner" style={{ textAlign: 'center', justifyContent: 'center' }}>
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6 }}>
          <div style={{ fontSize: '1.2em', color: '#f59e0b', fontWeight: 700, letterSpacing: 2, marginBottom: 12 }}>#8</div>
          <h1 style={{ fontSize: '2.4em', fontWeight: 900, color: '#f1f5f9', lineHeight: 1.2, marginBottom: 16 }}>
            Context Engineering
          </h1>
          <p style={{ fontSize: '1.15em', color: '#94a3b8', lineHeight: 1.6 }}>
            LLM에게 무엇을 넣고, 무엇을 뺄 것인가
          </p>
        </motion.div>
      </div>
    </div>
  );
}

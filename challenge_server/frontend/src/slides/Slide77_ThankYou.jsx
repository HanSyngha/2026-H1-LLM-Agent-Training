import { motion } from 'framer-motion';
import { Divider } from './SlideLayout';

export default function Slide77_ThankYou() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <motion.div
          initial={{ opacity: 0, scale: 0.85, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.8 }}
          style={{
            fontSize: '4em',
            fontWeight: 800,
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6, #0891b2)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            lineHeight: 1.2,
          }}
        >
          감사합니다
        </motion.div>

        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          style={{
            width: 80,
            height: 3,
            background: 'linear-gradient(90deg, #2563eb, #7c3aed, #0891b2)',
            margin: '1em auto',
            borderRadius: 2,
          }}
        />

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          style={{ fontSize: '1.2em', color: '#334155', marginTop: '.8em' }}
        >
          질문은 언제든 환영합니다
        </motion.p>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          style={{ marginTop: '2.5em', color: '#64748b', fontSize: '.88em' }}
        >
          LLM Agent 개발 실습 — 2일 과정
        </motion.p>
      </div>
    </div>
  );
}

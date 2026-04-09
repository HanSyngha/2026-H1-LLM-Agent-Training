import { useState } from 'react';
import { motion } from 'framer-motion';
import { postJSON } from '../api';

export default function Slide77_ThankYou() {
  const [text, setText] = useState('');
  const [rating, setRating] = useState(0);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (!text.trim()) return;
    try {
      await postJSON('/feedback', { text, rating });
      setSubmitted(true);
    } catch {}
  };

  return (
    <div className="slide-container">
      <div className="slide-inner">
        <motion.div
          initial={{ opacity: 0, scale: 0.85, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.8 }}
          style={{
            fontSize: '3.5em', fontWeight: 800,
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6, #0891b2)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            lineHeight: 1.2,
          }}>
          감사합니다
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
          style={{ marginTop: 24, maxWidth: 500, width: '100%' }}>
          {submitted ? (
            <div style={{ padding: 20, borderRadius: 12, background: '#f0fdf4', border: '1px solid #86efac', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5em', marginBottom: 4 }}>🙏</div>
              <div style={{ fontWeight: 700, color: '#059669' }}>피드백 감사합니다!</div>
            </div>
          ) : (
            <div style={{ padding: 20, borderRadius: 12, background: '#f8fafc', border: '1px solid #e2e8f0' }}>
              <div style={{ fontWeight: 700, fontSize: '.9em', color: '#475569', marginBottom: 8 }}>
                강의 피드백을 남겨주세요
              </div>
              <div style={{ display: 'flex', gap: 4, marginBottom: 10, justifyContent: 'center' }}>
                {[1,2,3,4,5].map(n => (
                  <button key={n} onClick={() => setRating(n)}
                    style={{
                      fontSize: '1.5em', background: 'none', border: 'none', cursor: 'pointer',
                      filter: n <= rating ? 'none' : 'grayscale(1) opacity(0.3)',
                    }}>⭐</button>
                ))}
              </div>
              <textarea value={text} onChange={e => setText(e.target.value)}
                placeholder="좋았던 점, 아쉬운 점, 개선할 점을 자유롭게 적어주세요..."
                style={{
                  width: '100%', height: 80, padding: 10, borderRadius: 8,
                  border: '1px solid #d1d5db', fontSize: '.88em', resize: 'none',
                  fontFamily: 'inherit',
                }} />
              <button onClick={handleSubmit} disabled={!text.trim()}
                style={{
                  marginTop: 8, padding: '8px 20px', borderRadius: 8, border: 'none',
                  width: '100%',
                  background: text.trim() ? '#2563eb' : '#e2e8f0',
                  color: text.trim() ? '#fff' : '#94a3b8',
                  fontWeight: 700, cursor: text.trim() ? 'pointer' : 'default',
                }}>피드백 제출</button>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}

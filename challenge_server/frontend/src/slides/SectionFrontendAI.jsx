import { motion } from 'framer-motion';

export default function SectionFrontendAI() {
  return (
    <div className="slide-container" style={{ background: '#182230', '--section-color': '#b45309' }}>
      <div className="slide-inner" style={{ textAlign: 'center', justifyContent: 'center' }}>
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6 }}>
          <div style={{ fontSize: '1.2em', color: '#f3be7a', fontWeight: 800, letterSpacing: 2.4, marginBottom: 12 }}>#8</div>
          <h1 style={{ fontSize: '2.4em', fontWeight: 900, color: '#f1f5f9', lineHeight: 1.2, marginBottom: 16 }}>
            Frontend AI Design
          </h1>
          <p style={{ fontSize: '1.12em', color: 'rgba(241,245,249,.72)', lineHeight: 1.8 }}>
            생성형 UI 도구를 맹신하지 않고, 정보 구조와 제품 감각을 빠르게 시각화하는 법
          </p>
          <div style={{ marginTop: 24, display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            {['Google Stitch', 'v0', 'Bolt', 'Lovable'].map(tool => (
              <span key={tool} style={{
                padding: '8px 16px', borderRadius: 999, fontSize: '.82em', fontWeight: 700,
                background: 'rgba(255,255,255,.06)', color: '#f6dcc0', border: '1px solid rgba(255,255,255,.12)',
              }}>{tool}</span>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}

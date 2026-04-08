import { motion } from 'framer-motion';

export default function SectionFrontendAI() {
  return (
    <div className="slide-container" style={{ background: '#0f172a', '--section-color': '#7c3aed' }}>
      <div className="slide-inner" style={{ textAlign: 'center', justifyContent: 'center' }}>
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6 }}>
          <div style={{ fontSize: '1.2em', color: '#7c3aed', fontWeight: 700, letterSpacing: 2, marginBottom: 12 }}>#8</div>
          <h1 style={{ fontSize: '2.4em', fontWeight: 900, color: '#f1f5f9', lineHeight: 1.2, marginBottom: 16 }}>
            Frontend AI Design
          </h1>
          <p style={{ fontSize: '1.15em', color: '#94a3b8', lineHeight: 1.6 }}>
            AI로 UI/UX를 디자인하고 코드를 생성하는 시대
          </p>
          <div style={{ marginTop: 24, display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            {['Google Stitch', 'v0', 'Bolt', 'Lovable'].map(tool => (
              <span key={tool} style={{
                padding: '6px 16px', borderRadius: 20, fontSize: '.85em', fontWeight: 600,
                background: 'rgba(124,58,237,.15)', color: '#a78bfa', border: '1px solid rgba(124,58,237,.3)',
              }}>{tool}</span>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}

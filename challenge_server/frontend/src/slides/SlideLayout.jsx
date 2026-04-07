import { motion } from 'framer-motion';

const variants = {
  enter: { opacity: 0, x: 60 },
  center: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -60 },
};

export default function SlideLayout({ children, day, className = '' }) {
  const dayColors = {
    0: { accent: '#2563eb', bg: '#f8fafc' },
    1: { accent: '#2563eb', bg: '#f8fafc' },
    2: { accent: '#7c3aed', bg: '#f8fafc' },
  };
  const colors = dayColors[day] || dayColors[0];

  return (
    <motion.div
      className={`slide-container ${className}`}
      variants={variants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      style={{ '--day-accent': colors.accent }}
    >
      <div className="slide-inner">
        {children}
      </div>
    </motion.div>
  );
}

// 공통 컴포넌트들
export function SlideTitle({ children }) {
  return <h1 className="slide-title">{children}</h1>;
}

export function SlideH2({ children, day2 }) {
  return <h2 className={`slide-h2 ${day2 ? 'day2' : ''}`}>{children}</h2>;
}

export function Divider() {
  return <div className="slide-divider" />;
}

export function Badge({ children, variant = 'day1' }) {
  return <span className={`slide-badge ${variant}`}>{children}</span>;
}

export function Box({ children, color = 'blue', className = '', style = {} }) {
  return <div className={`slide-box ${color} ${className}`} style={style}>{children}</div>;
}

export function BoxTitle({ children, color }) {
  return <div className="slide-box-title" style={color ? { color } : {}}>{children}</div>;
}

export function Grid({ children, cols = 2, gap = 16 }) {
  return (
    <div className="slide-grid" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)`, gap }}>
      {children}
    </div>
  );
}

export function Card({ children, borderColor, style = {} }) {
  return (
    <div className="slide-card" style={{ borderTopColor: borderColor, ...style }}>
      {children}
    </div>
  );
}

export function CodeBlock({ children, lang = 'python' }) {
  return (
    <pre className="slide-code">
      <div className="code-dots"><span /><span /><span /></div>
      <code>{children}</code>
      <span className="code-lang">{lang}</span>
    </pre>
  );
}

export function Quote({ children, author, borderColor }) {
  return (
    <blockquote className="slide-quote" style={borderColor ? { borderLeftColor: borderColor } : {}}>
      {children}
      {author && <div className="slide-quote-author">— {author}</div>}
    </blockquote>
  );
}

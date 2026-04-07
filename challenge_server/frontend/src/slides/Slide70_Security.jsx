import { motion } from 'framer-motion';
import { Badge, SlideH2 } from './SlideLayout';

const layers = [
  { color: '#2563eb', label: 'Layer 1:', desc: '입력 검증 — Prompt Injection 탐지, 입력 길이 제한' },
  { color: '#059669', label: 'Layer 2:', desc: 'Tool 제한 — 허용 Tool 화이트리스트, 인자 검증' },
  { color: '#d97706', label: 'Layer 3:', desc: '실행 격리 — 샌드박스, 리소스 제한, 타임아웃' },
  { color: '#ea580c', label: 'Layer 4:', desc: '출력 필터 — PII 마스킹, 유해 콘텐츠 차단' },
  { color: '#dc2626', label: 'Layer 5:', desc: '감사 로그 — 모든 LLM 호출/Tool 실행 기록' },
];

export default function Slide70_Security() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">하네스 엔지니어링</Badge>
        <SlideH2 day2>보안 / 가드레일 5계층 방어</SlideH2>

        <div style={{ maxWidth: 720, margin: '.8em auto', textAlign: 'left' }}>
          {layers.map((layer, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.12, duration: 0.5 }}
              style={{
                background: 'rgba(255,255,255,.7)',
                backdropFilter: 'blur(16px)',
                border: '1px solid rgba(148,163,184,.25)',
                borderLeft: `3px solid ${layer.color}`,
                borderRadius: 16,
                padding: '12px 22px',
                marginBottom: i < layers.length - 1 ? '.5em' : 0,
                boxShadow: '0 2px 12px rgba(0,0,0,.06)',
              }}
            >
              <strong style={{ color: layer.color }}>{layer.label}</strong> {layer.desc}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

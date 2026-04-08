import { motion } from 'framer-motion';

const categories = [
  {
    title: 'Frontend',
    options: [
      { name: 'React', desc: '생태계 최대, 자유도 높음', color: '#61dafb' },
      { name: 'Angular', desc: '엔터프라이즈, 구조 강제', color: '#dd0031' },
      { name: 'Vue', desc: '쉬운 학습, 점진적 채택', color: '#42b883' },
    ],
  },
  {
    title: 'Backend',
    options: [
      { name: 'FastAPI', desc: 'Python, 빠른 프로토타입', color: '#009688' },
      { name: 'Django', desc: 'Python, 배터리 포함', color: '#092e20' },
      { name: 'Spring', desc: 'Java, 엔터프라이즈 표준', color: '#6db33f' },
    ],
  },
  {
    title: 'AI/프로토타입',
    options: [
      { name: 'Streamlit', desc: '데모 최강, 빠른 UI', color: '#ff4b4b' },
      { name: 'Gradio', desc: 'ML 모델 데모', color: '#f97316' },
      { name: 'Jupyter', desc: '탐색·분석·실험', color: '#f37626' },
    ],
  },
];

export default function Slide01c_TechChoices() {
  return (
    <div className="slide-container" style={{ background: '#0f172a' }}>
      <div className="slide-inner" style={{ justifyContent: 'center' }}>
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <h2 style={{ fontSize: '1.6em', fontWeight: 900, color: '#f1f5f9', textAlign: 'center', marginBottom: 8 }}>
            그래서, 무엇을 배워야 할까요?
          </h2>
          <p style={{ textAlign: 'center', color: '#64748b', fontSize: '.95em', marginBottom: 28 }}>
            "무엇이 <strong style={{ color: '#fbbf24' }}>우리 조직</strong>에 가장 최선인가"를 판단하는 것이 핵심입니다.
          </p>
        </motion.div>

        <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
          {categories.map((cat, ci) => (
            <motion.div key={cat.title}
              initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + ci * 0.2 }}
              style={{
                flex: 1, maxWidth: 280, padding: '20px 18px', borderRadius: 14,
                background: 'rgba(255,255,255,.03)', border: '1px solid rgba(255,255,255,.08)',
              }}>
              <div style={{
                fontSize: '.8em', fontWeight: 700, color: '#94a3b8',
                textTransform: 'uppercase', letterSpacing: 2, marginBottom: 14,
                textAlign: 'center',
              }}>{cat.title}</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {cat.options.map((opt, i) => (
                  <motion.div key={opt.name}
                    initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + ci * 0.2 + i * 0.1 }}
                    style={{
                      padding: '10px 14px', borderRadius: 10,
                      background: `${opt.color}10`, border: `1px solid ${opt.color}30`,
                      display: 'flex', alignItems: 'center', gap: 10,
                    }}>
                    <div style={{
                      width: 8, height: 8, borderRadius: '50%',
                      background: opt.color, flexShrink: 0,
                    }} />
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '.9em', color: opt.color }}>{opt.name}</div>
                      <div style={{ fontSize: '.72em', color: '#94a3b8' }}>{opt.desc}</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.3 }}>
          <div style={{
            marginTop: 24, padding: '16px 28px', borderRadius: 12, textAlign: 'center',
            background: 'rgba(251,191,36,.08)', border: '1px solid rgba(251,191,36,.2)',
          }}>
            <p style={{ fontSize: '1em', color: '#fbbf24', fontWeight: 700, margin: 0 }}>
              어떤 기술이 "좋다/나쁘다"가 아니라,<br />
              <span style={{ color: '#f1f5f9' }}>어떤 상황에서 어떤 선택이 최선인지</span> 판단하는 눈을 기릅시다.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

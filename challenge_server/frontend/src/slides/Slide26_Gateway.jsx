import { motion } from 'framer-motion';
import { Badge, SlideH2, Box } from './SlideLayout';

function StageCard({ title, subtitle, color, delay, children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      style={{
        flex: 1,
        minHeight: 220,
        borderRadius: 24,
        padding: '24px 22px',
        background: `${color}10`,
        border: `1px solid ${color}33`,
        boxShadow: '0 18px 44px rgba(15, 23, 42, 0.08)',
      }}
    >
      <div style={{ fontSize: '.78em', fontWeight: 800, letterSpacing: '.08em', color, textTransform: 'uppercase' }}>{title}</div>
      <div style={{ marginTop: 8, fontSize: '1.18em', fontWeight: 800, color: '#0f172a', lineHeight: 1.35 }}>{subtitle}</div>
      <div style={{ marginTop: 16, display: 'grid', gap: 10, color: '#334155', lineHeight: 1.65, fontSize: '.95em' }}>
        {children}
      </div>
    </motion.div>
  );
}

function FlowArrow({ delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.3 }}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#2563eb',
        fontSize: '1.9em',
        fontWeight: 800,
        width: 36,
      }}
    >
      →
    </motion.div>
  );
}

export default function Slide26_Gateway() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">OpenAI Compatible</Badge>
        <SlideH2>Gateway 구조</SlideH2>
        <p style={{ color: '#475569', maxWidth: 920 }}>
          OpenAI Compatible은 <strong style={{ color: '#2563eb' }}>요청 형식의 표준</strong>이고, Gateway는 그 표준 요청 위에
          <strong style={{ color: '#7c3aed' }}> 사내 인증·정책·라우팅</strong>을 얹는 계층입니다.
        </p>

        <div style={{ display: 'flex', alignItems: 'stretch', gap: 14, marginTop: 18 }}>
          <StageCard title="1. Client" subtitle="코드는 표준 SDK 그대로" color="#2563eb" delay={0.1}>
            <div><strong>OpenAI SDK</strong>나 REST 호출을 그대로 사용합니다.</div>
            <div><code>messages</code>, <code>model</code>, <code>temperature</code> 같은 표준 필드를 보냅니다.</div>
            <div>개발자는 서비스 기능에 집중하고, 모델별 특수 계약은 최소화합니다.</div>
          </StageCard>

          <FlowArrow delay={0.18} />

          <StageCard title="2. Gateway" subtitle="사내 요구사항을 여기서 처리" color="#7c3aed" delay={0.26}>
            <div><strong>x-service-id</strong>, <strong>x-user-id</strong> 같은 사내 헤더를 검사합니다.</div>
            <div>허용된 모델인지 확인하고, 로깅·권한·운영 정책을 한 곳에서 통제합니다.</div>
            <div>실제 호출 대상 OpenAI, vLLM, 내부 LLM으로 요청을 라우팅합니다.</div>
          </StageCard>

          <FlowArrow delay={0.34} />

          <StageCard title="3. Models" subtitle="뒤에는 어떤 모델이 와도 됨" color="#0f766e" delay={0.42}>
            <div>OpenAI, 사내 배포 모델, 오픈소스 LLM을 같은 계약으로 교체할 수 있습니다.</div>
            <div>앞단 코드는 유지하고, 운영 측에서 모델 선택과 전환을 관리할 수 있습니다.</div>
            <div>핵심은 framework가 아니라 <strong>표준 요청 + 중앙 라우팅</strong>입니다.</div>
          </StageCard>
        </div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55 }}>
          <Box color="blue" style={{ marginTop: 18, fontSize: '.95em' }}>
            <strong>강조할 메시지:</strong> OpenAI Compatible은 "모양을 맞추는 표준"이고, Gateway는 "사내 환경에 맞게 실행시키는 운영 계층"입니다.
          </Box>
        </motion.div>
      </div>
    </div>
  );
}

import { motion } from 'framer-motion';
import { Badge, SlideH2, Quote } from './SlideLayout';

function AnimatedBox({ x, y, w, h, fill, stroke, delay, children }) {
  return (
    <motion.g initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay, duration: 0.4 }}>
      <rect x={x} y={y} width={w} height={h} rx={12} fill={fill} stroke={stroke} strokeWidth={2} />
      {children}
    </motion.g>
  );
}

export default function Slide67_WhatIsHarness() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">하네스 엔지니어링</Badge>
        <SlideH2 day2>하네스란?</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Quote borderColor="#7c3aed" author="모델의 성능을 실제 가치로 변환하는 모든 시스템">
            "모델은 엔진이고, 하네스는 자동차다."
          </Quote>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} style={{ marginTop: 24 }}>
          <svg viewBox="0 0 900 120" width="900" height="120" className="diagram-svg">
            {/* LLM core */}
            <AnimatedBox x={40} y={20} w={160} h={80} fill="rgba(51,65,85,.1)" stroke="rgba(100,116,139,.4)" delay={0.5}>
              <text x={120} y={52} textAnchor="middle" fill="#1e293b" fontWeight={700} fontSize={16}>LLM</text>
              <text x={120} y={74} textAnchor="middle" fill="#475569" fontSize={13}>엔진</text>
            </AnimatedBox>

            {/* + */}
            <motion.text x={240} y={65} textAnchor="middle" fill="#64748b" fontSize={26} fontWeight={300}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>+</motion.text>

            {/* Harness */}
            <AnimatedBox x={280} y={10} w={260} h={95} fill="rgba(139,92,246,.08)" stroke="rgba(139,92,246,.5)" delay={0.7}>
              <text x={410} y={42} textAnchor="middle" fill="#6d28d9" fontWeight={700} fontSize={16}>하네스</text>
              <text x={410} y={64} textAnchor="middle" fill="#475569" fontSize={13}>Tool + Loop + Guard + Log</text>
              <text x={410} y={84} textAnchor="middle" fill="#475569" fontSize={13}>Context Engineering</text>
            </AnimatedBox>

            {/* = */}
            <motion.text x={585} y={65} textAnchor="middle" fill="#64748b" fontSize={26} fontWeight={300}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }}>=</motion.text>

            {/* Agent */}
            <AnimatedBox x={625} y={15} w={160} h={85} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.9}>
              <text x={705} y={50} textAnchor="middle" fill="#047857" fontWeight={700} fontSize={16}>Agent</text>
              <text x={705} y={74} textAnchor="middle" fill="#475569" fontSize={13}>실용적 시스템</text>
            </AnimatedBox>
          </svg>
        </motion.div>

        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.0 }}
          style={{ marginTop: '0.8em', fontSize: '1em' }}>
          동일한 LLM이라도 하네스 설계에 따라 <strong style={{ color: '#3b82f6' }}>성능이 완전히 달라집니다</strong>
        </motion.p>
      </div>
    </div>
  );
}

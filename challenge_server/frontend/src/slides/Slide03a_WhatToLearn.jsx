import { motion } from 'framer-motion';
import { SlideH2, Divider } from './SlideLayout';

export default function Slide03a_WhatToLearn() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          style={{ fontSize: '3em', marginBottom: 8 }}
        >
          🤔
        </motion.div>

        <motion.h1
          className="slide-title"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          style={{ fontSize: '2.8em' }}
        >
          여러분은 무엇을 배우고 싶으세요?
        </motion.h1>

        <Divider />

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          style={{ fontSize: '1.2em', color: '#475569', marginTop: 16 }}
        >
          아래 질문 입력란에 자유롭게 적어주세요
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          style={{
            marginTop: 32, padding: '24px 32px',
            background: '#f0f9ff', border: '2px dashed #93c5fd',
            borderRadius: 16, maxWidth: 600, margin: '32px auto 0',
          }}
        >
          <p style={{ color: '#2563eb', fontWeight: 600, fontSize: '1.05em', marginBottom: 8 }}>
            예시:
          </p>
          <div style={{ color: '#475569', lineHeight: 2, fontSize: '1em' }}>
            "Agent를 실무에서 어떻게 적용할 수 있는지 알고 싶습니다"<br />
            "MCP가 뭔지 아직 잘 모르겠습니다"<br />
            "바이브 코딩으로 정말 서비스를 만들 수 있나요?"<br />
            "RAG 성능을 올리는 방법이 궁금합니다"
          </div>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          style={{ fontSize: '.9em', color: '#94a3b8', marginTop: 24 }}
        >
          입력하신 내용은 화면에 실시간으로 표시됩니다 👆
        </motion.p>
      </div>
    </div>
  );
}

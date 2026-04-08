import { useState } from 'react';
import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';
import { postJSON } from '../api';
import AnswerButton from './AnswerButton';
import Slide48_BrowserAnswer from './Slide48_BrowserAnswer';

export default function Slide47_BrowserTask() {
  const [key, setKey] = useState('');
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!key.trim()) return;
    setSubmitting(true);
    try {
      const r = await postJSON('/challenges/browser/submit', { answer: { secret_key: key.trim() } });
      setResult(r);
    } catch (e) {
      setResult({ status: 'FAIL', message: e.message });
    }
    setSubmitting(false);
  };

  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">브라우저 실습</Badge>
        <SlideH2>과제: JS 렌더링 페이지에서 비밀 키 추출</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="red" style={{ marginTop: 8, fontSize: '1em', padding: '18px 28px' }}>
            <strong>주의:</strong> 이 페이지는 <strong>JavaScript로 렌더링</strong>됩니다.<br />
            <code>requests.get()</code>이나 <code>curl</code>로는 "로딩 중..."만 보입니다!
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="blue" style={{ marginTop: 8, fontSize: '.95em', padding: '20px 28px' }}>
            <BoxTitle>과제</BoxTitle>
            아래 페이지에 숨겨진 <strong>비밀 키</strong>를 프로그래밍으로 추출하세요.<br />
            <code style={{ display: 'block', margin: '10px 0', padding: '8px 14px', background: 'rgba(0,0,0,.05)', borderRadius: 6, fontSize: '.95em' }}>
              http://a2g.samsungds.net:47777/browser-target
            </code>
            키는 DOM에 숨겨져 있습니다 — 눈에 보이지 않습니다!<br />
            <span style={{ fontSize: '.85em', color: '#64748b', marginTop: 4, display: 'block' }}>
              요소 ID: <code>#secret-key</code> | Playwright, Selenium, CDP 등 자유
            </span>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="green" style={{ marginTop: 8, padding: '20px 28px' }}>
            <BoxTitle color="#059669">비밀 키 제출</BoxTitle>
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <input
                type="text" value={key} onChange={e => setKey(e.target.value)}
                placeholder="추출한 비밀 키를 입력하세요"
                onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                style={{
                  flex: 1, padding: '10px 14px', borderRadius: 8,
                  border: '1.5px solid #d1d5db', fontSize: '.95em',
                  fontFamily: 'monospace',
                }}
              />
              <button onClick={handleSubmit} disabled={submitting || !key.trim()}
                style={{
                  padding: '10px 24px', borderRadius: 8, border: 'none',
                  background: key.trim() ? '#059669' : '#e2e8f0',
                  color: key.trim() ? '#fff' : '#94a3b8',
                  fontWeight: 700, fontSize: '.9em', cursor: key.trim() ? 'pointer' : 'default',
                }}>
                {submitting ? '확인 중...' : '제출'}
              </button>
            </div>
            {result && (
              <div style={{
                marginTop: 10, padding: '10px 14px', borderRadius: 8,
                background: result.status === 'SUCCESS' ? '#f0fdf4' : '#fef2f2',
                color: result.status === 'SUCCESS' ? '#059669' : '#dc2626',
                fontWeight: 700, fontSize: '.9em',
              }}>
                {result.status === 'SUCCESS' ? `🎉 ${result.message}` : `❌ ${result.message}`}
              </div>
            )}
          </Box>
        </motion.div>

        <AnswerButton answerId="browser"><Slide48_BrowserAnswer /></AnswerButton>
      </div>
    </div>
  );
}

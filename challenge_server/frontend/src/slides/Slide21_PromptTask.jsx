import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';
import { getPromptCases, testPrompt, submitPrompt } from '../api';
import AnswerButton from './AnswerButton';
import Slide22_PromptAnswer from './Slide22_PromptAnswer';

export default function Slide21_PromptTask() {
  const [mode, setMode] = useState('info'); // 'info' or 'lab'

  return (
    <div className="slide-container" style={{ padding: '20px 40px' }}>
      <div className="slide-inner">
        <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 12 }}>
          <button onClick={() => setMode('info')}
            style={{ padding: '6px 20px', borderRadius: 20, border: mode === 'info' ? '2px solid #2563eb' : '1px solid #e2e8f0',
              background: mode === 'info' ? '#eff6ff' : '#fff', color: mode === 'info' ? '#2563eb' : '#64748b',
              fontWeight: 600, fontSize: '.88em', cursor: 'pointer' }}>
            📋 과제 설명
          </button>
          <button onClick={() => setMode('lab')}
            style={{ padding: '6px 20px', borderRadius: 20, border: mode === 'lab' ? '2px solid #059669' : '1px solid #e2e8f0',
              background: mode === 'lab' ? '#f0fdf4' : '#fff', color: mode === 'lab' ? '#059669' : '#64748b',
              fontWeight: 600, fontSize: '.88em', cursor: 'pointer' }}>
            🧪 실습하기
          </button>
        </div>

        {mode === 'info' ? <InfoMode /> : <LabMode />}
      </div>
    </div>
  );
}

function InfoMode() {
  return (
    <>
      <Badge variant="day1">프롬프트 실습</Badge>
      <SlideH2>과제: 금융 기사 실적 추출</SlideH2>
      <Divider />

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <Box color="blue" style={{ fontSize: '1em', padding: '20px 28px' }}>
          <BoxTitle>문제</BoxTitle>
          <strong>하나의 System Prompt</strong>로 10개 금융 기사에서 실적 데이터(회사명, 종목코드, 매출, 영업이익 등 10개 필드)를
          정확히 추출하세요. <strong>Exact match — 모든 값이 정확해야 PASS</strong>입니다.
        </Box>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, justifyContent: 'center', margin: '12px 0' }}>
          {['company', 'ticker', 'revenue', 'operating_profit', 'net_income',
            'stock_price', 'price_change_pct', 'consensus_op', 'eps', 'target_price'].map(f => (
            <span key={f} style={{ padding: '4px 12px', borderRadius: 16, background: '#f1f5f9', color: '#475569', fontSize: '.82em' }}>{f}</span>
          ))}
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
        <Box color="green" style={{ textAlign: 'center', fontSize: '1em' }}>
          위 <strong>"🧪 실습하기"</strong> 탭을 눌러 바로 시작하세요!
        </Box>
      </motion.div>
    </>
  );
}

function LabMode() {
  const [cases, setCases] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [results, setResults] = useState({});
  const [testing, setTesting] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [finalMsg, setFinalMsg] = useState(null);
  const abortRef = useRef(false);

  useState(() => { getPromptCases().then(setCases); }, []);

  const [submitted, setSubmitted] = useState(false);

  const runTest = async () => {
    if (!prompt.trim()) return alert('프롬프트를 입력하세요.');
    setTesting(true); setResults({}); setFinalMsg(null); setSubmitted(false);
    abortRef.current = false;
    let passed = 0;
    for (let i = 0; i < cases.length; i++) {
      if (abortRef.current) break;
      setProgress({ current: i + 1, total: cases.length });
      try {
        const r = await testPrompt(prompt, cases[i].id);
        if (abortRef.current) break;
        setResults(prev => ({ ...prev, [cases[i].id]: r }));
        if (r.pass) passed++;
      } catch (e) {
        if (abortRef.current) break;
        setResults(prev => ({ ...prev, [cases[i].id]: { pass: false, error: e.message } }));
      }
    }
    setTesting(false);

    if (abortRef.current) {
      setFinalMsg(`⏹ 중지됨 (${passed}개 통과)`);
    } else if (passed === cases.length) {
      // 10/10 전체 통과 → 자동 제출
      setFinalMsg('🎉 전체 통과! 자동 제출 중...');
      try {
        const r = await submitPrompt(prompt);
        setSubmitted(true);
        setFinalMsg(r.status === 'SUCCESS' ? `🎉 ${r.message}` : `❌ ${r.message}`);
      } catch {
        setFinalMsg('🎉 전체 통과! (제출 실패 — 다시 시도해주세요)');
      }
    } else {
      setFinalMsg(`${passed}/${cases.length} 통과`);
    }
  };

  const stopTest = () => { abortRef.current = true; };

  const allPass = Object.values(results).length === cases.length && Object.values(results).every(r => r.pass);

  return (
    <div style={{ textAlign: 'left' }}>
      <textarea
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        placeholder="금융 기사에서 실적을 추출하는 System Prompt를 작성하세요..."
        style={{ width: '100%', minHeight: 120, padding: 14, border: '1px solid #e2e8f0', borderRadius: 10,
          fontFamily: 'monospace', fontSize: '.85em', lineHeight: 1.5, resize: 'vertical' }}
      />

      <div style={{ display: 'flex', gap: 8, margin: '10px 0', alignItems: 'center' }}>
        <button onClick={runTest} disabled={testing}
          style={{ padding: '8px 20px', borderRadius: 8, background: '#2563eb', color: '#fff', border: 'none', fontWeight: 600, cursor: 'pointer', fontSize: '.88em' }}>
          {testing ? `⏳ ${progress.current}/${progress.total}` : '🧪 전체 테스트'}
        </button>
        {testing && (
          <button onClick={stopTest}
            style={{ padding: '8px 20px', borderRadius: 8, background: '#dc2626', color: '#fff', border: 'none', fontWeight: 600, cursor: 'pointer', fontSize: '.88em' }}>
            ⏹ 중지
          </button>
        )}
        {finalMsg && <span style={{ fontSize: '.88em', fontWeight: 600, color: allPass ? '#059669' : '#dc2626' }}>{finalMsg}</span>}
      </div>

      {/* 결과 그리드 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 6 }}>
        {cases.map(tc => {
          const r = results[tc.id];
          const bg = r ? (r.pass ? '#f0fdf4' : '#fef2f2') : '#f8fafc';
          const border = r ? (r.pass ? '#86efac' : '#fca5a5') : '#e2e8f0';
          return (
            <div key={tc.id} style={{ padding: 8, borderRadius: 8, border: `1px solid ${border}`, background: bg, fontSize: '.75em' }}>
              <div style={{ fontWeight: 600, marginBottom: 2 }}>#{tc.id} {tc.title}</div>
              {r ? (
                <span style={{ color: r.pass ? '#059669' : '#dc2626', fontWeight: 700 }}>{r.pass ? 'PASS' : 'FAIL'}</span>
              ) : (
                <span style={{ color: '#94a3b8' }}>대기</span>
              )}
            </div>
          );
        })}
      </div>

      <AnswerButton answerId="prompt"><Slide22_PromptAnswer /></AnswerButton>
    </div>
  );
}

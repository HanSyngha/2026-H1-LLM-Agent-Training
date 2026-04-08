import { useState } from 'react';
import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';
import { postJSON } from '../api';
import AnswerButton from './AnswerButton';
import Slide61_AgentAnswer from './Slide61_AgentAnswer';

export default function Slide60_AgentTask() {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!code.trim()) return;
    setSubmitting(true);
    try {
      const r = await postJSON('/challenges/agent_loop/submit', { answer: { completion_code: code.trim() } });
      setResult(r);
    } catch (e) {
      setResult({ status: 'FAIL', message: e.message });
    }
    setSubmitting(false);
  };

  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agentic Loop 실습</Badge>
        <SlideH2>과제: API 미로 탈출</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue">
            <BoxTitle>1단계: 코드 다운로드 & 실행</BoxTitle>
            <a href="/downloads/agent_loop" download
              style={{ display: 'inline-block', padding: '8px 20px', borderRadius: 8, background: '#2563eb', color: '#fff',
                textDecoration: 'none', fontWeight: 600, fontSize: '.9em', marginBottom: 8 }}>
              📦 실습 코드 다운로드
            </a>
            <code style={{ display: 'block', fontSize: '1em', lineHeight: 1.8 }}>
              pip install streamlit requests PyJWT<br />
              streamlit run app.py --server.port 3000
            </code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="red" style={{ marginTop: 8 }}>
            <BoxTitle color="#dc2626">API 미로 규칙</BoxTitle>
            <div style={{ fontSize: '.9em', lineHeight: 1.8 }}>
              <code>start</code> → 랜덤 3개 스텝 순서 안내 (예: step3 → step7 → step1)<br />
              <code>step/N</code> → 순서대로 호출해야 통과, <strong style={{ color: '#dc2626' }}>틀리면 초기화!</strong><br />
              <code>end</code> → 3개 완료 후 호출 → <strong>completion_code</strong> 획득
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.82em', padding: '16px 24px' }}>
            <BoxTitle color="#d97706">TODO: run_agentic_loop() — while 루프</BoxTitle>
            <div style={{ lineHeight: 1.8 }}>
              1. <code>result, error = call_llm(messages)</code> 호출<br />
              2. <code>msg = result["choices"][0]["message"]</code><br />
              3. <code>msg["tool_calls"]</code> 없으면 → <code>msg["content"]</code> 반환 (종료)<br />
              4. <code>tool_calls</code> 있으면:<br />
              &nbsp;&nbsp;a. <code>messages.append(msg)</code> — assistant 메시지 추가<br />
              &nbsp;&nbsp;b. 각 tool_call: <code>execute_tool(name, args)</code> 실행<br />
              &nbsp;&nbsp;c. <code>{'messages.append({"role":"tool","tool_call_id":tc["id"],"content":json.dumps(result)})'}</code><br />
              &nbsp;&nbsp;d. 루프 계속 (다시 1번으로)
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }}>
          <Box color="green" style={{ marginTop: 8, padding: '20px 28px' }}>
            <BoxTitle color="#059669">Completion Code 제출</BoxTitle>
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <input type="text" value={code} onChange={e => setCode(e.target.value)}
                placeholder="completion_code를 입력하세요"
                onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                style={{ flex: 1, padding: '10px 14px', borderRadius: 8, border: '1.5px solid #d1d5db',
                  fontSize: '.95em', fontFamily: 'monospace' }} />
              <button onClick={handleSubmit} disabled={submitting || !code.trim()}
                style={{ padding: '10px 24px', borderRadius: 8, border: 'none',
                  background: code.trim() ? '#059669' : '#e2e8f0',
                  color: code.trim() ? '#fff' : '#94a3b8',
                  fontWeight: 700, fontSize: '.9em', cursor: code.trim() ? 'pointer' : 'default' }}>
                {submitting ? '확인 중...' : '제출'}
              </button>
            </div>
            {result && (
              <div style={{ marginTop: 10, padding: '10px 14px', borderRadius: 8,
                background: result.status === 'SUCCESS' ? '#f0fdf4' : '#fef2f2',
                color: result.status === 'SUCCESS' ? '#059669' : '#dc2626',
                fontWeight: 700, fontSize: '.9em' }}>
                {result.status === 'SUCCESS' ? `🎉 ${result.message}` : `❌ ${result.message}`}
              </div>
            )}
          </Box>
        </motion.div>

        <AnswerButton answerId="agent_loop"><Slide61_AgentAnswer /></AnswerButton>
      </div>
    </div>
  );
}

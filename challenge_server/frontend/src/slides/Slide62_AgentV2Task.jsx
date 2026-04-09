import { useState } from 'react';
import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, CodeBlock } from './SlideLayout';
import { postJSON } from '../api';
import AnswerButton from './AnswerButton';

export default function Slide62_AgentV2Task() {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!code.trim()) return;
    setSubmitting(true);
    try {
      const r = await postJSON('/challenges/agent_v2/submit', { answer: { completion_code: code.trim() } });
      setResult(r);
    } catch (e) { setResult({ status: 'FAIL', message: e.message }); }
    setSubmitting(false);
  };

  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agent 설계 실습</Badge>
        <SlideH2>과제: 바이브 코딩으로 에이전트 설계</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue">
            <BoxTitle>1단계: 스크립트 다운로드</BoxTitle>
            <a href="/downloads/agent_v2" download
              style={{ display: 'inline-block', padding: '8px 20px', borderRadius: 8, background: '#2563eb', color: '#fff',
                textDecoration: 'none', fontWeight: 600, fontSize: '.9em', marginBottom: 6 }}>
              📦 solve.py 다운로드
            </a>
            <div style={{ fontSize: '.88em', color: '#64748b' }}>
              바이브 코딩 도구에게 이 파일을 주고 <strong>"이 미로를 푸는 에이전트를 만들어줘"</strong>
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="red" style={{ marginTop: 8, fontSize: '.85em', padding: '14px 20px' }}>
            <BoxTitle color="#dc2626">핵심 도전 포인트</BoxTitle>
            <div style={{ lineHeight: 1.7 }}>
              <strong>1. History 관리</strong> — tool 결과를 LLM에 제대로 피드백하는가<br />
              <strong>2. Completion 판단</strong> — 언제 멈출지 설계 (모든 작업 완료 감지)<br />
              <strong>3. 에러 처리</strong> — 작업이 랜덤으로 실패함 → 재시도 로직<br />
              <strong>4. 데이터 수집</strong> — 각 작업의 반환값을 모아서 /end에 전달
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="purple" style={{ marginTop: 8, fontSize: '.82em', padding: '14px 20px' }}>
            <strong>API</strong>
            <code style={{ display: 'block', marginTop: 6, lineHeight: 1.9, background: 'rgba(0,0,0,.03)', padding: '8px 12px', borderRadius: 6 }}>
              GET /challenges/agent_v2/start?token=TOKEN → 5개 작업 목록<br />
              GET /challenges/agent_v2/task/{'{id}'}?token=TOKEN → 작업 실행 (실패 가능!)<br />
              GET /challenges/agent_v2/end?token=TOKEN → completion_code 획득
            </code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }}>
          <Box color="green" style={{ marginTop: 8, padding: '16px 24px' }}>
            <BoxTitle color="#059669">Completion Code 제출</BoxTitle>
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <input type="text" value={code} onChange={e => setCode(e.target.value)}
                placeholder="completion_code를 입력하세요"
                onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                style={{ flex: 1, padding: '10px 14px', borderRadius: 8, border: '1.5px solid #d1d5db',
                  fontSize: '.9em', fontFamily: 'monospace' }} />
              <button onClick={handleSubmit} disabled={submitting || !code.trim()}
                style={{ padding: '10px 24px', borderRadius: 8, border: 'none',
                  background: code.trim() ? '#059669' : '#e2e8f0',
                  color: code.trim() ? '#fff' : '#94a3b8',
                  fontWeight: 700, cursor: code.trim() ? 'pointer' : 'default' }}>
                {submitting ? '확인 중...' : '제출'}
              </button>
            </div>
            {result && (
              <div style={{ marginTop: 8, padding: '8px 12px', borderRadius: 6,
                background: result.status === 'SUCCESS' ? '#f0fdf4' : '#fef2f2',
                color: result.status === 'SUCCESS' ? '#059669' : '#dc2626', fontWeight: 700, fontSize: '.9em' }}>
                {result.status === 'SUCCESS' ? '🎉 ' : '❌ '}{result.message}
              </div>
            )}
          </Box>
        </motion.div>

        <AnswerButton answerId="agent_v2">
          <div>
            <h3 style={{ color: '#1e293b', marginBottom: 8 }}>예시 바이브 코딩 프롬프트</h3>
            <CodeBlock lang="prompt">{`solve.py를 완성해줘.

이 스크립트는 API 미로를 푸는 에이전트야.
- GET /challenges/agent_v2/start?token=TOKEN 으로 시작
- 5개 작업을 순서대로 GET /challenges/agent_v2/task/{id}?token=TOKEN 으로 실행
- 작업이 랜덤으로 실패할 수 있어 → 성공할 때까지 재시도
- 5개 다 끝나면 GET /challenges/agent_v2/end?token=TOKEN 호출
- completion_code를 출력해줘

requests 라이브러리 사용하고, 실패 시 최대 5회 재시도해.`}</CodeBlock>
          </div>
        </AnswerButton>
      </div>
    </div>
  );
}

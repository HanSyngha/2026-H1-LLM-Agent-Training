import { useState } from 'react';
import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, CodeBlock } from './SlideLayout';
import { postJSON } from '../api';
import AnswerButton from './AnswerButton';
import LabDownloadButton from './LabDownloadButton';

export default function Slide63b_BashToolTask({ slideRuntime }) {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!code.trim()) return;
    setSubmitting(true);
    try {
      const r = await postJSON('/challenges/bash_tool/submit', { answer: { secret_code: code.trim() } });
      setResult(r);
    } catch (e) { setResult({ status: 'FAIL', message: e.message }); }
    setSubmitting(false);
  };

  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Bash Tool 실습</Badge>
        <SlideH2>과제: subprocess로 암호 파일 해독</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue">
            <BoxTitle>1단계: 다운로드 & 실행</BoxTitle>
            <LabDownloadButton
              href="/downloads/bash_tool"
              label="📦 다운로드 (app.py + 암호 파일)"
              slideRuntime={slideRuntime}
              style={{ marginBottom: 6 }}
            />
            <code style={{ display: 'block', fontSize: '.95em', lineHeight: 1.8 }}>
              pip install requests<br />python app.py
            </code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="yellow" style={{ marginTop: 8 }}>
            <BoxTitle color="#d97706">TODO 2개 채우기</BoxTitle>
            <div style={{ fontSize: '.88em', lineHeight: 1.7 }}>
              <strong>TODO 1</strong> — <code>execute_command()</code>: subprocess.run()으로 명령어 실행<br />
              <strong>TODO 2</strong> — <code>read_file()</code>: open()으로 파일 읽기<br />
              LLM이 이 두 tool로 <code>encoded.txt</code>를 해독합니다.
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="red" style={{ marginTop: 8, fontSize: '.85em' }}>
            <strong>해독 순서:</strong> mission.txt 읽기 → base64 디코딩 → 각 줄 첫 글자 추출 → 비밀 코드!<br />
            <strong style={{ color: '#dc2626' }}>직접 디코딩 금지</strong> — LLM이 tool로 명령어를 실행해야 합니다.
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }}>
          <Box color="green" style={{ marginTop: 8, padding: '16px 24px' }}>
            <BoxTitle color="#059669">비밀 코드 제출</BoxTitle>
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <input type="text" value={code} onChange={e => setCode(e.target.value)}
                placeholder="해독한 비밀 코드를 입력하세요"
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

        <AnswerButton answerId="bash_tool">
          <div>
            <h3 style={{ color: '#1e293b', marginBottom: 8 }}>예시 바이브코딩 프롬프트</h3>
            <CodeBlock lang="prompt">{`app.py의 TODO 2개를 채워줘.

1. execute_command(command) 함수:
   subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
   stdout 있으면 stdout, 없으면 stderr 반환

2. read_file(path) 함수:
   open(path, "r", encoding="utf-8")로 파일 읽어서 내용 반환
   에러 시 에러 메시지 반환

두 함수만 구현하면 LLM이 알아서 해독합니다.`}</CodeBlock>
          </div>
        </AnswerButton>
      </div>
    </div>
  );
}

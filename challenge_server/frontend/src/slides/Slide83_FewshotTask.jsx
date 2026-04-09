import { useState } from 'react';
import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, CodeBlock } from './SlideLayout';
import { postJSON } from '../api';
import AnswerButton from './AnswerButton';

const CATEGORIES = ['P1-인프라', 'P1-데이터', 'P2-성능', 'P2-기능', 'P3-개선'];

export default function Slide83_FewshotTask() {
  const [prompt, setPrompt] = useState('');
  const [results, setResults] = useState([]);
  const [testing, setTesting] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 10 });
  const [finalMsg, setFinalMsg] = useState(null);

  const handleTest = async () => {
    if (testing) return;
    setTesting(true); setResults([]); setFinalMsg(null);
    let passed = 0;
    try {
      for (let i = 0; i < 10; i++) {
        setProgress({ current: i + 1, total: 10 });
        const r = await postJSON('/challenges/fewshot/test-one', { prompt, case_id: i });
        setResults(prev => [...prev, r]);
        if (r.pass) passed++;
      }
      if (passed === 10) {
        setFinalMsg(`🎉 ${passed}/10 전부 통과!`);
        try { await postJSON('/challenges/fewshot/submit', { answer: { prompt } }); } catch {}
      } else {
        setFinalMsg(`${passed}/10 통과 - 프롬프트를 개선하세요`);
      }
    } catch (e) {
      setFinalMsg(`에러: ${String(e)}`);
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="slide-container" style={{ padding: '20px 40px' }}>
      <div className="slide-inner">
        <Badge variant="day2">Context Engineering 실습</Badge>
        <SlideH2>과제: IT 헬프데스크 티켓 분류</SlideH2>
        <Divider />

        <div style={{ fontSize: '.85em', color: '#64748b', marginBottom: 6, lineHeight: 1.6 }}>
          사내 IT 헬프데스크 티켓을 아래 5가지 카테고리로 분류하는 <strong>시스템 프롬프트</strong>를 작성하세요.<br />
          <strong style={{ color: '#dc2626' }}>분류 규칙은 사내 전용이라 few-shot 예시 없이는 LLM이 모릅니다!</strong>
        </div>

        <div style={{ display: 'flex', gap: 6, marginBottom: 10, flexWrap: 'wrap' }}>
          {CATEGORIES.map(c => (
            <span key={c} style={{ padding: '3px 10px', borderRadius: 12, fontSize: '.78em', fontWeight: 600,
              background: c.startsWith('P1') ? '#fef2f2' : c.startsWith('P2') ? '#fefce8' : '#f0fdf4',
              color: c.startsWith('P1') ? '#dc2626' : c.startsWith('P2') ? '#d97706' : '#059669',
              border: `1px solid ${c.startsWith('P1') ? '#fca5a5' : c.startsWith('P2') ? '#fde68a' : '#86efac'}`,
            }}>{c}</span>
          ))}
        </div>

        <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
          placeholder={"시스템 프롬프트를 작성하세요. few-shot 예시를 포함해야 합니다!\n\n예:\n당신은 IT 헬프데스크 분류 봇입니다.\n카테고리: P1-인프라, P1-데이터, P2-성능, P2-기능, P3-개선\n\n분류 규칙:\n- P1-인프라: 서비스 중단, 접속 불가...\n- ...\n\n예시:\n입력: \"VPN 안됨\" → P1-인프라\n입력: \"버튼 추가 요청\" → P3-개선\n..."}
          style={{
            width: '100%', height: 150, padding: 12, borderRadius: 8,
            border: '1.5px solid #d1d5db', fontSize: '.82em', lineHeight: 1.5,
            resize: 'vertical', fontFamily: 'inherit',
          }} />

        <button onClick={handleTest} disabled={testing || !prompt.trim()}
          style={{
            marginTop: 8, padding: '10px 24px', borderRadius: 8, border: 'none', width: '100%',
            background: '#7c3aed', color: '#fff', fontWeight: 700, fontSize: '.9em', cursor: 'pointer',
          }}>
          {testing ? `⏳ ${progress.current}/${progress.total} 분류 중...` : '🧪 분류 테스트 (10개 티켓)'}
        </button>

        {(results.length > 0 || finalMsg) && (
          <div style={{ marginTop: 10, padding: 12, borderRadius: 8, background: '#fafbfc', border: '1px solid #e2e8f0' }}>
            {finalMsg && (
              <div style={{ fontWeight: 700, marginBottom: 6,
                color: finalMsg.includes('🎉') ? '#059669' : '#dc2626' }}>{finalMsg}</div>
            )}
            <div style={{ fontSize: '.78em' }}>
              {results.map((r, i) => (
                <div key={i} style={{
                  display: 'flex', gap: 8, padding: '4px 0',
                  borderBottom: '1px solid #f1f5f9', alignItems: 'center',
                }}>
                  <span style={{ width: 20, textAlign: 'center' }}>{r.pass ? '✅' : '❌'}</span>
                  <span style={{ flex: 2, color: '#475569' }}>{r.input}...</span>
                  <span style={{ flex: 1, fontWeight: 700, color: '#059669' }}>{r.expected}</span>
                  <span style={{ flex: 1, color: r.pass ? '#059669' : '#dc2626', fontFamily: 'monospace' }}>
                    {r.actual}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        <AnswerButton answerId="fewshot">
          <div>
            <h3 style={{ color: '#1e293b', marginBottom: 8 }}>예시 시스템 프롬프트 (10/10 통과)</h3>
            <CodeBlock lang="prompt">{`당신은 사내 IT 헬프데스크 티켓 분류 봇입니다.
티켓을 아래 5개 카테고리 중 하나로 정확히 분류하세요. 카테고리만 답하세요.

카테고리:
- P1-인프라: 서비스 중단, 접속 불가, 네트워크/서버 장애
- P1-데이터: 데이터 불일치, 잘못된 정보 노출, 정보 유출 위험
- P2-성능: 속도 저하, 프레임 끊김, 응답 지연
- P2-기능: 특정 기능 오작동, 버튼 안 됨, 오류 발생
- P3-개선: 기능 추가 요청, UI 변경, 편의성 개선

예시:
"VPN 접속이 안 됩니다" → P1-인프라
"ERP 재고 수량이 실제와 다릅니다" → P1-데이터
"포털 검색이 느립니다" → P2-성능
"날짜 선택이 안 됩니다" → P2-기능
"필터 옵션 추가해주세요" → P3-개선`}</CodeBlock>
          </div>
        </AnswerButton>
      </div>
    </div>
  );
}

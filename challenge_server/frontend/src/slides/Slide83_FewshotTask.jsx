import { useState } from 'react';
import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, CodeBlock } from './SlideLayout';
import { postJSON } from '../api';
import AnswerButton from './AnswerButton';

export default function Slide83_FewshotTask() {
  const [prompt, setPrompt] = useState('고객 문의를 "만족", "불만", "문의" 중 하나로 분류하세요. 카테고리만 답하세요.');
  const [examples, setExamples] = useState([{ input: '', label: '' }]);
  const [result, setResult] = useState(null);
  const [testing, setTesting] = useState(false);

  const addExample = () => setExamples([...examples, { input: '', label: '' }]);
  const removeExample = (i) => setExamples(examples.filter((_, idx) => idx !== i));
  const updateExample = (i, field, val) => {
    const copy = [...examples];
    copy[i][field] = val;
    setExamples(copy);
  };

  const handleTest = async () => {
    setTesting(true); setResult(null);
    const validExamples = examples.filter(e => e.input && e.label);
    try {
      const r = await postJSON('/challenges/fewshot/test', { prompt, examples: validExamples });
      setResult(r);
      if (r.pass) {
        try { await postJSON('/challenges/fewshot/submit', { answer: { prompt, examples: validExamples } }); } catch {}
      }
    } catch (e) { setResult({ pass: false, message: e.message }); }
    setTesting(false);
  };

  return (
    <div className="slide-container" style={{ padding: '20px 40px' }}>
      <div className="slide-inner">
        <Badge variant="day2">Context Engineering 실습</Badge>
        <SlideH2>과제: 최소 예시로 분류 80% 달성</SlideH2>
        <Divider />

        <div style={{ fontSize: '.85em', marginBottom: 8, color: '#64748b' }}>
          고객 문의를 <strong>만족/불만/문의</strong>로 분류합니다. 시스템 프롬프트와 few-shot 예시를 작성하세요.
        </div>

        <div style={{ marginBottom: 8 }}>
          <div style={{ fontWeight: 700, fontSize: '.82em', marginBottom: 4 }}>System Prompt</div>
          <input value={prompt} onChange={e => setPrompt(e.target.value)}
            style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db', fontSize: '.85em' }} />
        </div>

        <div style={{ marginBottom: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span style={{ fontWeight: 700, fontSize: '.82em' }}>Few-shot 예시 ({examples.length}개)</span>
            <button onClick={addExample}
              style={{ padding: '2px 10px', borderRadius: 4, border: '1px solid #d1d5db', background: '#fff',
                fontSize: '.78em', cursor: 'pointer' }}>+ 추가</button>
          </div>
          {examples.map((ex, i) => (
            <div key={i} style={{ display: 'flex', gap: 6, marginBottom: 4 }}>
              <input value={ex.input} onChange={e => updateExample(i, 'input', e.target.value)}
                placeholder="입력 예시"
                style={{ flex: 3, padding: '6px 10px', borderRadius: 4, border: '1px solid #d1d5db', fontSize: '.8em' }} />
              <select value={ex.label} onChange={e => updateExample(i, 'label', e.target.value)}
                style={{ flex: 1, padding: '6px 8px', borderRadius: 4, border: '1px solid #d1d5db', fontSize: '.8em' }}>
                <option value="">라벨</option>
                <option value="만족">만족</option>
                <option value="불만">불만</option>
                <option value="문의">문의</option>
              </select>
              {examples.length > 1 && (
                <button onClick={() => removeExample(i)}
                  style={{ padding: '4px 8px', borderRadius: 4, border: '1px solid #fca5a5', background: '#fff',
                    color: '#dc2626', fontSize: '.75em', cursor: 'pointer' }}>X</button>
              )}
            </div>
          ))}
        </div>

        <button onClick={handleTest} disabled={testing || !prompt.trim()}
          style={{
            padding: '10px 24px', borderRadius: 8, border: 'none', width: '100%',
            background: '#7c3aed', color: '#fff', fontWeight: 700, fontSize: '.9em', cursor: 'pointer',
          }}>
          {testing ? '10개 케이스 테스트 중...' : '🧪 분류 테스트 (10개 케이스)'}
        </button>

        {result && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            style={{ marginTop: 10, padding: 12, borderRadius: 8,
              background: result.pass ? '#f0fdf4' : '#fef2f2', border: `1px solid ${result.pass ? '#86efac' : '#fca5a5'}` }}>
            <div style={{ fontWeight: 700, color: result.pass ? '#059669' : '#dc2626', marginBottom: 6 }}>
              {result.pass ? '🎉 ' : ''}{result.message} (예시 {result.example_count || 0}개 사용)
            </div>
            {result.results && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 4, fontSize: '.75em' }}>
                {result.results.map((r, i) => (
                  <div key={i} style={{
                    padding: '4px 6px', borderRadius: 4, textAlign: 'center',
                    background: r.pass ? '#dcfce7' : '#fef2f2',
                    color: r.pass ? '#166534' : '#dc2626',
                  }}>
                    {r.pass ? '✅' : '❌'} {r.expected}
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        <AnswerButton answerId="fewshot">
          <div>
            <h3 style={{ color: '#1e293b', marginBottom: 8 }}>예시 답안 (10/10 통과)</h3>
            <CodeBlock lang="text">{`System Prompt:
"고객 문의를 '만족', '불만', '문의' 중 하나로만 분류하세요. 카테고리만 답하세요."

Few-shot 예시 3개:
1. "너무 좋아요 감사합니다" → 만족
2. "이게 뭐야 돈 아까워" → 불만
3. "배송 현황 알려주세요" → 문의`}</CodeBlock>
          </div>
        </AnswerButton>
      </div>
    </div>
  );
}

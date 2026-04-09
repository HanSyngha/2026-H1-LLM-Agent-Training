import { useState } from 'react';
import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';
import { postJSON } from '../api';
import AnswerButton from './AnswerButton';
import { CodeBlock } from './SlideLayout';

const LONG_DOC = `[반도체 사업부 2026년 상반기 전략 회의록]
일시: 2026-03-15 | 참석: 최현우 부사장, 박영수 상무, 김태호 팀장, 오정훈 팀장 외

1. HBM4 개발: 16단 적층 샘플 완성, 열 관리 문제로 양산 2개월 지연. 그래핀 TIM으로 전환 검토 → Q3 양산 목표.
2. DRAM 1c 전환: 1b 수율 91.2% 안정화. EUV 더블 패터닝 도입, 4월 파일럿→7월 양산. EUV 장비 2대 추가(8,000억).
3. AI 가속기(PIM): 시장 $4B 전망. 로직 인력 부족(50→200명), 외부 파운드리 활용 결정. 하반기 100명 채용.
4. 핵심 실행과제: HBM4 Q3 양산, 1c 전환, PIM 사업, 원가 8% 절감, AI석박사 50명 확보.`;

export default function Slide81_ContextTask() {
  const [compressed, setCompressed] = useState('');
  const [result, setResult] = useState(null);
  const [testing, setTesting] = useState(false);

  const handleTest = async () => {
    setTesting(true); setResult(null);
    try {
      const r = await postJSON('/challenges/context/test', { compressed });
      setResult(r);
      if (r.pass) {
        // 자동 제출
        try { await postJSON('/challenges/context/submit', { answer: { compressed } }); } catch {}
      }
    } catch (e) {
      setResult({ pass: false, message: e.message });
    }
    setTesting(false);
  };

  return (
    <div className="slide-container" style={{ padding: '20px 40px' }}>
      <div className="slide-inner">
        <Badge variant="day2">Context Engineering 실습</Badge>
        <SlideH2>과제: 5000자 회의록을 500자로 압축</SlideH2>
        <Divider />

        <div style={{ display: 'flex', gap: 14 }}>
          {/* 왼쪽: 원본 */}
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: '.85em', marginBottom: 6, color: '#64748b' }}>
              원본 회의록 ({LONG_DOC.length}자)
            </div>
            <div style={{
              background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8,
              padding: 12, fontSize: '.78em', lineHeight: 1.6, maxHeight: 280, overflowY: 'auto',
              whiteSpace: 'pre-wrap', color: '#334155',
            }}>
              {LONG_DOC}
            </div>
          </div>

          {/* 오른쪽: 압축 */}
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: '.85em', marginBottom: 6, color: '#7c3aed' }}>
              압축 프롬프트 ({compressed.length}/500자)
            </div>
            <textarea
              value={compressed} onChange={e => setCompressed(e.target.value)}
              placeholder="핵심만 남겨서 500자 이내로 압축하세요..."
              style={{
                width: '100%', height: 200, padding: 12, borderRadius: 8,
                border: `1.5px solid ${compressed.length > 500 ? '#ef4444' : '#d1d5db'}`,
                fontSize: '.82em', lineHeight: 1.5, resize: 'none', fontFamily: 'inherit',
              }}
            />
            <button onClick={handleTest} disabled={testing || !compressed.trim() || compressed.length > 500}
              style={{
                marginTop: 8, padding: '8px 20px', borderRadius: 8, border: 'none', width: '100%',
                background: compressed.trim() && compressed.length <= 500 ? '#7c3aed' : '#e2e8f0',
                color: compressed.trim() && compressed.length <= 500 ? '#fff' : '#94a3b8',
                fontWeight: 700, fontSize: '.9em', cursor: 'pointer',
              }}>
              {testing ? 'AI 예측 중...' : '🧪 AI에게 다음 행동 예측시키기'}
            </button>
          </div>
        </div>

        {result && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            style={{
              marginTop: 12, padding: 14, borderRadius: 10,
              background: result.pass ? '#f0fdf4' : '#fef2f2',
              border: `1px solid ${result.pass ? '#86efac' : '#fca5a5'}`,
            }}>
            <div style={{ fontWeight: 700, color: result.pass ? '#059669' : '#dc2626', marginBottom: 6 }}>
              {result.pass ? '🎉 ' : '❌ '}{result.message}
            </div>
            {result.actions && result.actions.length > 0 && (
              <div style={{ fontSize: '.85em' }}>
                <strong>AI가 예측한 행동:</strong>
                {result.actions.map((a, i) => (
                  <div key={i} style={{ padding: '3px 0', color: '#334155' }}>
                    {i+1}. {a} {result.results?.[i] && (result.results[i].matched ? ' ✅' : ' ❌')}
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        <AnswerButton answerId="context">
          <div>
            <h3 style={{ color: '#1e293b', marginBottom: 8 }}>예시 압축 프롬프트 (3/3 통과)</h3>
            <CodeBlock lang="text">{`HBM4: 16단 샘플 완성, 열 문제로 양산 지연. 그래핀 TIM 전환하여 Q3 양산 목표.
DRAM 1c: 1b 수율 91.2% 안정화. EUV 더블패터닝 도입, 4월 파일럿→7월 양산. EUV 장비 2대 추가(8000억).
PIM: 시장 $4B. 로직 인력 부족(50→200명). 외부 파운드리 활용, 하반기 100명 채용.
핵심 실행: HBM4 양산, 1c 전환, PIM 사업, 원가 8% 절감.`}</CodeBlock>
          </div>
        </AnswerButton>
      </div>
    </div>
  );
}

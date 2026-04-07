import { useState, useEffect } from 'react';
import { getPromptCases, testPrompt, submitPrompt } from '../api';

export default function PromptChallenge({ user }) {
  const [cases, setCases] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [results, setResults] = useState({});
  const [testing, setTesting] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0, caseId: null });
  const [finalResult, setFinalResult] = useState(null);

  useEffect(() => { getPromptCases().then(setCases); }, []);

  const runTest = async () => {
    if (!prompt.trim()) { alert('프롬프트를 입력하세요.'); return; }
    setTesting(true);
    setResults({});
    setFinalResult(null);

    let passed = 0;
    for (let i = 0; i < cases.length; i++) {
      const tc = cases[i];
      setProgress({ current: i, total: cases.length, caseId: tc.id });
      try {
        const r = await testPrompt(prompt, tc.id);
        setResults(prev => ({ ...prev, [tc.id]: r }));
        if (r.pass) passed++;
      } catch (e) {
        setResults(prev => ({ ...prev, [tc.id]: { pass: false, error: e.message } }));
      }
    }
    setProgress({ current: cases.length, total: cases.length, caseId: null });
    setFinalResult({ passed, total: cases.length });
    setTesting(false);
  };

  const runSubmit = async () => {
    if (!user) { window.location.href = '/auth/login?redirect=/challenges/prompt'; return; }
    const r = await submitPrompt(prompt);
    setFinalResult({ ...r, submitted: true });
  };

  const allPass = finalResult?.passed === finalResult?.total && finalResult?.total > 0;

  return (
    <div className="container">
      <div className="page-header">
        <h1>프롬프트 엔지니어링 Challenge</h1>
        <p>하나의 프롬프트로 10개 금융 기사의 실적 데이터를 정확히 추출하세요</p>
      </div>

      {/* 추출 필드 안내 */}
      <div className="card" style={{ marginBottom: 16, padding: '16px 24px' }}>
        <h3 style={{ marginBottom: 8 }}>추출할 필드 (10개)</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, fontSize: '.85em' }}>
          {['company (회사명)', 'ticker (종목코드)', 'revenue (매출, 억원)', 'operating_profit (영업이익, 억원)',
            'net_income (순이익, 억원)', 'stock_price (주가, 원)', 'price_change_pct (등락률, %)',
            'consensus_op (컨센서스, 억원)', 'eps (EPS, 원)', 'target_price (목표가, 원)'].map(f => (
            <span key={f} style={{ padding: '4px 12px', borderRadius: 16, background: '#f1f5f9', color: 'var(--text2)' }}>{f}</span>
          ))}
        </div>
      </div>

      {/* 프롬프트 입력 */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3>System Prompt 작성</h3>
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="금융 기사에서 실적 데이터를 추출하는 system prompt를 작성하세요.&#10;&#10;이 프롬프트 하나로 10개의 서로 다른 기사를 처리해야 합니다.&#10;모든 필드가 exact match여야 PASS입니다."
        />

        {user && (
          <div style={{ marginTop: 8, fontSize: '.85em', color: 'var(--green)' }}>
            ✅ {user.name} ({user.dept})
          </div>
        )}

        <div style={{ display: 'flex', gap: 10, marginTop: 12 }}>
          <button className="btn btn-blue" onClick={runTest} disabled={testing}>
            {testing ? `⏳ 실행 중... (${progress.current}/${progress.total})` : '🧪 전체 테스트 (10개)'}
          </button>
          <button className="btn btn-green" onClick={runSubmit} disabled={!allPass || testing}>
            🎯 제출 {allPass ? '' : '(전체 통과 시)'}
          </button>
        </div>

        {progress.total > 0 && (
          <div style={{ marginTop: 8 }}>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${(progress.current / progress.total) * 100}%` }} />
            </div>
            <div style={{ fontSize: '.8em', color: 'var(--text3)', textAlign: 'center' }}>
              {progress.current} / {progress.total}
            </div>
          </div>
        )}
      </div>

      {/* 최종 결과 */}
      {finalResult && (
        <div className="card" style={{
          marginBottom: 16, textAlign: 'center', padding: 24,
          background: allPass ? '#f0fdf4' : '#fef2f2',
          borderColor: allPass ? '#86efac' : '#fca5a5',
        }}>
          <h2 style={{ color: allPass ? 'var(--green)' : 'var(--red)', fontSize: '1.4em' }}>
            {allPass ? '🎉 전체 통과!' : `❌ ${finalResult.passed}/${finalResult.total} 통과`}
          </h2>
          <p style={{ color: 'var(--text2)', marginTop: 4 }}>
            {allPass
              ? (finalResult.submitted ? finalResult.message || '대시보드에서 확인하세요!' : '제출 버튼을 눌러 성공을 등록하세요.')
              : '실패한 케이스의 Expected vs Actual을 확인하고 프롬프트를 수정하세요.'}
          </p>
        </div>
      )}

      {/* 테스트 케이스 카드 */}
      <div className="grid grid-2">
        {cases.map(tc => {
          const r = results[tc.id];
          const status = r ? (r.pass ? 'pass' : 'fail') : (testing && progress.caseId === tc.id ? 'testing' : '');

          return (
            <div className={`case-card ${status}`} key={tc.id}>
              <div className="case-header">
                <strong>#{tc.id} {tc.title}</strong>
                <span className={`badge ${r ? (r.pass ? 'badge-pass' : 'badge-fail') : 'badge-pending'}`}>
                  {r ? (r.pass ? 'PASS' : 'FAIL') : (status === 'testing' ? '실행 중...' : '대기')}
                </span>
              </div>
              <div className="case-input">{tc.input.substring(0, 120)}...</div>

              {r && r.details && (
                <table className="detail-table">
                  <thead><tr><th>필드</th><th>결과</th><th>예상</th><th>실제</th></tr></thead>
                  <tbody>
                    {r.details.map(d => (
                      <tr key={d.key}>
                        <td style={{ fontWeight: 600 }}>{d.key}</td>
                        <td className={d.pass ? 'pass-text' : 'fail-text'}>{d.pass ? '✓' : '✗'}</td>
                        <td>{JSON.stringify(d.expected)}</td>
                        <td>{JSON.stringify(d.actual)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {r && r.error && (
                <div style={{ fontSize: '.8em', color: 'var(--red)', marginTop: 8 }}>{r.error}</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

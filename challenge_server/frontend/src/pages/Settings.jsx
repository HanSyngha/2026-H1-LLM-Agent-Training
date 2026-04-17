import { useState, useEffect } from 'react';
import { fetchJSON, postJSON } from '../api';

export default function Settings() {
  const [endpoints, setEndpoints] = useState({});
  const [challengeMap, setChallengeMap] = useState({});
  const [challenges, setChallenges] = useState([]);
  const [form, setForm] = useState({ name: '', base_url: '', api_key: '', model: '' });
  const [status, setStatus] = useState(null);
  const [vlForm, setVlForm] = useState({ base_url: '', api_key: '', model: '' });
  const [vlStatus, setVlStatus] = useState(null);

  useEffect(() => {
    fetchJSON('/settings/llm-endpoints').then(d => {
      setEndpoints(d.endpoints || {});
      setChallengeMap(d.challenge_map || {});
    });
    fetchJSON('/challenges').then(setChallenges);
    fetchJSON('/settings/vl').then(d => {
      if (d.base_url) setVlForm({ base_url: d.base_url, api_key: '', model: d.model });
    });
  }, []);

  const addLLM = async () => {
    if (!form.base_url || !form.model) { setStatus({ ok: false, msg: 'URL과 모델은 필수입니다.' }); return; }
    setStatus({ ok: null, msg: '테스트 중...' });
    const r = await postJSON('/settings/llm-endpoints', { ...form, name: form.name || form.model });
    setStatus({ ok: r.status === 'ok', msg: r.message });
    if (r.status === 'ok') {
      setForm({ name: '', base_url: '', api_key: '', model: '' });
      const d = await fetchJSON('/settings/llm-endpoints');
      setEndpoints(d.endpoints || {});
    }
  };

  const setMapping = async (challengeId, llmId) => {
    await postJSON('/settings/challenge-llm', { challenge_id: challengeId, llm_id: llmId });
    setChallengeMap(prev => ({ ...prev, [challengeId]: llmId }));
  };

  return (
    <div className="page-shell" style={{ maxWidth: 980 }}>
      <div className="page-hero">
        <div className="page-eyebrow">Admin Console</div>
        <h1 className="page-title">설정</h1>
        <p className="page-copy">
          사내망용 강의안 운영에 필요한 LLM 엔드포인트, VL 채점 모델, 과제별 매핑을 여기서 관리합니다.
        </p>
      </div>

      <div className="content-card stack" style={{ marginBottom: 18 }}>
        <h3>LLM 엔드포인트 추가</h3>
        <div className="form-grid">
          <input placeholder="이름" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
          />
          <input placeholder="모델" value={form.model} onChange={e => setForm({ ...form, model: e.target.value })}
          />
        </div>
        <input placeholder="Base URL" value={form.base_url} onChange={e => setForm({ ...form, base_url: e.target.value })}
          style={{ fontFamily: 'JetBrains Mono, monospace' }} />
        <input placeholder="API Key" type="password" value={form.api_key} onChange={e => setForm({ ...form, api_key: e.target.value })}
        />
        <div className="inline-actions">
          <button className="btn btn-blue" onClick={addLLM}>+ 추가 및 테스트</button>
        </div>
        {status && (
          <div className={`status-card ${status.ok === true ? 'status-success' : status.ok === false ? 'status-error' : 'status-neutral'}`}>
            {status.msg}
          </div>
        )}

        {Object.keys(endpoints).length > 0 && (
          <div className="stack">
            {Object.entries(endpoints).map(([id, e]) => (
              <div key={id} className="list-row" style={{ border: '1px solid var(--line)', borderRadius: 18, background: 'rgba(255,255,255,.56)' }}>
                <div>
                  <div className="list-row-title">{e.name}</div>
                  <div className="list-row-meta" style={{ fontFamily: 'JetBrains Mono, monospace', marginTop: 4 }}>{e.base_url} · {e.model}</div>
                </div>
                <div className="inline-actions">
                  <span className="list-row-meta">{id}</span>
                  <button onClick={async () => {
                    await fetch(`/settings/llm-endpoints/${id}`, { method: 'DELETE' });
                    const d = await fetchJSON('/settings/llm-endpoints');
                    setEndpoints(d.endpoints || {});
                    setChallengeMap(d.challenge_map || {});
                  }} className="btn btn-danger" style={{ padding: '8px 12px' }}>삭제</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="content-card stack" style={{ marginBottom: 18 }}>
        <h3>VL 모델 설정 (대시보드 채점용)</h3>
        <p className="subtle">React 대시보드 과제 스크린샷을 평가하는 Vision-Language 모델입니다.</p>
        <input placeholder="Base URL (예: https://llm-gateway.example.com/v1)" value={vlForm.base_url}
          onChange={e => setVlForm({ ...vlForm, base_url: e.target.value })}
          style={{ fontFamily: 'JetBrains Mono, monospace' }} />
        <div className="form-grid">
          <input placeholder="모델명 (예: qwen3.5-35b-a3b)" value={vlForm.model}
            onChange={e => setVlForm({ ...vlForm, model: e.target.value })}
          />
          <input placeholder="API Key" type="password" value={vlForm.api_key}
            onChange={e => setVlForm({ ...vlForm, api_key: e.target.value })}
          />
        </div>
        <div className="inline-actions">
          <button className="btn btn-blue" onClick={async () => {
            setVlStatus({ ok: null, msg: '설정 중...' });
            const r = await postJSON('/settings/vl', vlForm);
            setVlStatus({ ok: r.status === 'ok', msg: r.message });
          }}>VL 모델 설정</button>
        </div>
        {vlStatus && (
          <div className={`status-card ${vlStatus.ok ? 'status-success' : 'status-error'}`}>
            {vlStatus.msg}
          </div>
        )}
      </div>

      <div className="content-card">
        <h3>과제별 LLM 매핑</h3>
        <div className="data-table" style={{ marginTop: 14 }}>
          <table>
            <thead><tr><th>과제</th><th>LLM</th></tr></thead>
            <tbody>
              {[{ id: 'prompt', name: '프롬프트 엔지니어링' }, ...challenges].map(c => (
                <tr key={c.id}>
                  <td style={{ fontWeight: 700, color: 'var(--text)' }}>{c.name}</td>
                  <td>
                    <select value={challengeMap[c.id] || ''} onChange={e => setMapping(c.id, e.target.value)}
                      style={{ minWidth: 220 }}>
                      <option value="">(기본) testmodel — llm.example.com</option>
                      {Object.entries(endpoints).map(([id, e]) => (
                        <option key={id} value={id}>{e.name} ({e.model})</option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

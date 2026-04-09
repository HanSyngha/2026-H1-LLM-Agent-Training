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
    <div className="container" style={{ maxWidth: 800 }}>
      <div className="page-header">
        <h1>설정</h1>
        <p>LLM 엔드포인트 관리 및 과제 매핑</p>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3>LLM 엔드포인트 추가</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 12 }}>
          <input placeholder="이름" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
            style={{ padding: 10, border: '1px solid var(--border)', borderRadius: 8 }} />
          <input placeholder="모델" value={form.model} onChange={e => setForm({ ...form, model: e.target.value })}
            style={{ padding: 10, border: '1px solid var(--border)', borderRadius: 8 }} />
        </div>
        <input placeholder="Base URL" value={form.base_url} onChange={e => setForm({ ...form, base_url: e.target.value })}
          style={{ width: '100%', padding: 10, border: '1px solid var(--border)', borderRadius: 8, marginTop: 8, fontFamily: 'monospace' }} />
        <input placeholder="API Key" type="password" value={form.api_key} onChange={e => setForm({ ...form, api_key: e.target.value })}
          style={{ width: '100%', padding: 10, border: '1px solid var(--border)', borderRadius: 8, marginTop: 8 }} />
        <button className="btn btn-blue" onClick={addLLM} style={{ marginTop: 12 }}>+ 추가 및 테스트</button>
        {status && (
          <div style={{ marginTop: 8, padding: 10, borderRadius: 8, fontSize: '.85em',
            background: status.ok === true ? '#f0fdf4' : status.ok === false ? '#fef2f2' : '#f1f5f9',
            color: status.ok === true ? 'var(--green)' : status.ok === false ? 'var(--red)' : 'var(--text3)' }}>
            {status.msg}
          </div>
        )}

        {Object.keys(endpoints).length > 0 && (
          <div style={{ marginTop: 16 }}>
            {Object.entries(endpoints).map(([id, e]) => (
              <div key={id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '10px 14px', background: 'var(--bg)', borderRadius: 8, marginTop: 8 }}>
                <div>
                  <div style={{ fontWeight: 600 }}>{e.name}</div>
                  <div style={{ fontSize: '.78em', color: 'var(--text3)', fontFamily: 'monospace' }}>{e.base_url} · {e.model}</div>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <span style={{ fontSize: '.78em', color: 'var(--text3)' }}>{id}</span>
                  <button onClick={async () => {
                    await fetch(`/settings/llm-endpoints/${id}`, { method: 'DELETE' });
                    const d = await fetchJSON('/settings/llm-endpoints');
                    setEndpoints(d.endpoints || {});
                    setChallengeMap(d.challenge_map || {});
                  }} style={{ padding: '4px 10px', borderRadius: 6, border: '1px solid #fca5a5', background: '#fef2f2',
                    color: '#dc2626', fontSize: '.75em', cursor: 'pointer', fontWeight: 600 }}>삭제</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3>VL 모델 설정 (대시보드 채점용)</h3>
        <p style={{ fontSize: '.85em', color: 'var(--text3)', marginTop: 4 }}>React 대시보드 과제의 스크린샷을 채점하는 Vision-Language 모델</p>
        <input placeholder="Base URL (예: http://a2g.samsungds.net:8090/v1)" value={vlForm.base_url}
          onChange={e => setVlForm({ ...vlForm, base_url: e.target.value })}
          style={{ width: '100%', padding: 10, border: '1px solid var(--border)', borderRadius: 8, marginTop: 8, fontFamily: 'monospace' }} />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 8 }}>
          <input placeholder="모델명 (예: qwen3.5-35b-a3b)" value={vlForm.model}
            onChange={e => setVlForm({ ...vlForm, model: e.target.value })}
            style={{ padding: 10, border: '1px solid var(--border)', borderRadius: 8 }} />
          <input placeholder="API Key" type="password" value={vlForm.api_key}
            onChange={e => setVlForm({ ...vlForm, api_key: e.target.value })}
            style={{ padding: 10, border: '1px solid var(--border)', borderRadius: 8 }} />
        </div>
        <button className="btn btn-blue" onClick={async () => {
          setVlStatus({ ok: null, msg: '설정 중...' });
          const r = await postJSON('/settings/vl', vlForm);
          setVlStatus({ ok: r.status === 'ok', msg: r.message });
        }} style={{ marginTop: 12 }}>VL 모델 설정</button>
        {vlStatus && (
          <div style={{ marginTop: 8, padding: 10, borderRadius: 8, fontSize: '.85em',
            background: vlStatus.ok ? '#f0fdf4' : '#fef2f2',
            color: vlStatus.ok ? 'var(--green)' : 'var(--red)' }}>
            {vlStatus.msg}
          </div>
        )}
      </div>

      <div className="card">
        <h3>과제별 LLM 매핑</h3>
        <table style={{ marginTop: 12 }}>
          <thead><tr><th>과제</th><th>LLM</th></tr></thead>
          <tbody>
            {[{ id: 'prompt', name: '프롬프트 엔지니어링' }, ...challenges].map(c => (
              <tr key={c.id}>
                <td style={{ fontWeight: 600 }}>{c.name}</td>
                <td>
                  <select value={challengeMap[c.id] || ''} onChange={e => setMapping(c.id, e.target.value)}
                    style={{ padding: 6, borderRadius: 6, border: '1px solid var(--border)', minWidth: 150 }}>
                    <option value="">선택 안 함</option>
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
  );
}

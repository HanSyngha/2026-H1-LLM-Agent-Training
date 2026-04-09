import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';
import { postJSON } from '../api';

export default function Slide76c_ReactDashboardTask() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const pasteRef = useRef(null);

  const handlePaste = (e) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const blob = item.getAsFile();
        const reader = new FileReader();
        reader.onload = (ev) => {
          setImage(ev.target.result);
          setPreview(ev.target.result);
        };
        reader.readAsDataURL(blob);
        break;
      }
    }
  };

  const handleSubmit = async () => {
    if (!image) return;
    setSubmitting(true); setResult(null);
    try {
      const r = await postJSON('/dashboard-challenge/submit', { image });
      setResult(r);
    } catch (e) { setResult({ status: 'FAIL', message: e.message, score: 0 }); }
    setSubmitting(false);
  };

  return (
    <div className="slide-container" style={{ padding: '20px 40px' }}>
      <div className="slide-inner">
        <Badge variant="day2">React 대시보드 실습</Badge>
        <SlideH2>과제: LLM 사용 현황 대시보드 만들기</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue" style={{ fontSize: '.85em', padding: '14px 20px' }}>
            <BoxTitle>제공 API (5개 모두 활용하세요!)</BoxTitle>
            <code style={{ display: 'block', lineHeight: 1.8, marginTop: 6 }}>
              GET /dashboard-challenge/api/usage  — 일별 호출수, 토큰량<br />
              GET /dashboard-challenge/api/users  — 주간 사용자 추이<br />
              GET /dashboard-challenge/api/tools  — Tool별 호출, 성공률<br />
              GET /dashboard-challenge/api/models — 모델별 요청, 지연, 비용<br />
              GET /dashboard-challenge/api/costs  — 월별 비용 vs 예산
            </code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="purple" style={{ marginTop: 8, fontSize: '.85em' }}>
            <BoxTitle color="#7c3aed">React + Stitch로 대시보드 만들기</BoxTitle>
            <div style={{ lineHeight: 1.7 }}>
              1. React 프로젝트 생성 (<code>npm create vite@latest</code>)<br />
              2. 위 API로 데이터 fetch<br />
              3. 차트/그래프로 시각화 (recharts, chart.js 등)<br />
              4. Stitch로 디자인하면 가산점!<br />
              5. 완성 후 스크린샷을 아래에 붙여넣기
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="green" style={{ marginTop: 8, padding: '16px 20px' }}>
            <BoxTitle color="#059669">스크린샷 제출 (Ctrl+V로 붙여넣기)</BoxTitle>
            <div ref={pasteRef} onPaste={handlePaste} tabIndex={0}
              style={{
                marginTop: 8, minHeight: 120, border: '2px dashed #d1d5db', borderRadius: 10,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', background: preview ? 'transparent' : '#f8fafc',
                outline: 'none', position: 'relative', overflow: 'hidden',
              }}
              onClick={() => pasteRef.current?.focus()}>
              {preview ? (
                <img src={preview} alt="dashboard" style={{ maxWidth: '100%', maxHeight: 200, borderRadius: 8 }} />
              ) : (
                <span style={{ color: '#94a3b8', fontSize: '.9em' }}>
                  여기를 클릭하고 Ctrl+V로 스크린샷을 붙여넣으세요
                </span>
              )}
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <button onClick={handleSubmit} disabled={submitting || !image}
                style={{
                  flex: 1, padding: '10px', borderRadius: 8, border: 'none',
                  background: image ? '#059669' : '#e2e8f0',
                  color: image ? '#fff' : '#94a3b8',
                  fontWeight: 700, fontSize: '.9em', cursor: image ? 'pointer' : 'default',
                }}>
                {submitting ? 'VL 모델 채점 중...' : '🎨 제출 & 채점'}
              </button>
              {image && (
                <button onClick={() => { setImage(null); setPreview(null); setResult(null); }}
                  style={{ padding: '10px 16px', borderRadius: 8, border: '1px solid #d1d5db',
                    background: '#fff', cursor: 'pointer', fontSize: '.85em' }}>
                  초기화
                </button>
              )}
            </div>
            {result && (
              <div style={{
                marginTop: 8, padding: '12px 16px', borderRadius: 8,
                background: result.score >= 70 ? '#f0fdf4' : result.score >= 40 ? '#fefce8' : '#fef2f2',
                border: `1px solid ${result.score >= 70 ? '#86efac' : result.score >= 40 ? '#fde68a' : '#fca5a5'}`,
              }}>
                <div style={{ fontSize: '1.5em', fontWeight: 900, color: result.score >= 70 ? '#059669' : result.score >= 40 ? '#d97706' : '#dc2626' }}>
                  {result.score}점
                </div>
                <div style={{ fontSize: '.88em', color: '#475569', marginTop: 4 }}>{result.feedback || result.message}</div>
              </div>
            )}
          </Box>
        </motion.div>
      </div>
    </div>
  );
}

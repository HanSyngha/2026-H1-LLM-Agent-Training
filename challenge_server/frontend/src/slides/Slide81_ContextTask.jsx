import { useState } from 'react';
import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';
import { postJSON } from '../api';
import AnswerButton from './AnswerButton';
import { CodeBlock } from './SlideLayout';

const LONG_DOC = `[반도체 사업부 2026년 상반기 전략 회의록]
일시: 2026-03-15 09:00-12:00 | 장소: 본관 19층 대회의실
참석: 최현우 부사장, 박영수 상무, 김태호 팀장, 오정훈 팀장, 이수진 과장, 정민호 대리, 한지원 사원 외 12명
서기: 한지원 사원 | 배포: 참석자 전원 + 기술기획실

[안건 1] HBM4 개발 현황 (발표: 오정훈 팀장, 30분)
현재 HBM4 16단 적층 샘플이 완성되었으나, 열 관리 문제로 양산 일정이 2개월 지연 중이다. 구체적으로 상위 4개 다이의 온도가 정상 작동 범위(105도)를 초과하는 현상이 반복 발생하고 있다. 마이크로범프 간격을 40um에서 35um로 줄이는 미세 피치 기술 개발이 핵심 과제로 부상하였다. 경쟁사 SK하이닉스는 이미 HBM4 샘플을 N사(NVIDIA)에 납품한 것으로 확인되었으며, 마이크론은 2026년 Q4 양산을 목표로 하고 있다. 오정훈 팀장은 열계면재(TIM) 소재를 기존 인듐(Indium)에서 그래핀 복합재로 전환하는 방안을 제안하였다. 그래핀 TIM의 열전도율은 기존 대비 3배이며, 이를 적용하면 열저항을 30% 감소시킬 수 있다. 이 경우 양산 일정을 2026년 Q3로 앞당길 수 있을 것으로 예상된다. 다만 그래핀 TIM의 대량 생산 공정은 아직 검증이 필요하며, 소재 업체 A사와 공동 개발 MOU가 체결되었다.

[안건 2] DRAM 1c 공정 전환 (발표: 김태호 팀장, 25분)
1b 공정 수율이 91.2%로 안정화되어 1c 전환 준비가 완료되었다. 1c 공정의 핵심은 EUV 더블 패터닝 도입으로 회로 밀도를 25% 향상시키는 것이다. 현재 EUV 장비 가동률이 78%로 목표(85%)에 미달하고 있어 이를 개선해야 한다. ASML과 기술 지원 계약을 체결하여 장비 가동률 향상을 추진 중이다. 파일럿 라인은 4월에 가동을 시작하고, 7월에 본 양산에 돌입할 계획이다. 이를 위해 EUV 장비 2대를 추가 도입하며 (ASML NXE:3800, 대당 4,000억원, 총 8,000억원), 클린룸 증설도 병행한다.

[안건 3] AI 가속기 사업 진출 검토 (발표: 박영수 상무, 35분)
메모리 중심 AI 가속기(PIM) 사업화 검토 결과를 보고하였다. 2027년 AI 가속기 시장은 $80B으로 전망되며, PIM 비중은 약 5%($4B)로 추정된다. 당사의 강점은 메모리 공정 기술, HBM 양산 경험, 첨단 패키징 기술이며, 약점은 로직 설계 인력 부족(현재 50명, 필요 200명)과 IP 라이센스 미확보이다. 최현우 부사장은 PIM 1세대 개발은 진행하되, 로직 부분은 외부 파운드리를 활용하여 리스크를 최소화하라고 지시하였다. 로직 설계 인력 100명을 하반기에 채용하는 계획을 수립하기로 하였다. 박영수 상무는 ARM과의 IP 라이센스 협상이 진행 중이며 6월까지 계약 체결이 목표라고 보고하였다.

[안건 4] 하반기 핵심 실행 과제 (최현우 부사장 종합, 20분)
(1) HBM4 양산 일정 사수: Q3 양산 시작, 그래핀 TIM 개발 가속화 (4월 시제품, 5월 양산테스트, 6월 수율안정화)
(2) DRAM 1c 전환: 4월 파일럿, 7월 양산, EUV 가동률 85% 달성
(3) PIM 사업: 외부 파운드리 계약, ARM IP 라이센스 확보, 로직 인력 100명 채용
(4) 원가 절감: 웨이퍼당 원가 8% 절감 (자동화 + 수율 개선)
(5) 인재 확보: AI/반도체 석박사 50명 산학 프로그램 운영

[기타 논의]
- 이수진 과장: HBM4 테스트 장비 리드타임 3개월, 즉시 발주 필요
- 정민호 대리: DRAM 1c 파일럿 라인 청정도 업그레이드 필요 (Class 10 → Class 1)
- 박영수 상무: PIM 관련 특허 3건 Q2 내 출원 예정

다음 회의: 2026-04-15 09:00 (월간 진척 점검)`;

export default function Slide81_ContextTask() {
  const [compressed, setCompressed] = useState('');
  const [result, setResult] = useState(null);
  const [testing, setTesting] = useState(false);

  const handleTest = async () => {
    console.log('[Context] handleTest called, compressed:', compressed.length, 'testing:', testing);
    setTesting(true); setResult(null);
    try {
      const r = await postJSON('/challenges/context/test', { compressed });
      setResult(r);
      if (r.pass) {
        try { await postJSON('/challenges/context/submit', { answer: { compressed } }); } catch {}
      }
    } catch (e) {
      setResult({ pass: false, message: String(e) });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="slide-container" style={{ padding: '20px 40px' }}>
      <div className="slide-inner">
        <Badge variant="day2">Context Engineering 실습</Badge>
        <SlideH2>과제: 회의록을 200자로 압축</SlideH2>
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
              압축 프롬프트 ({compressed.length}/200자)
            </div>
            <textarea
              value={compressed} onChange={e => setCompressed(e.target.value)}
              placeholder="핵심만 남겨서 200자 이내로 압축하세요..."
              style={{
                width: '100%', height: 200, padding: 12, borderRadius: 8,
                border: `1.5px solid ${compressed.length > 200 ? '#ef4444' : '#d1d5db'}`,
                fontSize: '.82em', lineHeight: 1.5, resize: 'none', fontFamily: 'inherit',
              }}
            />
            <button onClick={handleTest} disabled={testing || !compressed.trim() || compressed.length > 200}
              style={{
                marginTop: 8, padding: '8px 20px', borderRadius: 8, border: 'none', width: '100%',
                background: compressed.trim() && compressed.length <= 200 ? '#7c3aed' : '#e2e8f0',
                color: compressed.trim() && compressed.length <= 200 ? '#fff' : '#94a3b8',
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
            {result.raw && (
              <details style={{ marginTop: 6, fontSize: '.8em' }}>
                <summary style={{ cursor: 'pointer', color: '#64748b' }}>LLM Raw Output</summary>
                <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: 8, borderRadius: 6,
                  overflow: 'auto', maxHeight: 100, whiteSpace: 'pre-wrap', marginTop: 4 }}>{result.raw}</pre>
              </details>
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

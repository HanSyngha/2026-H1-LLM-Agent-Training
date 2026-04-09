import { useState } from 'react';
import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, CodeBlock } from './SlideLayout';
import { postJSON } from '../api';
import AnswerButton from './AnswerButton';

const CHAT_LOG = `[팀 메신저 대화 기록 — 2026-03-18~03-22]

김태호: 안녕하세요 다들 주간 상황 공유 부탁드립니다
오정훈: HBM4 시제품 테스트 결과 나왔는데 열저항 문제가 예상보다 심각합니다. TIM 소재 변경이 시급합니다.
김태호: 그래핀 TIM 샘플은 언제 나오나요?
오정훈: A사에서 4월 10일에 보내준다고 합니다
이수진: 테스트 장비는 제가 이미 발주했어요. 6월 도착 예정입니다.
김태호: 수고하셨습니다
정민호: 1c 파일럿 라인 클린룸 업그레이드 견적 받았습니다. 23억원이에요.
김태호: 승인 요청 올려주세요. 이번 주 금요일까지.
정민호: 네 알겠습니다!
한지원: 다음 주 월요일에 부사장님 주간보고가 있어서 자료 준비해야 합니다
김태호: 오정훈 팀장님이 HBM4 현황, 제가 1c 전환 현황 정리할게요
오정훈: 넵 화요일까지 자료 보내드리겠습니다
이수진: 참고로 ASML에서 EUV 장비 가동률 개선 방안 미팅 요청이 왔습니다. 3월 25일로 잡을까요?
김태호: 좋습니다. 제가 참석하겠습니다.
정민호: 저도 같이 참석하고 싶습니다
김태호: 네 같이 가시죠
한지원: 아 그리고 지난주 PIM 회의 회의록 아직 배포가 안됐는데요
오정훈: 제가 검토 중인데 내용이 좀 많아서... 수요일까지 마무리하겠습니다
김태호: 서둘러주세요. 박상무님이 기다리고 계십니다
한지원: EUV 장비 추가 도입 건 구매팀에 요청서 넣었습니다. 납기 확인 중이에요.
이수진: 참 그리고 HBM4 테스트 중에 범프 접합 불량이 3건 발견됐어요. 분석 중입니다.
오정훈: 그건 심각한데요. 원인 파악되면 바로 공유해주세요
이수진: 네 이번 주 내로 분석 완료할게요
정민호: 클린룸 업그레이드 승인 받았습니다! 4월 1일 착공 예정이에요
김태호: 잘됐네요 👍
한지원: 부사장님 보고 자료 템플릿 보내드렸어요. 확인해주세요
김태호: 확인했어요 감사합니다
오정훈: 범프 접합 불량 원인 나왔습니다. 리플로우 온도 프로파일이 사양 벗어났었네요.
이수진: 온도 프로파일 재설정했습니다. 재테스트 진행하겠습니다.
김태호: 다음 주 주요 일정 정리해봅시다
한지원: 월요일: 부사장님 주간보고, 화요일: 오정훈 팀장 자료 마감, 수요일: PIM 회의록 배포, 금요일: ASML 미팅(3/25)
김태호: 아 ASML 미팅이 금요일이 아니라 화요일 25일이에요
한지원: 아 맞다 3월 25일이 화요일이죠. 수정하겠습니다
오정훈: 그리고 목요일에 그래핀 TIM 관련 논문 리뷰 미팅 잡았습니다. 관심있는 분 참석해주세요.
이수진: 저 참석할게요!
정민호: 저도요
김태호: 좋습니다. 이번 주 고생 많으셨습니다. 다들 주말 잘 보내세요!`;

export default function Slide81b_ChatExtractTask() {
  const [summary, setSummary] = useState('');
  const [result, setResult] = useState(null);
  const [testing, setTesting] = useState(false);

  const handleTest = async () => {
    setTesting(true); setResult(null);
    try {
      const r = await postJSON('/challenges/chat_extract/test', { summary });
      setResult(r);
      if (r.pass) {
        try { await postJSON('/challenges/chat_extract/submit', { answer: { summary } }); } catch {}
      }
    } catch (e) { setResult({ pass: false, message: String(e) }); } finally { setTesting(false); }
  };

  return (
    <div className="slide-container" style={{ padding: '20px 40px' }}>
      <div className="slide-inner">
        <Badge variant="day2">Context Engineering 실습</Badge>
        <SlideH2>과제: 채팅 기록에서 핵심 정보 추출</SlideH2>
        <Divider />

        <div style={{ display: 'flex', gap: 14 }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: '.85em', marginBottom: 6, color: '#64748b' }}>
              팀 메신저 대화 ({CHAT_LOG.length}자)
            </div>
            <div style={{
              background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8,
              padding: 12, fontSize: '.72em', lineHeight: 1.5, maxHeight: 300, overflowY: 'auto',
              whiteSpace: 'pre-wrap', color: '#334155',
            }}>
              {CHAT_LOG}
            </div>
          </div>

          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: '.85em', marginBottom: 6, color: '#7c3aed' }}>
              요약 ({summary.length}/300자)
            </div>
            <textarea value={summary} onChange={e => setSummary(e.target.value)}
              placeholder="일정, 할 일, 완료한 일, 결정사항을 빠짐없이 정리하세요..."
              style={{
                width: '100%', height: 220, padding: 12, borderRadius: 8,
                border: `1.5px solid ${summary.length > 300 ? '#ef4444' : '#d1d5db'}`,
                fontSize: '.82em', lineHeight: 1.5, resize: 'none', fontFamily: 'inherit',
              }} />
            <button onClick={handleTest} disabled={testing || !summary.trim() || summary.length > 300}
              style={{
                marginTop: 8, padding: '8px 20px', borderRadius: 8, border: 'none', width: '100%',
                background: summary.trim() && summary.length <= 300 ? '#7c3aed' : '#e2e8f0',
                color: summary.trim() && summary.length <= 300 ? '#fff' : '#94a3b8',
                fontWeight: 700, fontSize: '.9em', cursor: 'pointer',
              }}>
              {testing ? 'AI 검증 중...' : '🧪 AI에게 핵심 정보 확인시키기'}
            </button>
          </div>
        </div>

        {result && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            style={{ marginTop: 10, padding: 12, borderRadius: 10,
              background: result.pass ? '#f0fdf4' : '#fef2f2',
              border: `1px solid ${result.pass ? '#86efac' : '#fca5a5'}` }}>
            <div style={{ fontWeight: 700, color: result.pass ? '#059669' : '#dc2626', marginBottom: 6 }}>
              {result.pass ? '🎉 ' : '❌ '}{result.message}
            </div>
            {result.checks && result.checks.map((c, i) => (
              <div key={i} style={{ fontSize: '.85em', padding: '2px 0' }}>
                {c.matched ? '✅' : '❌'} {c.item}
              </div>
            ))}
            {result.raw && (
              <details style={{ marginTop: 6, fontSize: '.8em' }}>
                <summary style={{ cursor: 'pointer', color: '#64748b' }}>LLM Raw Output</summary>
                <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: 8, borderRadius: 6,
                  overflow: 'auto', maxHeight: 100, whiteSpace: 'pre-wrap', marginTop: 4 }}>{result.raw}</pre>
              </details>
            )}
          </motion.div>
        )}

        <AnswerButton answerId="chat_extract">
          <div>
            <h3 style={{ color: '#1e293b', marginBottom: 8 }}>예시 요약 (5/5 통과)</h3>
            <CodeBlock lang="text">{`일정: 3/25(화) ASML EUV미팅(김태호,정민호), 월요일 부사장 주간보고, 목요일 그래핀TIM 논문리뷰
완료: 클린룸 승인(4/1착공), 테스트장비 발주(6월도착), 범프불량 원인파악(리플로우온도)→재테스트
할일: 그래핀TIM 샘플(4/10), PIM회의록 수요일배포, HBM4/1c 보고자료 화요일마감`}</CodeBlock>
          </div>
        </AnswerButton>
      </div>
    </div>
  );
}

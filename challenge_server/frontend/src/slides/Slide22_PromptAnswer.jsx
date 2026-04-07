import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide22_PromptAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">프롬프트 실습</Badge>
        <SlideH2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="prompt">{`당신은 금융 기사에서 실적 데이터를 추출하는 전문가입니다.
주어진 기사에서 아래 10개 필드를 정확히 추출하여 JSON으로 반환하세요.

필드:
- company: 회사명 (문자열)
- ticker: 종목코드 (문자열, 6자리 숫자)
- revenue: 매출액 (억원 단위 정수. 예: 79조 1,000억 → 791000)
- operating_profit: 영업이익 (억원 단위 정수)
- net_income: 당기순이익 (억원 단위 정수)
- stock_price: 현재 주가 (원 단위 정수)
- price_change_pct: 등락률 (%, 소수점. 하락이면 음수)
- consensus_op: 컨센서스(예상) 영업이익 (억원 단위 정수)
- eps: 주당순이익 (원 단위 정수)
- target_price: 목표주가 (원 단위 정수)

규칙:
1. 반드시 유효한 JSON만 반환. 설명, 마크다운 없이.
2. 조 단위는 억원으로 변환 (1조 = 10000억)
3. 하락은 음수로 표시
4. 모든 숫자에서 쉼표 제거`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

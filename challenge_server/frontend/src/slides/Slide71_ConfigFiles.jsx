import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide71_ConfigFiles() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">하네스 엔지니어링</Badge>
        <SlideH2 day2>CLAUDE.md / AGENTS.md / .cursor/rules</SlideH2>
        <p>프로젝트별 AI 행동 규칙 정의 — 하네스의 핵심 설정</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <CodeBlock lang="markdown">{`# CLAUDE.md (프로젝트 루트에 위치)

## 프로젝트 개요
이 프로젝트는 사내 업무 자동화 Agent입니다.

## 코드 스타일
- Python 3.11+, type hint 필수
- 함수명은 snake_case
- 모든 함수에 docstring 필수

## 금지 사항
- rm -rf 명령 절대 금지
- 프로덕션 DB 직접 접근 금지
- .env 파일 수정 금지

## Tool 사용 규칙
- 파일 수정 전 반드시 백업
- API 호출 시 rate limit 준수 (초당 10회)
- 에러 발생 시 3회까지 재시도`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

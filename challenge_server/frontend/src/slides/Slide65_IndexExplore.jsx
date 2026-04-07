import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide65_IndexExplore() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">검색 전략</Badge>
        <SlideH2 day2>Index Explore: 코드 탐색 방식</SlideH2>
        <p>Claude Code 방식 — grep / glob / AST 기반 정확한 탐색</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <CodeBlock>{`# 파일 구조 탐색
def glob_search(pattern: str) -> list:
    """패턴에 맞는 파일 목록 반환"""
    return glob.glob(pattern, recursive=True)

# 내용 검색
def grep_search(pattern: str, path: str) -> list:
    """정규식으로 파일 내용 검색"""
    result = subprocess.run(
        ["grep", "-rn", pattern, path],
        capture_output=True, text=True
    )
    return result.stdout.splitlines()

# 파일 읽기
def read_file(path: str, start: int, end: int) -> str:
    """파일의 특정 범위만 읽기"""
    lines = open(path).readlines()[start:end]
    return "".join(lines)`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide62_BashTool() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">bash Agent</Badge>
        <SlideH2 day2>subprocess로 Tool 만들기</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock>{`import subprocess

def run_command(command: str, timeout: int = 30) → dict:
    """쉘 명령어를 실행하고 결과를 반환합니다."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=ALLOWED_DIR,  # 작업 디렉토리 제한
        )
        return {
            "stdout": result.stdout[:5000],
            "stderr": result.stderr[:2000],
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": "명령어 실행 시간 초과"}`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

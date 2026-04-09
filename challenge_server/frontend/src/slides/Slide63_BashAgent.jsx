import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide63_BashAgent() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">bash Agent</Badge>
        <SlideH2 day2>안전장치: 허용 명령어 & 경로 제한</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock>{`# 화이트리스트 기반 명령어 필터
ALLOWED_COMMANDS = {"ls", "cat", "grep", "find", "head",
                    "wc", "python", "pip", "git"}
BLOCKED_PATTERNS = ["rm -rf", "sudo", ":(){:|:&}", "dd if="]
ALLOWED_DIR = "/home/user/workspace"

def validate_command(cmd: str) → bool:
    # 1. 위험 패턴 차단
    for pattern in BLOCKED_PATTERNS:
        if pattern in cmd:
            return False

    # 2. 첫 번째 명령어가 허용 목록에 있는지
    base_cmd = cmd.split()[0].split("/")[-1]
    if base_cmd not in ALLOWED_COMMANDS:
        return False

    # 3. 경로 이탈 방지
    if ".." in cmd or cmd.startswith("/"):
        return False
    return True`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

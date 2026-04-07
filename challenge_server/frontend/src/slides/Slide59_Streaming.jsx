import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide59_Streaming() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agentic Loop</Badge>
        <SlideH2 day2>Streaming (SSE) 처리</SlideH2>
        <p>Server-Sent Events — 응답을 실시간으로 받아 UX 개선</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <CodeBlock>{`# Streaming 요청
resp = requests.post(
    "https://gateway.company.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={"model": "claude-sonnet-4-20250514", "messages": msgs,
          "stream": True},  # ← 스트리밍 활성화
    stream=True,
)

# SSE 파싱
for line in resp.iter_lines():
    if line.startswith(b"data: "):
        data = json.loads(line[6:])
        if data == "[DONE]":
            break
        delta = data["choices"][0]["delta"]
        if "content" in delta:
            print(delta["content"], end="", flush=True)`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

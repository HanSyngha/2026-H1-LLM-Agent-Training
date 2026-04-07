import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide56_RequestsImpl() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agentic Loop</Badge>
        <SlideH2 day2>requests로 직접 구현</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock>{`import requests, json

def agent_loop(user_msg, tools, max_iter=10):
    messages = [
        {"role": "system", "content": "당신은 도구를 사용하는 AI 어시스턴트입니다."},
        {"role": "user", "content": user_msg},
    ]

    for _ in range(max_iter):
        resp = requests.post(
            "https://gateway.company.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": "claude-sonnet-4-20250514",
                  "messages": messages, "tools": tools}
        ).json()

        choice = resp["choices"][0]
        msg = choice["message"]
        messages.append(msg)

        if choice["finish_reason"] == "stop":
            return msg["content"]  # 최종 응답!

        if msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                result = execute_tool(tc)
                messages.append({"role": "tool",
                    "tool_call_id": tc["id"], "content": json.dumps(result)})`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

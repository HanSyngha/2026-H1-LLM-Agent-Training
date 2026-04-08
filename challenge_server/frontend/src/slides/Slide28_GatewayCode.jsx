import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide28_GatewayCode() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">OpenAI Compatible</Badge>
        <SlideH2>사내 Gateway 연결 코드 예시</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="python">{`import requests

# 사내 LLM Gateway (OpenAI Compatible + 커스텀 헤더)
resp = requests.post(
    "http://a2g.samsungds.net:8090/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "x-service-id": "test-service",   # 서비스 ID
        "x-user-id": "hong.gildong",      # SSO 사번
    },
    json={
        "model": "default",               # Gateway가 라우팅
        "messages": [
            {"role": "system", "content": "사내 업무 도우미입니다."},
            {"role": "user",   "content": "오늘 일정 알려줘"},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
    },
)

answer = resp.json()["choices"][0]["message"]["content"]
print(answer)`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide27_BaseURL() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">OpenAI Compatible</Badge>
        <SlideH2>base_url / api_key 구조</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="python">{`from openai import OpenAI

# OpenAI 직접 사용
client_openai = OpenAI(
    api_key="sk-...",
    # base_url 기본값: https://api.openai.com/v1
)

# 사내 Gateway — 커스텀 헤더 인증 방식!
client_gateway = OpenAI(
    base_url="https://llm-gateway.example.com/v1",
    api_key="not-needed",
    default_headers={
        "x-service-id": "test-service",
        "x-user-id": "<로그인한 user ID>",  # SSO 로그인 필수
    },
)

# vLLM / Ollama 로컬 사용 (역시 같은 코드!)
client_local = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed",
)`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock, Divider, Box, BoxTitle } from './SlideLayout';

export default function Slide28_GatewayCode() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">OpenAI Compatible</Badge>
        <SlideH2>원하는 Data를 뽑아내는 것이 시작입니다</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12 }}>
          <Box color="blue" style={{ marginBottom: 12 }}>
            <BoxTitle>핵심 메시지</BoxTitle>
            <div style={{ lineHeight: 1.75, fontSize: '.95em' }}>
              LLM을 다루기 시작할 때 가장 먼저 해야 할 일은 <strong>원하는 data를 정확히 뽑아내는 것</strong>입니다.<br />
              LLM의 가장 뛰어난 능력은 writing보다 <strong>reading</strong>에 가깝습니다.<br />
              문서, 메일, 회의록, 보고서를 읽히고 <strong>필요한 정보만 추출하게 하는 습관</strong>을 적극 활용하세요.
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="python">{`import requests

# 사내 LLM Gateway (OpenAI Compatible + 커스텀 헤더)
resp = requests.post(
    "http://a2g.samsungds.net:8090/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "x-service-id": "test-service",   # 서비스 ID
        "x-user-id": "<로그인한 user ID>",    # SSO 로그인 필수
    },
    json={
        "model": "testmodel",             # Gateway가 라우팅
        "messages": [
            {"role": "system", "content": "당신은 사내 문서에서 필요한 데이터를 정확히 추출하는 도우미입니다."},
            {"role": "user",   "content": "다음 회의 공지 메일에서 날짜, 시간, 참석자만 뽑아줘"},
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

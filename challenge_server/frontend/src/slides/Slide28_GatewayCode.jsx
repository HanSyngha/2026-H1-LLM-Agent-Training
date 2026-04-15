import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock, Divider, Box, BoxTitle } from './SlideLayout';

export default function Slide28_GatewayCode() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">OpenAI Compatible</Badge>
        <SlideH2>OpenAI Compatible 연결 코드</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12 }}>
          <Box color="blue" style={{ marginBottom: 12 }}>
            <BoxTitle>핵심 메시지</BoxTitle>
            <div style={{ lineHeight: 1.75, fontSize: '.95em' }}>
              OpenAI Compatible의 장점은 <strong>요청 형식이 널리 공유된다</strong>는 점입니다.<br />
              <strong>base_url, header, model</strong>만 맞추면 기존 코드를 거의 그대로 재사용할 수 있습니다.<br />
              핵심은 framework가 아니라 <strong>공통 request contract를 이해하는 것</strong>입니다.
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

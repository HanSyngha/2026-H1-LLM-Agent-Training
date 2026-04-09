import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, CodeBlock } from './SlideLayout';

export default function Slide76b_ReactSetup() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">부록</Badge>
        <SlideH2>Windows에서 React 프로젝트 시작하기</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue" style={{ fontSize: '.82em', padding: '14px 20px' }}>
            <BoxTitle>1. Node.js 설치</BoxTitle>
            <CodeBlock lang="powershell">{`# https://nodejs.org 에서 LTS 버전 다운로드 & 설치
# 설치 후 확인:
node --version   # v22.x.x
npm --version    # 10.x.x

# 사내망이라 npm registry 변경 필요:
npm config set registry https://repo.samsungds.net/artifactory/api/npm/npm-remote/
npm config set strict-ssl false`}</CodeBlock>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '.82em', padding: '14px 20px' }}>
            <BoxTitle color="#059669">2. React 프로젝트 생성</BoxTitle>
            <CodeBlock lang="powershell">{`# Vite로 React 프로젝트 생성 (가장 빠름)
npm create vite@latest my-chatbot -- --template react
cd my-chatbot
npm install
npm run dev
# → http://localhost:5173 에서 확인`}</CodeBlock>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="purple" style={{ marginTop: 8, fontSize: '.82em', padding: '14px 20px' }}>
            <BoxTitle color="#7c3aed">3. LLM 챗봇으로 확장</BoxTitle>
            <CodeBlock lang="javascript">{`// src/App.jsx에서 LLM 호출 예시
const resp = await fetch("http://a2g.samsungds.net:8090/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "x-service-id": "test-service",
    "x-user-id": "your-id",
  },
  body: JSON.stringify({
    model: "testmodel",
    messages: [{ role: "user", content: userInput }],
  }),
});
const data = await resp.json();
const answer = data.choices[0].message.content;`}</CodeBlock>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }}>
          <Box color="yellow" style={{ marginTop: 8, textAlign: 'center', fontSize: '.92em' }}>
            <strong>Tip:</strong> Google Stitch로 UI 디자인 → 코드 내보내기 → React에 붙이기!
          </Box>
        </motion.div>
      </div>
    </div>
  );
}

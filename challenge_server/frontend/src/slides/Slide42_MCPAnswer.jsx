import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide42_MCPAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">MCP 실습</Badge>
        <SlideH2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="prompt">{`FastMCP 클라이언트로 MCP 서버에 연결해줘.

1. python day1/01_mcp/mcp_server.py 로 서버 실행 (별도 터미널)
2. FastMCP Client로 연결
3. 3개 도구 호출: add(157,289), get_weather("서울"), search_employee("김")
4. POST /challenges/mcp/submit 에 제출
   {"token":"SSO토큰","answer":{"results":["결과1","결과2","결과3"]}}

from fastmcp import Client
async with Client("mcp_server.py") as client:
    result = await client.call_tool("add", {"a":157, "b":289})`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

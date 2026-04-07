import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide39_FastMCP() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">MCP</Badge>
        <SlideH2>FastMCP 서버 코드 예시</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="python">{`from fastmcp import FastMCP

mcp = FastMCP("사내 도구 서버")

@mcp.tool()
def search_employee(name: str) -> dict:
    """직원 이름으로 인사정보를 검색합니다."""
    # SSO API 호출
    result = sso_api.search(name)
    return {"name": result.name, "dept": result.dept}

@mcp.tool()
def book_meeting_room(room: str, time: str) -> str:
    """회의실을 예약합니다."""
    return booking_api.reserve(room, time)

# 서버 실행
mcp.run()  # stdio 또는 SSE 모드로 실행`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}

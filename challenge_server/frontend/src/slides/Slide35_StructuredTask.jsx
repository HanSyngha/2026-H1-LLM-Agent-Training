import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';
import AnswerButton from './AnswerButton';
import Slide36_StructuredAnswer from './Slide36_StructuredAnswer';

export default function Slide35_StructuredTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Tool Use 실습</Badge>
        <SlideH2>바이브 코딩: Function Calling 챗봇</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue">
            <BoxTitle>1단계: 코드 다운로드 & 실행</BoxTitle>
            <a href="/downloads/tool_use" download
              style={{ display: 'inline-block', padding: '8px 20px', borderRadius: 8, background: '#2563eb', color: '#fff',
                textDecoration: 'none', fontWeight: 600, fontSize: '.9em', marginBottom: 8 }}>
              📦 실습 코드 다운로드 (tool_use_code.zip)
            </a>
            <code style={{ display: 'block', fontSize: '1em', lineHeight: 1.8 }}>
              pip install streamlit requests PyJWT<br />
              streamlit run app.py --server.port 3000
            </code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.85em', padding: '16px 24px' }}>
            <BoxTitle color="#d97706">2단계: TODO 2개 채우기</BoxTitle>
            <div style={{ lineHeight: 1.7 }}>
              <strong>TODO 1 — tools 스키마</strong>: OpenAI Function Calling 형식<br />
              <code style={{ fontSize: '.85em' }}>{'[{"type":"function","function":{"name":"...","description":"...","parameters":{"type":"object","properties":{...},"required":[...]}}}]'}</code><br />
              <strong style={{ marginTop: 4, display: 'inline-block' }}>TODO 2 — execute_tool()</strong>: tool_name에 따라 API 호출 후 resp.json() 반환
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="purple" style={{ marginTop: 8, fontSize: '.82em', padding: '16px 24px' }}>
            <strong>Tool 정보</strong>
            <table style={{ fontSize: '.9em', margin: '6px 0 0', width: '100%' }}>
              <tbody>
                <tr>
                  <th style={{ width: '25%', padding: '3px 8px' }}>get_secret_key</th>
                  <td style={{ padding: '3px 8px' }}>
                    <code>GET {'{CHALLENGE_SERVER}'}/challenges/tool_use/secret?token={'{token}'}</code><br />
                    파라미터 없음 / 응답: <code>{'{"secret_key":"KEY-..."}'}</code>
                  </td>
                </tr>
                <tr>
                  <th style={{ padding: '3px 8px' }}>submit_secret_key</th>
                  <td style={{ padding: '3px 8px' }}>
                    <code>POST {'{CHALLENGE_SERVER}'}/challenges/tool_use/submit</code><br />
                    파라미터: <code>secret_key</code> (string) / body: <code>{'{"token":token,"answer":{"secret_key":"..."}}'}</code>
                  </td>
                </tr>
              </tbody>
            </table>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '.95em' }}>
            <strong>성공 조건:</strong> LLM이 Tool 2개를 연속 호출 →{' '}
            <code>get_secret_key</code> → <code>submit_secret_key</code> → <strong style={{ color: '#059669' }}>자동 통과!</strong>
            <div style={{ marginTop: 8, fontSize: '.85em', color: '#64748b' }}>
              챗봇에 "과제 제출해줘"라고 입력하면 LLM이 알아서 Tool을 호출합니다.
            </div>
          </Box>
        </motion.div>

        <AnswerButton answerId="tool_use"><Slide36_StructuredAnswer /></AnswerButton>
      </div>
    </div>
  );
}

import Slide01_Title from './Slide01_Title';
import Slide02_Agenda from './Slide02_Agenda';
import Slide03_Day1Header from './Slide03_Day1Header';
import SectionSSO from './SectionSSO';
import Slide04_SSO from './Slide04_SSO';
import Slide05_SSOChallenge from './Slide05_SSOChallenge';
import Slide06_SSOStructure from './Slide06_SSOStructure';
import Slide07_SSOTips from './Slide07_SSOTips';
import Slide08_OAuth2Flow from './Slide08_OAuth2Flow';
import Slide09_OIDCDiff from './Slide09_OIDCDiff';
import Slide10_WhyTheory from './Slide10_WhyTheory';
import Slide11_SSOLabIntro from './Slide11_SSOLabIntro';
import Slide12_SSOTask1 from './Slide12_SSOTask1';
import Slide13_SSOTask2 from './Slide13_SSOTask2';
import Slide14_SSOTaskOIDC from './Slide14_SSOTaskOIDC';
import Slide15_SSOAnswer from './Slide15_SSOAnswer';
import SectionAI from './SectionAI';
import Slide16_AILearning1 from './Slide16_AILearning1';
import Slide17_AILearning2 from './Slide17_AILearning2';
import SectionPrompt from './SectionPrompt';
import Slide18_Prompt1 from './Slide18_Prompt1';
import Slide19_Prompt2 from './Slide19_Prompt2';
import Slide20_ContextEng from './Slide20_ContextEng';
import Slide21_PromptTask from './Slide21_PromptTask';
import Slide22_PromptAnswer from './Slide22_PromptAnswer';
import SectionAPI from './SectionAPI';
import Slide23_APIBasic from './Slide23_APIBasic';
import Slide24_APITool from './Slide24_APITool';
import Slide25_OpenAICompat from './Slide25_OpenAICompat';
import Slide26_Gateway from './Slide26_Gateway';
import Slide27_BaseURL from './Slide27_BaseURL';
import Slide28_GatewayCode from './Slide28_GatewayCode';
import Slide29_EndpointTask from './Slide29_EndpointTask';
import Slide30_EndpointAnswer from './Slide30_EndpointAnswer';
import SectionStructured from './SectionStructured';
import Slide31_JSONvsStructured from './Slide31_JSONvsStructured';
import Slide32_StructuredExample from './Slide32_StructuredExample';
import Slide33_ToolCallingFlow from './Slide33_ToolCallingFlow';
import Slide34_ToolChoice from './Slide34_ToolChoice';
import Slide35_StructuredTask from './Slide35_StructuredTask';
import Slide36_StructuredAnswer from './Slide36_StructuredAnswer';
import SectionMCP from './SectionMCP';
import Slide37_MCP1 from './Slide37_MCP1';
import Slide38_MCPArch from './Slide38_MCPArch';
import Slide39_FastMCP from './Slide39_FastMCP';
import Slide40_MCPFlow from './Slide40_MCPFlow';
import Slide41_MCPTask from './Slide41_MCPTask';
import Slide42_MCPAnswer from './Slide42_MCPAnswer';
import SectionBrowser from './SectionBrowser';
import Slide43_BrowserCompare from './Slide43_BrowserCompare';
import Slide44_CDP from './Slide44_CDP';
import Slide45_Playwright from './Slide45_Playwright';
import Slide46_IframeCOM from './Slide46_IframeCOM';
import Slide47_BrowserTask from './Slide47_BrowserTask';
import Slide48_BrowserAnswer from './Slide48_BrowserAnswer';
import SectionDay1Lab from './SectionDay1Lab';
import Slide49_Day1Lab from './Slide49_Day1Lab';
import Slide50_Day2Header from './Slide50_Day2Header';
import SectionFramework from './SectionFramework';
import Slide51_ADK from './Slide51_ADK';
import Slide52_LangGraph from './Slide52_LangGraph';
import Slide53_FrameworkCompare from './Slide53_FrameworkCompare';
import Slide54_Trend from './Slide54_Trend';
import SectionAgenticLoop from './SectionAgenticLoop';
import Slide55_AgentLoop from './Slide55_AgentLoop';
import Slide56_RequestsImpl from './Slide56_RequestsImpl';
import Slide57_ToolCallsParse from './Slide57_ToolCallsParse';
import Slide58_MultiIteration from './Slide58_MultiIteration';
import Slide59_Streaming from './Slide59_Streaming';
import Slide60_AgentTask from './Slide60_AgentTask';
import Slide61_AgentAnswer from './Slide61_AgentAnswer';
import SectionBash from './SectionBash';
import Slide62_BashTool from './Slide62_BashTool';
import Slide63_BashAgent from './Slide63_BashAgent';
import SectionVectorDB from './SectionVectorDB';
import Slide64_SemanticSearch from './Slide64_SemanticSearch';
import Slide65_IndexExplore from './Slide65_IndexExplore';
import Slide66_VDBCompare from './Slide66_VDBCompare';
import SectionHarness from './SectionHarness';
import Slide67_WhatIsHarness from './Slide67_WhatIsHarness';
import Slide68_5Pillars from './Slide68_5Pillars';
import Slide69_ContextEng2 from './Slide69_ContextEng2';
import Slide70_Security from './Slide70_Security';
import Slide71_ConfigFiles from './Slide71_ConfigFiles';
import Slide72_RAG from './Slide72_RAG';
import SectionFinal from './SectionFinal';
import Slide73_FinalTask from './Slide73_FinalTask';
import Slide74_FinalAnswer from './Slide74_FinalAnswer';
import SectionWrapup from './SectionWrapup';
import Slide75_Summary from './Slide75_Summary';
import Slide76_Message from './Slide76_Message';
import Slide77_ThankYou from './Slide77_ThankYou';

const SLIDES = [
  // Intro
  { id: 1, component: Slide01_Title, title: 'LLM Agent 개발 실습', day: 0 },
  { id: 2, component: Slide02_Agenda, title: '전체 과정 구성', day: 0 },
  // Day 1
  { id: 3, component: Slide03_Day1Header, title: 'Day 1', day: 1 },
  { id: 4, component: SectionSSO, title: '#0 SSO', day: 1 },
  { id: 5, component: Slide04_SSO, title: 'SSO란?', day: 1 },
  { id: 6, component: Slide06_SSOStructure, title: '사내 SSO 구조', day: 1 },
  { id: 7, component: Slide07_SSOTips, title: '연동 신청 & 팁', day: 1 },
  { id: 8, component: Slide08_OAuth2Flow, title: 'OAuth2 흐름', day: 1 },
  { id: 9, component: Slide09_OIDCDiff, title: 'OIDC vs OAuth2', day: 1 },
  { id: 10, component: Slide10_WhyTheory, title: '왜 이론을 알아야 하는가', day: 1 },
  { id: 11, component: Slide11_SSOLabIntro, title: '실습 안내', day: 1 },
  { id: 12, component: Slide12_SSOTask1, title: '과제: SSO 연동 (1/2)', day: 1 },
  { id: 13, component: Slide13_SSOTask2, title: '서버 정보 & 제출', day: 1 },
  { id: 14, component: Slide14_SSOTaskOIDC, title: 'OIDC 차이점', day: 1 },
  { id: 15, component: Slide15_SSOAnswer, title: '예시 답안', day: 1 },
  // AI 학습
  { id: 16, component: SectionAI, title: '#2 AI 학습이란?', day: 1 },
  { id: 17, component: Slide16_AILearning1, title: '학습의 모호성', day: 1 },
  { id: 18, component: Slide17_AILearning2, title: '사내에서의 AI 활용', day: 1 },
  // 프롬프트
  { id: 19, component: SectionPrompt, title: '#3 프롬프트', day: 1 },
  { id: 20, component: Slide18_Prompt1, title: '프롬프트가 핵심', day: 1 },
  { id: 21, component: Slide19_Prompt2, title: 'system/user/assistant', day: 1 },
  { id: 22, component: Slide20_ContextEng, title: '컨텍스트 엔지니어링', day: 1 },
  { id: 23, component: Slide21_PromptTask, title: '프롬프트 과제', day: 1 },
  { id: 24, component: Slide22_PromptAnswer, title: '예시 답안', day: 1 },
  // API
  { id: 25, component: SectionAPI, title: '#4 API', day: 1 },
  { id: 26, component: Slide23_APIBasic, title: 'REST API란?', day: 1 },
  { id: 27, component: Slide24_APITool, title: 'API를 Tool로', day: 1 },
  { id: 28, component: Slide25_OpenAICompat, title: 'OpenAI Compatible', day: 1 },
  { id: 29, component: Slide26_Gateway, title: 'Gateway 구조', day: 1 },
  { id: 30, component: Slide27_BaseURL, title: 'base_url / api_key', day: 1 },
  { id: 31, component: Slide28_GatewayCode, title: '연결 코드', day: 1 },
  { id: 32, component: Slide29_EndpointTask, title: 'Endpoint 과제', day: 1 },
  { id: 33, component: Slide30_EndpointAnswer, title: '예시 답안', day: 1 },
  // Structured Output
  { id: 34, component: SectionStructured, title: '#5 Structured Output', day: 1 },
  { id: 35, component: Slide31_JSONvsStructured, title: 'JSON vs Structured', day: 1 },
  { id: 36, component: Slide32_StructuredExample, title: 'Structured 예시', day: 1 },
  { id: 37, component: Slide33_ToolCallingFlow, title: 'Tool Calling 흐름', day: 1 },
  { id: 38, component: Slide34_ToolChoice, title: 'tool_choice', day: 1 },
  { id: 39, component: Slide35_StructuredTask, title: 'Structured 과제', day: 1 },
  { id: 40, component: Slide36_StructuredAnswer, title: '예시 답안', day: 1 },
  // MCP
  { id: 41, component: SectionMCP, title: '#6 MCP', day: 1 },
  { id: 42, component: Slide37_MCP1, title: 'MCP 개요', day: 1 },
  { id: 43, component: Slide38_MCPArch, title: 'MCP 아키텍처', day: 1 },
  { id: 44, component: Slide39_FastMCP, title: 'FastMCP 코드', day: 1 },
  { id: 45, component: Slide40_MCPFlow, title: 'MCP+LLM 연동', day: 1 },
  { id: 46, component: Slide41_MCPTask, title: 'MCP 과제', day: 1 },
  { id: 47, component: Slide42_MCPAnswer, title: '예시 답안', day: 1 },
  // 브라우저
  { id: 48, component: SectionBrowser, title: '#7 브라우저', day: 1 },
  { id: 49, component: Slide43_BrowserCompare, title: '브라우저 비교', day: 1 },
  { id: 50, component: Slide44_CDP, title: 'CDP 구조', day: 1 },
  { id: 51, component: Slide45_Playwright, title: 'Playwright', day: 1 },
  { id: 52, component: Slide46_IframeCOM, title: 'iframe/COM', day: 1 },
  { id: 53, component: Slide47_BrowserTask, title: '브라우저 과제', day: 1 },
  { id: 54, component: Slide48_BrowserAnswer, title: '예시 답안', day: 1 },
  // Day 1 실습
  { id: 55, component: SectionDay1Lab, title: 'Day 1 실습', day: 1 },
  { id: 56, component: Slide49_Day1Lab, title: '바이브 코딩 실습', day: 1 },
  // Day 2
  { id: 57, component: Slide50_Day2Header, title: 'Day 2', day: 2 },
  { id: 58, component: SectionFramework, title: '#8 Framework', day: 2 },
  { id: 59, component: Slide51_ADK, title: 'Google ADK', day: 2 },
  { id: 60, component: Slide52_LangGraph, title: 'LangGraph', day: 2 },
  { id: 61, component: Slide53_FrameworkCompare, title: '프레임워크 비교', day: 2 },
  { id: 62, component: Slide54_Trend, title: '트렌드', day: 2 },
  { id: 63, component: SectionAgenticLoop, title: '#9 Agentic Loop', day: 2 },
  { id: 64, component: Slide55_AgentLoop, title: 'Agent Loop 패턴', day: 2 },
  { id: 65, component: Slide56_RequestsImpl, title: 'requests 구현', day: 2 },
  { id: 66, component: Slide57_ToolCallsParse, title: 'tool_calls 파싱', day: 2 },
  { id: 67, component: Slide58_MultiIteration, title: 'Multi-iteration', day: 2 },
  { id: 68, component: Slide59_Streaming, title: 'Streaming', day: 2 },
  { id: 69, component: Slide60_AgentTask, title: 'Agent Loop 과제', day: 2 },
  { id: 70, component: Slide61_AgentAnswer, title: '예시 답안', day: 2 },
  { id: 71, component: SectionBash, title: '#10 bash Agent', day: 2 },
  { id: 72, component: Slide62_BashTool, title: 'subprocess Tool', day: 2 },
  { id: 73, component: Slide63_BashAgent, title: 'CLI Agent', day: 2 },
  { id: 74, component: SectionVectorDB, title: '#11 Vector DB', day: 2 },
  { id: 75, component: Slide64_SemanticSearch, title: 'Semantic Search', day: 2 },
  { id: 76, component: Slide65_IndexExplore, title: 'Index Explore', day: 2 },
  { id: 77, component: Slide66_VDBCompare, title: '비교', day: 2 },
  { id: 78, component: SectionHarness, title: '#12 하네스', day: 2 },
  { id: 79, component: Slide67_WhatIsHarness, title: '하네스란?', day: 2 },
  { id: 80, component: Slide68_5Pillars, title: '5대 요소', day: 2 },
  { id: 81, component: Slide69_ContextEng2, title: '컨텍스트 엔지니어링', day: 2 },
  { id: 82, component: Slide70_Security, title: '보안 5계층', day: 2 },
  { id: 83, component: Slide71_ConfigFiles, title: 'CLAUDE.md', day: 2 },
  { id: 84, component: Slide72_RAG, title: 'RAG 파이프라인', day: 2 },
  { id: 85, component: SectionFinal, title: '종합 실습', day: 2 },
  { id: 86, component: Slide73_FinalTask, title: '종합 과제', day: 2 },
  { id: 87, component: Slide74_FinalAnswer, title: '예시 답안', day: 2 },
  { id: 88, component: SectionWrapup, title: '마무리', day: 2 },
  { id: 89, component: Slide75_Summary, title: '학습 정리', day: 2 },
  { id: 90, component: Slide76_Message, title: '핵심 메시지', day: 2 },
  { id: 91, component: Slide77_ThankYou, title: '감사합니다', day: 2 },
];

export default SLIDES;

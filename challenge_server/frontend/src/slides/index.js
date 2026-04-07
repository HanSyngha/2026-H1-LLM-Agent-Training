import Slide01_Title from './Slide01_Title';
import Slide02_Agenda from './Slide02_Agenda';
import Slide03_Day1Header from './Slide03_Day1Header';
import Slide04_SSO from './Slide04_SSO';
import Slide05_SSOChallenge from './Slide05_SSOChallenge';

const SLIDES = [
  { id: 1, component: Slide01_Title, title: 'LLM Agent 개발 실습', day: 0 },
  { id: 2, component: Slide02_Agenda, title: '전체 과정 구성', day: 0 },
  { id: 3, component: Slide03_Day1Header, title: 'Day 1', day: 1 },
  { id: 4, component: Slide04_SSO, title: 'SSO란?', day: 1 },
  { id: 5, component: Slide05_SSOChallenge, title: 'SSO 과제', day: 1 },
];

export default SLIDES;

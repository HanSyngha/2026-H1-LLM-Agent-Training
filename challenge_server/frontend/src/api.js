const API = window.location.origin;

export async function fetchJSON(path, options = {}) {
  const resp = await fetch(`${API}${path}`, {
    credentials: 'include',
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  });
  return resp.json();
}

export async function postJSON(path, body) {
  return fetchJSON(path, { method: 'POST', body: JSON.stringify(body) });
}

export async function getMe() {
  try {
    const resp = await fetch(`${API}/auth/me`, { credentials: 'include' });
    if (resp.ok) return resp.json();
    return null;
  } catch { return null; }
}

export async function getChallenges() { return fetchJSON('/challenges'); }
export async function getCompletions() { return fetchJSON('/completions'); }
export async function resetCompletions() { return postJSON('/completions/reset', {}); }
export async function getPromptCases() { return fetchJSON('/challenges/prompt/cases'); }

export async function testPrompt(prompt, caseId) {
  return postJSON('/challenges/prompt/test', { prompt, case_id: caseId });
}

export async function submitPrompt(prompt) {
  return postJSON('/challenges/prompt/submit', { prompt });
}

export async function submitChallenge(challengeId, answer) {
  return postJSON(`/challenges/${challengeId}/submit`, { answer });
}

export async function sendReaction(slideNum, type) {
  return postJSON('/reactions', { slide: slideNum, type });
}

export async function getReactions(slideNum) {
  return fetchJSON(`/reactions?slide=${slideNum}`);
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    let message = 'Request failed';
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  return response.json();
}

export function getLeagues() {
  return request('/leagues');
}

export function getTeams(league) {
  return request(`/teams?league=${encodeURIComponent(league)}`);
}

export function getNews({ league, team, range }) {
  const query = new URLSearchParams({ league, team, range });
  return request(`/news?${query.toString()}`);
}

export function summarize({ league, team, articles }) {
  return request('/summarize', {
    method: 'POST',
    body: JSON.stringify({ league, team, articles })
  });
}


export async function getSourceStatus() {
  return request("/source-status");
}

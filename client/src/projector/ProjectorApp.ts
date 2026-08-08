import './projector.css';

const API_BASE = 'http://localhost:8000';
const ROUND_DURATION_SEC = 300;

interface ProjectorState {
  sessionId: string;
  timeLeft: number;
  status: string;
  staking: { candidate: string; amount: number }[];
  leaderboard: { name: string; score: number }[];
  bountyPhrase: string;
  round: number;
  revealOrder: string[];
}

export function initProjectorApp(root: HTMLElement) {
  let state: ProjectorState = {
    sessionId: '',
    timeLeft: ROUND_DURATION_SEC,
    status: 'uninitialized',
    staking: [
      { candidate: 'A', amount: 0 },
      { candidate: 'B', amount: 0 },
      { candidate: 'C', amount: 0 },
      { candidate: 'D', amount: 0 },
    ],
    leaderboard: [],
    bountyPhrase: '',
    round: 1,
    revealOrder: []
  };
  
  const autoStart = () => {
    state.sessionId = 'DEFAULT_SESSION';
    startPolling();
  };

  const render = () => {
    if (state.status === 'uninitialized') {
      return;
    }

    if (state.status === 'waiting' || state.status === 'complete') {
      root.innerHTML = `
        <div class="projector-container" style="justify-content: center; align-items: center;">
          <h1 class="headline" style="font-size: 8rem;">UNDERCOVER</h1>
          <p class="subheadline" style="font-size: 3rem;">${state.status.toUpperCase()}</p>
        </div>
      `;
      return;
    }

    if (state.status === 'reveal') {
      if (state.revealOrder.length === 0) {
        root.innerHTML = `
          <div class="projector-container" style="justify-content: center; align-items: center;">
            <h1 class="headline" style="font-size: 8rem; color: var(--color-accent);">THE REVEAL</h1>
            <p class="subheadline" style="font-size: 3rem;">Waiting for the host...</p>
          </div>
        `;
        return;
      }
      const latestReveal = state.revealOrder[state.revealOrder.length - 1];
      root.innerHTML = `
        <div class="projector-container" style="justify-content: center; align-items: center; background: radial-gradient(circle, var(--color-accent) 0%, var(--color-bg) 70%);">
          <h1 class="headline" style="font-size: 10rem; color: white; text-shadow: 0 0 20px rgba(0,0,0,0.5); animation: pulse 2s infinite;">REVEALED</h1>
          <p class="subheadline" style="font-size: 5rem; color: var(--color-text-primary); margin-top: 2rem;">Candidate <strong style="font-size: 7rem; color: white;">${latestReveal}</strong> is the AI!</p>
          <p style="margin-top: 3rem; font-size: 2.5rem; font-family: var(--font-body); color: rgba(255,255,255,0.7);">Revealed so far: ${state.revealOrder.join(', ')}</p>
        </div>
      `;
      return;
    }

    const totalStaked = state.staking.reduce((sum, item) => sum + item.amount, 0);

    root.innerHTML = `
      <div class="projector-container">
        <header class="projector-header">
          <div class="header-left">
            <h1 class="headline">ROUND ${state.round}</h1>
            <p class="subheadline">LIVE STAKING DISTRIBUTION</p>
          </div>
          <div class="projector-timer ${state.timeLeft <= 10 ? 'warning' : ''}">
            ${Math.floor(state.timeLeft / 60).toString().padStart(2, '0')}:${(state.timeLeft % 60).toString().padStart(2, '0')}
          </div>
        </header>

        <main class="projector-main">
          <!-- Staking Distribution -->
          <div class="projector-panel staking-distribution">
            <h2 class="panel-title">ROOM CONSENSUS</h2>
            <div class="bars-wrapper">
              ${state.staking.map(item => {
                const percentage = totalStaked === 0 ? 0 : (item.amount / totalStaked) * 100;
                return `
                  <div class="bar-container">
                    <div class="bar-header">
                      <span>CANDIDATE ${item.candidate}</span>
                      <span>${item.amount.toLocaleString()} coins (${Math.round(percentage)}%)</span>
                    </div>
                    <div class="bar-bg">
                      <div class="bar-fill" style="width: ${percentage}%"></div>
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          </div>

          <!-- Leaderboard -->
          <div class="projector-panel leaderboard-panel">
            <h2 class="panel-title">LEADERBOARD</h2>
            <div class="leaderboard-list">
              ${state.leaderboard.length === 0 ? '<p>No data</p>' : ''}
              ${state.leaderboard.map((team, idx) => `
                <div class="leaderboard-item">
                  <span class="team-name">#${idx + 1} ${team.name}</span>
                  <span class="team-score">${team.score.toLocaleString()}</span>
                </div>
              `).join('')}
            </div>
          </div>
        </main>

        ${state.bountyPhrase ? `
        <div class="bounty-banner">
          <h3>BOUNTY PHRASE</h3>
          <p class="bounty-phrase">"${state.bountyPhrase}"</p>
        </div>
        ` : ''}
      </div>
    `;
  };

  const startPolling = () => {
    window.setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/session/${state.sessionId}/state`);
        if (res.ok) {
          const data = await res.json();
          state.status = data.status;
          
          if (state.status.startsWith('round')) {
            state.round = parseInt(state.status.replace('round', '')) || 1;
            if (data.current_round_start_time) {
              const start = new Date(data.current_round_start_time + 'Z').getTime();
              const now = new Date().getTime();
              const elapsed = Math.floor((now - start) / 1000);
              state.timeLeft = Math.max(0, ROUND_DURATION_SEC - elapsed);
            }
          }
          
          if (data.reveal_order) {
            state.revealOrder = data.reveal_order;
          }

          if (data.current_round) {
             state.bountyPhrase = data.current_round.bounty_phrase || '';
             // For real staking updates, we would fetch /api/session/{session_id}/stats
             // We can just keep it 0 or mock it for now since backend doesn't aggregate them in /state
          }

          // In a real app we'd also fetch the live leaderboard and staking from another endpoint 
          // but for now, we just rely on the session state.

          render();
        }
      } catch(e) {
        console.error("Projector polling error", e);
      }
    }, 2000);
  };

  autoStart();
}


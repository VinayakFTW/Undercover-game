import './player.css';

const API_BASE = 'http://localhost:8000';
const TOTAL_COINS = 10000;
const ROUND_DURATION_SEC = 300; // 5 minutes
const SPEED_BONUS_SEC = 25; // As per the event spec speed bonus ends at 25 seconds

interface AppState {
  sessionId: string;
  teamId: string;
  allocations: number[];
  timeLeft: number;
  locked: boolean;
  status: string;
  currentRound: string;
  revealOrder: string[];
}

export function initPlayerApp(root: HTMLElement) {
  let state: AppState = {
    sessionId: '',
    teamId: '',
    allocations: [0, 0, 0, 0],
    timeLeft: ROUND_DURATION_SEC,
    locked: false,
    status: 'uninitialized',
    currentRound: '',
    revealOrder: []
  };

  const renderLogin = () => {
    root.innerHTML = `
      <div class="player-container flex-center" style="height: 100vh; flex-direction: column;">
        <h1 class="headline" style="font-size: 5rem; color: var(--color-accent); margin-bottom: 2rem;">JOIN SESSION</h1>
        <div style="background: rgba(0,0,0,0.5); padding: 3rem; border-radius: 12px; display: flex; flex-direction: column; gap: 1.5rem; width: 400px; max-width: 90%;">
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <label style="color: var(--color-text-secondary); font-family: var(--font-heading);">Team ID</label>
            <input type="text" id="login-team-id" placeholder="e.g. team_12345678" style="padding: 1rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: white; font-family: var(--font-body); font-size: 1.2rem;">
            <input type="hidden" id="login-session-id" value="DEFAULT_SESSION">
          </div>
          <button id="btn-join-session" style="background: var(--color-accent); color: white; border: none; padding: 1rem; border-radius: 6px; font-family: var(--font-heading); font-size: 1.5rem; cursor: pointer; margin-top: 1rem; transition: transform 0.2s;">Join Game</button>
        </div>
      </div>
    `;

    document.getElementById('btn-join-session')?.addEventListener('click', () => {
      const sId = (document.getElementById('login-session-id') as HTMLInputElement).value.trim();
      const tId = (document.getElementById('login-team-id') as HTMLInputElement).value.trim();
      
      if (!tId) {
        alert("Please enter a Team ID");
        return;
      }
      
      state.sessionId = sId;
      state.teamId = tId;
      state.status = 'loading';
      
      // Let's verify session exists
      fetch(`${API_BASE}/api/session/${sId}/state`).then(res => {
         if(res.ok) {
           startPolling();
           renderWaiting();
         } else {
           alert("Session not found or invalid!");
         }
      }).catch(() => alert("Network error"));
    });
  };

  const renderWaiting = () => {
    root.innerHTML = `
      <div class="player-container flex-center" style="height: 100vh; flex-direction: column;">
        <h1 class="headline" style="font-size: 5rem; color: var(--color-text-primary);">WAITING FOR HOST</h1>
        <p style="font-size: 2rem; color: var(--color-accent); font-family: var(--font-heading);">Please wait until the next round starts.</p>
        <p style="margin-top: 2rem; font-family: var(--font-body); color: var(--color-text-secondary);">Session: ${state.sessionId} | Team: ${state.teamId}</p>
      </div>
    `;
  };

  const renderReveal = () => {
    if (state.revealOrder.length === 0) {
      root.innerHTML = `
        <div class="player-container flex-center" style="height: 100vh; flex-direction: column;">
          <h1 class="headline" style="font-size: 5rem; color: var(--color-accent);">THE REVEAL</h1>
          <p style="font-size: 2rem; color: var(--color-text-primary); font-family: var(--font-heading);">Waiting for the host to reveal the AI...</p>
        </div>
      `;
      return;
    }

    const latestReveal = state.revealOrder[state.revealOrder.length - 1];
    root.innerHTML = `
      <div class="player-container flex-center" style="height: 100vh; flex-direction: column; background: radial-gradient(circle, var(--color-accent) 0%, var(--color-bg) 70%);">
        <h1 class="headline" style="font-size: 6rem; color: white; text-shadow: 0 0 20px rgba(0,0,0,0.5); animation: pulse 2s infinite;">REVEALED</h1>
        <p style="font-size: 3rem; color: var(--color-text-primary); font-family: var(--font-heading); margin-top: 2rem;">Candidate <strong style="font-size: 5rem; color: white;">${latestReveal}</strong> is the AI!</p>
        <p style="margin-top: 2rem; font-family: var(--font-body); color: rgba(255,255,255,0.7);">Revealed so far: ${state.revealOrder.join(', ')}</p>
      </div>
    `;
  };

  const renderGame = () => {
    const totalAllocated = state.allocations.reduce((a, b) => a + b, 0);
    const unallocated = TOTAL_COINS - totalAllocated;
    const isValid = totalAllocated === TOTAL_COINS;
    
    const timeElapsed = ROUND_DURATION_SEC - state.timeLeft;
    const isSpeedBonusActive = timeElapsed <= SPEED_BONUS_SEC;

    let roundName = 'ROUND 1: FIRST IMPRESSIONS';
    if (state.status === 'round2') roundName = 'ROUND 2: CROSS-EXAMINATION';
    if (state.status === 'round3') roundName = 'ROUND 3: PROMPT ENGINEERING JAILBREAK';

    root.innerHTML = `
      <div class="player-container">
        <header class="player-header">
          <div class="round-info">
            <h1>${roundName}</h1>
            <p>Allocate your starting pool of 10,000 Byte-Coins</p>
          </div>
          <div class="timer-container">
            <div class="timer-text ${state.timeLeft <= 10 && !state.locked ? 'warning' : ''}">
              ${Math.floor(state.timeLeft / 60).toString().padStart(2, '0')}:${(state.timeLeft % 60).toString().padStart(2, '0')}
            </div>
            <div class="speed-bonus ${isSpeedBonusActive && !state.locked ? 'active' : ''}">
              ⚡ Speed Bonus Active
            </div>
          </div>
        </header>

        <div class="balance-panel">
          <h2 style="color: var(--color-text-secondary); font-size: 1.5rem; text-transform: none;">Remaining Balance</h2>
          <div class="balance-amount ${totalAllocated === TOTAL_COINS ? 'complete' : ''}">
            ${unallocated.toLocaleString()} <span style="font-size: 2rem; color: var(--color-text-secondary);">Byte-Coins</span>
          </div>
        </div>

        <div class="candidates-grid">
          ${['A', 'B', 'C', 'D'].map((letter, index) => {
            const currentValue = state.allocations[index];
            return `
              <div class="candidate-card ${currentValue > 0 ? 'active-card' : ''}">
                <div class="candidate-avatar">${letter}</div>
                <h3 class="candidate-name">CANDIDATE ${letter}</h3>
                <div class="allocation-display">${currentValue.toLocaleString()}</div>
                <div class="slider-container">
                  <input type="range" min="0" max="${TOTAL_COINS}" value="${currentValue}" data-index="${index}" class="allocation-slider" ${state.locked ? 'disabled' : ''} />
                </div>
              </div>
            `;
          }).join('')}
        </div>

        <div class="action-area">
          <button class="btn-lock" id="lock-in-btn" ${!isValid || state.locked ? 'disabled' : ''} style="font-family: var(--font-heading); background: var(--color-accent); color: white; border: none; padding: 1.5rem 5rem; font-size: 2.5rem; border-radius: 50px; cursor: pointer;">
            ${state.locked ? 'LOCKED IN' : 'LOCK IN'}
          </button>
        </div>
      </div>
    `;

    attachEvents();
  };

  const attachEvents = () => {
    const sliders = root.querySelectorAll('.allocation-slider') as NodeListOf<HTMLInputElement>;
    sliders.forEach(slider => {
      slider.addEventListener('input', (e) => {
        if (state.locked) return;
        const target = e.target as HTMLInputElement;
        const index = parseInt(target.dataset.index!);
        let newValue = parseInt(target.value);
        
        const otherAllocations = state.allocations.reduce((sum, val, i) => i !== index ? sum + val : sum, 0);
        const maxAllowed = TOTAL_COINS - otherAllocations;
        
        if (newValue > maxAllowed) {
          newValue = maxAllowed;
          target.value = newValue.toString(); 
        }
        
        state.allocations[index] = newValue;
        updateDOMWithoutRender();
      });
    });

    const lockBtn = root.querySelector('#lock-in-btn') as HTMLButtonElement;
    if (lockBtn) {
      lockBtn.addEventListener('click', async () => {
        const total = state.allocations.reduce((a, b) => a + b, 0);
        if (total === TOTAL_COINS) {
          state.locked = true;
          lockBtn.innerText = 'LOCKED IN';
          lockBtn.disabled = true;
          
          const allocationsPayload = ['A', 'B', 'C', 'D'].map((cand, i) => ({
            candidate_id: cand,
            amount: state.allocations[i]
          }));
          
          const timeElapsed = ROUND_DURATION_SEC - state.timeLeft;
          
          try {
             await fetch(`${API_BASE}/api/round/allocate`, {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({
                 team_id: state.teamId,
                 round_id: state.currentRound || "R1",
                 allocations: allocationsPayload,
                 lock_in_time_seconds: timeElapsed
               })
             });
          } catch(e) {
             console.error("Failed to allocate:", e);
          }
        }
      });
    }
  };

  const updateDOMWithoutRender = () => {
    const totalAllocated = state.allocations.reduce((a, b) => a + b, 0);
    const unallocated = TOTAL_COINS - totalAllocated;
    const isValid = totalAllocated === TOTAL_COINS;

    const balanceAmountEl = root.querySelector('.balance-amount');
    if (balanceAmountEl) {
      balanceAmountEl.innerHTML = `${unallocated.toLocaleString()} <span style="font-size: 2rem; color: var(--color-text-secondary);">Byte-Coins</span>`;
      if (isValid) {
        balanceAmountEl.classList.add('complete');
      } else {
        balanceAmountEl.classList.remove('complete');
      }
    }

    const cards = root.querySelectorAll('.candidate-card');
    state.allocations.forEach((val, index) => {
      const card = cards[index];
      const displayEl = card.querySelector('.allocation-display');
      if (displayEl) displayEl.textContent = val.toLocaleString();
      
      if (val > 0) card.classList.add('active-card');
      else card.classList.remove('active-card');
    });

    const lockBtn = root.querySelector('#lock-in-btn') as HTMLButtonElement;
    if (lockBtn) lockBtn.disabled = !isValid;
  };

  const startPolling = () => {
    window.setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/session/${state.sessionId}/state`);
        if (res.ok) {
          const data = await res.json();
          const prevStatus = state.status;
          state.status = data.status;
          
          if (data.current_round) {
             state.currentRound = data.current_round.round_id;
          }
          
          if (state.status.startsWith('round') && data.current_round_start_time) {
            const start = new Date(data.current_round_start_time + 'Z').getTime();
            const now = new Date().getTime();
            const elapsed = Math.floor((now - start) / 1000);
            state.timeLeft = Math.max(0, ROUND_DURATION_SEC - elapsed);
            
            if (state.timeLeft === 0 && !state.locked) {
               state.locked = true;
               // DO NOT UPDATE HOST SESSION STATUS FROM PLAYER!
               // The host is responsible for moving the session to waiting.
               // Just update UI state.
            }
          }

          if (data.reveal_order) {
            const oldLen = state.revealOrder.length;
            state.revealOrder = data.reveal_order;
            // Re-render if new reveal happened while in reveal state
            if (state.status === 'reveal' && state.revealOrder.length > oldLen) {
               renderReveal();
            }
          }

          if (state.status !== prevStatus) {
            if (state.status === 'waiting' || state.status === 'complete') {
              renderWaiting();
            } else if (state.status === 'reveal') {
              renderReveal();
            } else if (state.status.startsWith('round')) {
              state.locked = false;
              state.allocations = [0, 0, 0, 0];
              renderGame();
            }
          } else if (state.status.startsWith('round')) {
            const timerEl = root.querySelector('.timer-text');
            if (timerEl) {
               timerEl.textContent = `${Math.floor(state.timeLeft / 60).toString().padStart(2, '0')}:${(state.timeLeft % 60).toString().padStart(2, '0')}`;
               if (state.timeLeft <= 10) timerEl.classList.add('warning');
            }
          }
        }
      } catch(e) {
        console.error("Polling error", e);
      }
    }, 2000);
  };

    // autoStart(); // Removed autoStart, replaced with login screen
    renderLogin();
}

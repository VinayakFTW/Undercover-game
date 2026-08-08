import './host.css';

const API_BASE = 'http://localhost:8000';

export function initHostApp(root: HTMLElement) {
  root.innerHTML = `
    <div class="host-container">
      <header class="host-header">
        <h1 class="headline" style="color: var(--color-accent);">HOST DASHBOARD</h1>
        <p style="color: var(--color-text-secondary);">Manage Game Show Entities and Sessions</p>
      </header>

      <div class="host-grid">
        <!-- Session Controls -->
        <div class="host-card" style="grid-column: 1 / -1;">
          <h2>Session Controls (Auto-Syncing DEFAULT_SESSION)</h2>
          <div class="session-control-panel">
            <div style="display: flex; gap: 1rem; align-items: center;">
              <input type="text" id="host-session-id" placeholder="Enter Session ID..." style="padding: 0.5rem; border-radius: 4px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: white;" value="DEFAULT_SESSION">
              <button class="host-btn" onclick="loadSession()" style="background: var(--color-accent);">Load Session</button>
              <button class="host-btn" onclick="createAutoSession()">Create Auto-Session</button>
            </div>
            
            <div id="session-status-display" style="margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.5); border-radius: 8px;">
               <p>Loading session...</p>
            </div>
            
            <div class="status-buttons" style="margin-top: 1rem; display: flex; gap: 1rem; flex-wrap: wrap;">
              <button class="host-btn" onclick="updateSessionStatus('waiting')">Set Waiting</button>
              <button class="host-btn" onclick="updateSessionStatus('round1')">Start Round 1</button>
              <button class="host-btn" onclick="updateSessionStatus('round2')">Start Round 2</button>
              <button class="host-btn" onclick="updateSessionStatus('round3')">Start Round 3</button>
              <button class="host-btn" onclick="updateSessionStatus('reveal')">Enter Reveal State</button>
              <button class="host-btn" onclick="revealCandidate('A')">Reveal Cand A</button>
              <button class="host-btn" onclick="revealCandidate('B')">Reveal Cand B</button>
              <button class="host-btn" onclick="revealCandidate('C')">Reveal Cand C</button>
              <button class="host-btn" onclick="revealCandidate('D')">Reveal Cand D</button>
              <button class="host-btn" onclick="updateSessionStatus('complete')">Complete Session</button>
            </div>
          </div>
        </div>

        <!-- Candidate Answers and TTS -->
        <div class="host-card" style="grid-column: 1 / -1;">
          <h2>Candidate Responses (Current Round)</h2>
          <div id="candidate-responses-display" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
             <p style="color: var(--color-text-secondary);">Loading answers...</p>
          </div>
        </div>

        <!-- Teams Management -->
        <div class="host-card" style="grid-column: 1 / -1;">
          <h2>Teams Management</h2>
          <button class="host-btn" onclick="fetchAllTeams()" style="margin-bottom: 1rem;">Refresh Teams</button>
          <div id="teams-list-display" style="display: flex; flex-direction: column; gap: 1rem;">
             <p style="color: var(--color-text-secondary);">Click refresh to load teams...</p>
          </div>
        </div>

      </div>
    </div>
  `;

  attachHostEvents();
  autoSetup(root);
}

async function autoSetup(root: HTMLElement) {
  // Try to create the default session and candidates silently
  try {
    const cands = ['A', 'B', 'C', 'D'];
    for (const c of cands) {
      await fetch(`${API_BASE}/api/candidate/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_id: c, name: `Candidate ${c}` })
      }).catch(() => {});
    }
    
    await fetch(`${API_BASE}/api/session/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: 'DEFAULT_SESSION', team_id: 'DUMMY_TEAM' })
    }).catch(() => {});
    
  } catch (e) {}

  (window as any).currentActiveSession = 'DEFAULT_SESSION';
  
  // Auto poll the session status every 2 seconds
  setInterval(() => {
    (window as any).fetchSessionState(root);
  }, 2000);
}

// Store globally for quick access in onclick
(window as any).currentActiveSession = '';
(window as any).currentActiveRound = '';

(window as any).loadSession = () => {
  const sid = (document.getElementById('host-session-id') as HTMLInputElement).value;
  if (!sid) {
    alert("Please enter a session ID");
    return;
  }
  (window as any).currentActiveSession = sid;
  alert(`Session set to ${sid}`);
};

(window as any).createAutoSession = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/session/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await res.json();
    if (res.ok) {
      (document.getElementById('host-session-id') as HTMLInputElement).value = data.session_id;
      (window as any).currentActiveSession = data.session_id;
      alert(`Created session: ${data.session_id}`);
    } else {
      alert(`Error: ${data.detail}`);
    }
  } catch (e: any) {
    alert(e.message);
  }
};

(window as any).fetchAllTeams = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/host/teams`);
    if (res.ok) {
      const data = await res.json();
      const teamsList = document.getElementById('teams-list-display');
      if (teamsList) {
        if (data.teams.length === 0) {
          teamsList.innerHTML = '<p>No teams found.</p>';
          return;
        }
        teamsList.innerHTML = data.teams.map((t: any) => `
          <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <h3 style="color: var(--color-accent);">${t.team_name}</h3>
              <p>ID: ${t.team_id} | Session: ${t.session_id || 'None'}</p>
            </div>
            <button class="host-btn" onclick="addTeamToSession('${t.team_id}')" style="background: var(--color-accent); padding: 0.5rem 1rem;">Add to Current Session</button>
          </div>
        `).join('');
      }
    }
  } catch (e: any) {
    console.error(e);
  }
};

(window as any).addTeamToSession = async (teamId: string) => {
  const sessionId = (window as any).currentActiveSession;
  if (!sessionId) {
    alert("Please load a session first!");
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/api/host/edit_team/${teamId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    });
    if (res.ok) {
      alert(`Team added to session ${sessionId}`);
      (window as any).fetchAllTeams();
    } else {
      const data = await res.json();
      alert(`Error: ${data.detail}`);
    }
  } catch (e: any) {
    alert(e.message);
  }
};

(window as any).updateSessionStatus = async (status: string) => {
  const sessionId = (window as any).currentActiveSession;
  if (!sessionId) {
    alert("Please load a session first!");
    return;
  }
  
  try {
    const res = await fetch(`${API_BASE}/api/session/update_status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, status })
    });
    if (res.ok) {
      alert(`Session updated to ${status}`);
      document.getElementById('btn-fetch-session')?.click();
    } else {
      const data = await res.json();
      alert(`Error: ${data.detail}`);
    }
  } catch (e: any) {
    alert(e.message);
  }
};

(window as any).revealCandidate = async (candidateId: string) => {
  const sessionId = (window as any).currentActiveSession;
  if (!sessionId) {
    alert("Please load a session first!");
    return;
  }
  
  try {
    const res = await fetch(`${API_BASE}/api/candidate/reveal?session_id=${sessionId}&candidate_id=${candidateId}`, {
      method: 'POST'
    });
    if (res.ok) {
      alert(`Candidate ${candidateId} revealed successfully!`);
    } else {
      const data = await res.json();
      alert(`Error: ${data.detail}`);
    }
  } catch (e: any) {
    alert(e.message);
  }
};

(window as any).playTTS = async (candidateId: string, text: string) => {
  const sessionId = (window as any).currentActiveSession;
  const roundId = (window as any).currentActiveRound || "R1"; // Fallback
  
  try {
    const res = await fetch(`${API_BASE}/api/candidate/speech`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        round_id: roundId,
        candidate_id: candidateId,
        text: text
      })
    });
    
    if (res.ok) {
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.play();
    } else {
      const data = await res.json();
      alert(`TTS Error: ${data.detail}`);
    }
  } catch(e: any) {
    alert(e.message);
  }
}

function attachHostEvents() {
  (window as any).fetchSessionState = async (root: HTMLElement) => {
    const sessionId = (window as any).currentActiveSession;
    if (!sessionId) return;
    
    try {
      const res = await fetch(`${API_BASE}/api/session/${sessionId}/state`);
      if (res.ok) {
        const data = await res.json();
        const statusDisplay = root.querySelector('#session-status-display');
        if (statusDisplay) {
          statusDisplay.innerHTML = `
            <strong>Status:</strong> <span style="color: var(--color-accent); text-transform: uppercase;">${data.status}</span><br/>
            <strong>Round Start:</strong> ${data.current_round_start_time || 'N/A'}<br/>
            <strong>Current Round ID:</strong> ${data.current_round ? data.current_round.round_id : 'None'}
          `;
        }
        
        if (data.current_round) {
          (window as any).currentActiveRound = data.current_round.round_id;
        }

        const respDisplay = root.querySelector('#candidate-responses-display');
        if (respDisplay && data.current_round && data.current_round.candidate_answers) {
          const answers = data.current_round.candidate_answers;
          if (Object.keys(answers).length === 0) {
             respDisplay.innerHTML = `<p>No answers submitted yet.</p>`;
          } else {
             respDisplay.innerHTML = Object.keys(answers).map(candId => `
               <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">
                 <h3 style="color: var(--color-accent);">Candidate ${candId}</h3>
                 <p style="margin-bottom: 1rem; font-family: var(--font-body);">${answers[candId]}</p>
                 <button class="host-btn" onclick="playTTS('${candId}', \`${answers[candId].replace(/\`/g, '')}\`)">Play Audio</button>
               </div>
             `).join('');
          }
        } else if (respDisplay) {
          respDisplay.innerHTML = `<p>No active round or no answers.</p>`;
        }
      }
    } catch (e: any) {
      console.error(e.message);
    }
  };
}

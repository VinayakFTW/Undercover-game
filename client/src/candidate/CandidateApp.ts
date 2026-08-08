import './candidate.css';

const API_BASE = 'http://localhost:8000';

export function initCandidateApp(root: HTMLElement) {
  root.innerHTML = `
    <div class="candidate-container">
      <header class="candidate-header">
        <h1 class="headline" style="color: var(--color-accent);">CANDIDATE TERMINAL</h1>
        <p style="color: var(--color-text-secondary);">Input your responses</p>
      </header>

      <div class="candidate-card glass">
        <form id="form-submit-answer" class="candidate-form">
          <div class="form-group" style="display: none;">
            <input type="hidden" id="cand-session-id" value="DEFAULT_SESSION">
          </div>
          <div class="form-group">
            <label>Candidate ID</label>
            <input type="text" id="cand-candidate-id" required placeholder="A, B, C, or D">
          </div>
          <div class="form-group">
            <label>Question / Prompt (for AI generation)</label>
            <input type="text" id="cand-question" placeholder="Enter question asked by host to generate AI response...">
            <button type="button" id="btn-generate-ai" class="candidate-btn" style="margin-top: 0.5rem; background: var(--color-accent);">Generate Response with AI</button>
          </div>
          <div class="form-group">
            <label>Your Response</label>
            <textarea id="cand-response-text" required placeholder="Type your answer here..." rows="4" style="resize: none; background: rgba(0,0,0,0.3); color: white; padding: 1rem; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; font-family: var(--font-body);"></textarea>
          </div>
          <button type="submit" class="candidate-btn">Submit Answer</button>
          <div class="status-msg" id="msg-candidate"></div>
        </form>
      </div>
    </div>
  `;

  attachCandidateEvents(root);
}

function attachCandidateEvents(root: HTMLElement) {
  const form = root.querySelector('#form-submit-answer');
  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const sessionId = (root.querySelector('#cand-session-id') as HTMLInputElement).value;
    const candidateId = (root.querySelector('#cand-candidate-id') as HTMLInputElement).value;
    const text = (root.querySelector('#cand-response-text') as HTMLTextAreaElement).value;
    const msgEl = root.querySelector('#msg-candidate') as HTMLElement;

    try {
      msgEl.textContent = 'Submitting...';
      msgEl.className = 'status-msg loading';

      const stateRes = await fetch(`${API_BASE}/api/session/${sessionId}/state`);
      if (!stateRes.ok) throw new Error("Could not fetch session state");
      const stateData = await stateRes.json();
      const roundId = stateData.current_round ? stateData.current_round.round_id : 'R1';

      const response = await fetch(`${API_BASE}/api/candidate/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          round_id: roundId,
          candidate_id: candidateId,
          text: text
        })
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        msgEl.textContent = 'Answer Submitted Successfully!';
        msgEl.className = 'status-msg success';
        // Clear only the text area to keep context
        (root.querySelector('#cand-response-text') as HTMLTextAreaElement).value = '';
      } else {
        msgEl.textContent = `Error: ${data.detail || response.statusText}`;
        msgEl.className = 'status-msg error';
      }
    } catch (err: any) {
      msgEl.textContent = `Network Error: ${err.message}`;
      msgEl.className = 'status-msg error';
    }

    setTimeout(() => {
      msgEl.textContent = '';
      msgEl.className = 'status-msg';
    }, 5000);
  });

  const btnGenerateAI = root.querySelector('#btn-generate-ai');
  btnGenerateAI?.addEventListener('click', async () => {
    const question = (root.querySelector('#cand-question') as HTMLInputElement).value;
    const msgEl = root.querySelector('#msg-candidate') as HTMLElement;
    const responseTextArea = root.querySelector('#cand-response-text') as HTMLTextAreaElement;

    if (!question) {
      msgEl.textContent = 'Please enter a question to generate a response for.';
      msgEl.className = 'status-msg error';
      return;
    }

    try {
      msgEl.textContent = 'AI is generating...';
      msgEl.className = 'status-msg loading';
      btnGenerateAI.setAttribute('disabled', 'true');

      const response = await fetch(`${API_BASE}/api/candidate/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: question,
          conversation_history: []
        })
      });

      const data = await response.json();

      if (response.ok) {
        responseTextArea.value = data.response;
        msgEl.textContent = 'AI Generation Complete!';
        msgEl.className = 'status-msg success';
      } else {
        msgEl.textContent = `Error: ${data.detail || response.statusText}`;
        msgEl.className = 'status-msg error';
      }
    } catch (err: any) {
      msgEl.textContent = `Network Error: ${err.message}`;
      msgEl.className = 'status-msg error';
    } finally {
      btnGenerateAI.removeAttribute('disabled');
      setTimeout(() => {
        if (msgEl.textContent === 'AI Generation Complete!' || msgEl.className.includes('error')) {
            msgEl.textContent = '';
            msgEl.className = 'status-msg';
        }
      }, 5000);
    }
  });
}

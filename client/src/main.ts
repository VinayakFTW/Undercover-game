import './style.css'
import { initPlayerApp } from './player/PlayerApp'
import { initProjectorApp } from './projector/ProjectorApp'
import { initHostApp } from './host/HostApp'
import { initCandidateApp } from './candidate/CandidateApp'

const app = document.querySelector<HTMLDivElement>('#app')!

function renderLanding() {
  app.innerHTML = `
    <div class="container flex-center" style="height: 100vh; flex-direction: column; gap: 2rem;">
      <h1 class="headline" style="font-size: 6rem; color: var(--color-accent); text-shadow: 0 0 20px rgba(196, 30, 58, 0.5);">UNDERCOVER</h1>
      <h2 style="font-family: var(--font-body); font-size: 1.5rem; text-transform: none; color: var(--color-text-secondary); margin-bottom: 2rem;">Select Interface</h2>
      <div style="display: flex; gap: 2rem;">
        <button onclick="window.location.hash = '#/player'">Player View</button>
        <button onclick="window.location.hash = '#/projector'">Projector View</button>
        <button onclick="window.location.hash = '#/host'">Host Dashboard</button>
        <button onclick="window.location.hash = '#/candidate'">Candidate Terminal</button>
      </div>
    </div>
  `
}

function router() {
  const hash = window.location.hash

  switch (hash) {
    case '#/player':
      initPlayerApp(app)
      break
    case '#/projector':
      initProjectorApp(app)
      break
    case '#/host':
      initHostApp(app)
      break
    case '#/candidate':
      initCandidateApp(app)
      break
    default:
      renderLanding()
      break
  }
}

window.addEventListener('hashchange', router)
router() // initial load

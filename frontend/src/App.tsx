import { Routes, Route } from 'react-router-dom';
import GoalInput from './components/GoalInput';
import RunList from './components/RunList';
import RunDetail from './components/RunDetail';

function Home() {
  return (
    <div className="app-home">
      <header className="app-header">
        <h1>ElevateIQ Agent</h1>
        <p className="app-subtitle">Describe what you want done, and watch the agent work.</p>
      </header>
      <main className="app-main">
        <GoalInput />
        <RunList />
      </main>
      <style>{`
        .app-home {
          max-width: 800px;
          margin: 0 auto;
          padding: var(--spacing-xl);
        }
        .app-header {
          margin-bottom: var(--spacing-xl);
        }
        .app-header h1 {
          font-size: 1.75rem;
          margin-bottom: var(--spacing-xs);
        }
        .app-subtitle {
          color: var(--color-text-muted);
        }
        .app-main {
          min-height: 60vh;
        }
      `}</style>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/runs/:runId" element={<RunDetail />} />
    </Routes>
  );
}

import Link from "next/link";

const experiments = [
  ["Summer onboarding offer", "Simulated", "DRAFT", "—", "12 Nov 2023"],
  ["Pricing page revamp", "Simulated", "RUNNING", "68%", "09 Nov 2023"],
  ["Referral prompt", "Simulated", "PAUSED", "42%", "02 Nov 2023"],
];

export default function Dashboard() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">M</span><span className="brand-name">MARKETLAB</span></div>
        <div className="nav-label">Workspace</div>
        <nav className="side-nav">
          <Link href="/" aria-current="page"><span>▦</span><span>Dashboard</span></Link>
          <Link href="/builder"><span>✦</span><span>Hypotheses</span></Link>
          <Link href="/assets"><span>◈</span><span>Assets & approval</span></Link>
          <Link href="/"><span>◒</span><span>Experiments</span></Link>
          <Link href="/"><span>⌁</span><span>Evidence search</span></Link>
        </nav>
        <div className="side-footer">Simulated channel enabled<br />Academic prototype</div>
      </aside>
      <main className="main-content">
        <header className="topbar">
          <div><p className="eyebrow">Experiment workspace</p><h1>Good morning, Naphat</h1><p className="subtitle">Turn your next product idea into measurable evidence.</p></div>
          <div className="user-chip"><span>Operator</span><span className="avatar">N</span></div>
        </header>
        <section className="stats-grid" aria-label="Workspace summary">
          <article className="stat-card"><span className="stat-label">Active experiments</span><strong className="stat-value">01</strong><span className="stat-note">+1 this month</span></article>
          <article className="stat-card"><span className="stat-label">Drafts awaiting review</span><strong className="stat-value">02</strong><span className="stat-note">Needs your attention</span></article>
          <article className="stat-card"><span className="stat-label">Total budget used</span><strong className="stat-value">฿450</strong><span className="stat-note">of ฿1,000 cap</span></article>
          <article className="stat-card"><span className="stat-label">Evidence records</span><strong className="stat-value">14</strong><span className="stat-note">Reusable learnings</span></article>
        </section>
        <div className="dashboard-grid">
          <section className="panel">
            <div className="panel-header"><div><h2 className="panel-title">Recent experiments</h2><span className="panel-meta">Your latest hypotheses and results</span></div><Link className="button secondary" href="/builder">+ New hypothesis</Link></div>
            <div className="table-wrap"><table><thead><tr><th>Experiment</th><th>Channel</th><th>Status</th><th>Progress</th><th>Updated</th></tr></thead><tbody>
              {experiments.map(([name, channel, status, progress, date]) => <tr key={name}><td><strong>{name}</strong></td><td>{channel}</td><td><span className={`status ${status.toLowerCase()}`}>{status}</span></td><td>{progress === "—" ? "—" : <div className="progress"><span style={{ width: progress }} /></div>}</td><td>{date}</td></tr>)}
            </tbody></table></div>
          </section>
          <section className="panel">
            <div className="panel-header"><div><h2 className="panel-title">Next steps</h2><span className="panel-meta">Follow the evidence workflow</span></div></div>
            <div className="workflow">
              <Link className="workflow-card" href="/builder"><span className="workflow-step">01 · Start</span><h3>Define a hypothesis →</h3><p>Capture Problem, Segment, Offer and Pricing.</p></Link>
              <Link className="workflow-card" href="/assets"><span className="workflow-step">02 · Review</span><h3>Approve your asset →</h3><p>Check AI drafts before the simulated launch.</p></Link>
              <Link className="workflow-card" href="/"><span className="workflow-step">03 · Learn</span><h3>Read the results →</h3><p>Compare metrics and save reusable evidence.</p></Link>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

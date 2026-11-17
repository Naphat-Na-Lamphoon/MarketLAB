import HypothesisForm from "./hypothesis-form";

export default function BuilderPage() {
  return (
    <main className="main-content">
      <div className="topbar"><div><p className="eyebrow">02 · Hypothesis builder</p><h1>Define your 4D hypothesis</h1><p className="subtitle">Complete every field before asking AI to draft experiment assets.</p></div><a className="button ghost" href="/">← Dashboard</a></div>
      <HypothesisForm />
    </main>
  );
}

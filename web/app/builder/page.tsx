import HypothesisForm from "./hypothesis-form";

export default function BuilderPage() {
  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: 48, fontFamily: "Arial, sans-serif" }}>
      <p style={{ color: "#4263eb", fontWeight: 700 }}>HYPOTHESIS BUILDER</p>
      <h1>Define your 4D hypothesis</h1>
      <p>Complete every field before asking AI to draft experiment assets.</p>
      <HypothesisForm />
    </main>
  );
}

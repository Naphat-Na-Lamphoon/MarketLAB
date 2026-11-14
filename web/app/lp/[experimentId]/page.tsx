export default async function LandingPage({ params }: { params: Promise<{ experimentId: string }> }) {
  const { experimentId } = await params;
  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: 64, fontFamily: "Arial, sans-serif" }}>
      <p style={{ color: "#4263eb", fontWeight: 700 }}>MARKETLAB EXPERIMENT</p>
      <h1>Discover a better way to solve your problem.</h1>
      <p>This landing page is rendered from an approved experiment variant.</p>
      <button type="button" style={{ padding: "12px 20px", borderRadius: 8, border: 0 }}>
        Learn more
      </button>
      <small style={{ display: "block", marginTop: 48, color: "#777" }}>
        Experiment: {experimentId}. Academic prototype.
      </small>
    </main>
  );
}

import Link from "next/link";

const cards = [
  ["Hypothesis Builder", "Define Problem, Segment, Offer, and Pricing."],
  ["Asset Review", "Review AI-generated draft assets before launch."],
  ["Experiment Monitor", "Track spend, CTR, CVR, sample size, and p-value."],
  ["Evidence Graph", "Reuse validated learning in future experiments."],
];

export default function Dashboard() {
  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 48, fontFamily: "Arial, sans-serif" }}>
      <p style={{ color: "#4263eb", fontWeight: 700 }}>MARKETLAB</p>
      <h1>Validate ideas with evidence.</h1>
      <p style={{ color: "#555", maxWidth: 680 }}>
        A safe experiment workflow from product concept to approved, measurable learning.
      </p>
      <section style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16, marginTop: 32 }}>
        {cards.map(([title, description]) => (
          <article key={title} style={{ border: "1px solid #ddd", borderRadius: 12, padding: 20 }}>
            <h2>{title}</h2>
            <p>{description}</p>
          </article>
        ))}
      </section>
      <nav style={{ display: "flex", gap: 16, marginTop: 32 }}>
        <Link href="/builder">Create hypothesis</Link>
        <Link href="/assets">Review draft assets</Link>
      </nav>
      <p style={{ marginTop: 40, fontSize: 13, color: "#777" }}>
        Academic prototype. The simulated channel is enabled by default.
      </p>
    </main>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import {
  approveExperiment,
  createExperiment,
  generateAsset,
  launchExperiment,
  type AssetDraft,
} from "../../lib/api";

export default function AssetReviewPage() {
  return (
    <Suspense fallback={<main style={{ padding: 40, fontFamily: "Arial, sans-serif" }}>กำลังโหลด Asset Review...</main>}>
      <AssetReviewContent />
    </Suspense>
  );
}

function AssetReviewContent() {
  const searchParams = useSearchParams();
  const hypothesisId = searchParams.get("hypothesisId");
  const budget = Number(searchParams.get("budget") ?? 1000);
  const [asset, setAsset] = useState<AssetDraft | null>(null);
  const [headline, setHeadline] = useState("");
  const [body, setBody] = useState("");
  const [callToAction, setCallToAction] = useState("");
  const [status, setStatus] = useState("พร้อมสร้างโฆษณา");
  const [isLoading, setIsLoading] = useState(false);

  async function generate() {
    if (!hypothesisId) {
      setStatus("ไม่พบ Hypothesis กรุณาเริ่มจากหน้า Builder");
      return;
    }
    setIsLoading(true);
    setStatus("กำลังสร้างโฆษณา...");
    try {
      const result = await generateAsset(hypothesisId);
      setAsset(result);
      setHeadline(result.headline);
      setBody(result.body);
      setCallToAction(result.call_to_action);
      setStatus("สร้างแล้ว — กรุณาตรวจสอบก่อนอนุมัติ");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "สร้างโฆษณาไม่สำเร็จ");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void generate();
  }, [hypothesisId]);

  async function launch() {
    if (!asset) return;
    setIsLoading(true);
    try {
      const experiment = await createExperiment(asset.hypothesis_id);
      await approveExperiment(experiment.experiment_id, budget);
      await launchExperiment(experiment.experiment_id);
      setStatus("RUNNING — เปิดแคมเปญจำลองแล้ว");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "เปิดแคมเปญไม่สำเร็จ");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 980, margin: "0 auto", padding: 40, fontFamily: "Arial, sans-serif" }}>
      <p style={{ color: "#4263eb", fontWeight: 700 }}>ASSET REVIEW · SIMULATED CHANNEL</p>
      <h1>สร้างและตรวจสอบโฆษณา</h1>
      <p>โฆษณานี้เป็น Prototype สำหรับนำเสนอ ยังไม่ได้ยิงไปยังแพลตฟอร์มจริง</p>
      <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 28, marginTop: 28 }}>
        <div style={{ display: "grid", gap: 12 }}>
          <label>Headline<input value={headline} onChange={(event) => setHeadline(event.target.value)} style={inputStyle} /></label>
          <label>ข้อความโฆษณา<textarea value={body} onChange={(event) => setBody(event.target.value)} rows={5} style={inputStyle} /></label>
          <label>ปุ่ม Call-to-action<input value={callToAction} onChange={(event) => setCallToAction(event.target.value)} style={inputStyle} /></label>
          <div style={{ display: "flex", gap: 10 }}>
            <button type="button" onClick={() => void generate()} disabled={isLoading}>Generate ใหม่</button>
            <button type="button" onClick={() => void launch()} disabled={!asset || isLoading}>Approve & Launch</button>
          </div>
          <p aria-live="polite" style={{ color: status.startsWith("RUNNING") ? "#087f5b" : "#8a5a00" }}>{status}</p>
        </div>
        <article style={{ borderRadius: 18, overflow: "hidden", background: "linear-gradient(135deg, #1d3557, #457b9d)", color: "white", minHeight: 360, padding: 28, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
          <div><small>MARKETLAB · AD PREVIEW</small><h2 style={{ fontSize: 32, margin: "36px 0 16px" }}>{headline || "Headline ของโฆษณา"}</h2><p style={{ lineHeight: 1.6 }}>{body || "ข้อความโฆษณาจะแสดงตรงนี้"}</p></div>
          <button type="button" style={{ alignSelf: "flex-start", background: "#f4a261", border: 0, borderRadius: 8, padding: "12px 20px", fontWeight: 700 }}>{callToAction || "Call to action"}</button>
        </article>
      </section>
    </main>
  );
}

const inputStyle = { display: "block", width: "100%", marginTop: 6, padding: 10, border: "1px solid #ccc", borderRadius: 6, font: "inherit" };

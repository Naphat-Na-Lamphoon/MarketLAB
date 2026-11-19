from __future__ import annotations

import os
from contextlib import asynccontextmanager
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.ai import AssetDraft
from app.core.db import engine
from app.schemas.domain import (
    HypothesisCreateRequest,
    TelemetryEventRequest,
    VariantCreateRequest,
)
from app.services.rules import blocked_by_guardrail, decide
from app.services.stats import two_proportion_z_test

@asynccontextmanager
async def lifespan(_: FastAPI):
    if os.getenv("ENV", "dev") == "dev":
        seed_demo_state()
    yield


app = FastAPI(title="MarketLab API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class ExperimentCreate(BaseModel):
    hypothesis_id: UUID
    channel_type: str = "simulated"


class ApprovalCreate(BaseModel):
    approved_by_user_id: UUID
    budget_cap_thb: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class AssetGenerateRequest(BaseModel):
    hypothesis_id: UUID


hypotheses: dict[UUID, dict] = {}
variants: dict[UUID, dict] = {}
experiments: dict[UUID, dict] = {}
approvals: dict[UUID, dict] = {}
assets: dict[UUID, dict] = {}
telemetry_events: dict[UUID, dict] = {}


def seed_demo_state() -> None:
    """Load presentation data without requiring database infrastructure."""
    if hypotheses:
        return

    demo_users = (
        ("admin", "admin@marketlab.local"),
        ("operator", "operator@marketlab.local"),
        ("viewer", "viewer@marketlab.local"),
    )
    for index, (role, email) in enumerate(demo_users, start=1):
        hypothesis_id = UUID(f"00000000-0000-0000-0000-00000000010{index}")
        control_id = UUID(f"00000000-0000-0000-0000-00000000020{index}")
        treatment_id = UUID(f"00000000-0000-0000-0000-00000000030{index}")
        hypothesis = {
            "hypothesis_id": hypothesis_id,
            "problem_statement": "ทีมใช้เวลานานในการตรวจสอบข้อเสนอใหม่",
            "target_segment": "ผู้ใช้ MarketLab สำหรับการทดลองเบื้องต้น",
            "offer_description": f"ข้อเสนอทดลองสำหรับ {role} workspace",
            "pricing_tier": "ฟรีสำหรับ prototype",
            "budget_cap_thb": Decimal("1000.00"),
            "version": 1,
            "role": role,
            "owner_email": email,
        }
        hypotheses[hypothesis_id] = hypothesis
        variants[control_id] = {
            "variant_id": control_id,
            "hypothesis_id": hypothesis_id,
            "is_control": True,
            "ad_creative_copy": "Control message",
            "page_content": None,
            "status": "APPROVED",
        }
        variants[treatment_id] = {
            "variant_id": treatment_id,
            "hypothesis_id": hypothesis_id,
            "is_control": False,
            "ad_creative_copy": "Treatment message",
            "page_content": None,
            "status": "APPROVED",
        }

    experiment_id = UUID("00000000-0000-0000-0000-000000000401")
    operator_hypothesis_id = UUID("00000000-0000-0000-0000-000000000102")
    experiments[experiment_id] = {
        "experiment_id": experiment_id,
        "hypothesis_id": operator_hypothesis_id,
        "channel_type": "simulated",
        "status": "RUNNING",
        "spend_thb": Decimal("450.00"),
    }
    approvals[experiment_id] = {
        "approval_id": UUID("00000000-0000-0000-0000-000000000501"),
        "experiment_id": experiment_id,
        "approved_by_user_id": UUID("00000000-0000-0000-0000-000000000001"),
        "budget_cap_thb": Decimal("1000.00"),
    }
    control_id = UUID("00000000-0000-0000-0000-000000000202")
    treatment_id = UUID("00000000-0000-0000-0000-000000000302")
    for index in range(80):
        visitor_id = UUID(f"00000000-0000-0000-0000-{index + 1:012d}")
        variant_id = control_id if index % 2 == 0 else treatment_id
        event_id = UUID(f"00000000-0000-0001-0000-{index + 1:012d}")
        telemetry_events[event_id] = {
            "event_id": event_id,
            "experiment_id": experiment_id,
            "variant_id": variant_id,
            "event_type": "view",
            "value": None,
            "visitor_id": visitor_id,
        }

    assets[UUID("00000000-0000-0000-0000-000000000601")] = {
        "asset_id": UUID("00000000-0000-0000-0000-000000000601"),
        "hypothesis_id": operator_hypothesis_id,
        "headline": "ข้อเสนอที่ออกแบบมาเพื่อทีมของคุณ",
        "body": "ทดลอง workflow จำลองและดูผลลัพธ์ได้ในไม่กี่ขั้นตอน",
        "call_to_action": "เริ่มทดลองเลย",
        "status": "DRAFT",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "marketlab-api"}


@app.get("/health/db")
async def database_health() -> dict[str, str]:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from error
    return {"status": "ok", "service": "marketlab-database"}


@app.post("/api/v1/hypotheses", status_code=status.HTTP_201_CREATED)
async def create_hypothesis(payload: HypothesisCreateRequest) -> dict:
    item = {"hypothesis_id": uuid4(), **payload.model_dump(), "version": 1}
    hypotheses[item["hypothesis_id"]] = item
    return item


@app.get("/api/v1/hypotheses")
async def list_hypotheses() -> list[dict]:
    return list(hypotheses.values())


@app.post("/api/v1/variants", status_code=status.HTTP_201_CREATED)
async def create_variant(payload: VariantCreateRequest) -> dict:
    if payload.hypothesis_id not in hypotheses:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    item = {
        "variant_id": uuid4(),
        **payload.model_dump(),
        "status": "DRAFT",
    }
    variants[item["variant_id"]] = item
    return item


@app.get("/api/v1/hypotheses/{hypothesis_id}/variants")
async def list_variants(hypothesis_id: UUID) -> list[dict]:
    if hypothesis_id not in hypotheses:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    return [
        variant for variant in variants.values()
        if variant["hypothesis_id"] == hypothesis_id
    ]


@app.post("/api/v1/variants/{variant_id}/approve")
async def approve_variant(variant_id: UUID) -> dict:
    variant = variants.get(variant_id)
    if variant is None:
        raise HTTPException(status_code=404, detail="Variant not found")
    variant["status"] = "APPROVED"
    return variant


@app.post("/api/v1/variants/{variant_id}/reject")
async def reject_variant(variant_id: UUID) -> dict:
    variant = variants.get(variant_id)
    if variant is None:
        raise HTTPException(status_code=404, detail="Variant not found")
    variant["status"] = "REJECTED"
    return variant


@app.post("/api/v1/assets/generate", status_code=status.HTTP_201_CREATED)
async def generate_asset(payload: AssetGenerateRequest) -> dict:
    hypothesis = hypotheses.get(payload.hypothesis_id)
    if hypothesis is None:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    asset = AssetDraft(
        headline=f"{hypothesis['offer_description'][:80]} ที่ออกแบบมาเพื่อคุณ",
        body=(
            f"หมดปัญหาเรื่อง {hypothesis['problem_statement'][:180]} "
            f"ทดลองข้อเสนอสำหรับ {hypothesis['target_segment'][:120]} ได้แล้ววันนี้"
        ),
        call_to_action="เริ่มทดลองเลย",
    )
    item = {"asset_id": uuid4(), "hypothesis_id": payload.hypothesis_id, **asset.model_dump()}
    assets[item["asset_id"]] = item
    return item


@app.get("/api/v1/hypotheses/{hypothesis_id}")
async def get_hypothesis(hypothesis_id: UUID) -> dict:
    item = hypotheses.get(hypothesis_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    return item


@app.post("/api/v1/experiments", status_code=status.HTTP_201_CREATED)
async def create_experiment(payload: ExperimentCreate) -> dict:
    if payload.hypothesis_id not in hypotheses:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    if payload.channel_type != "simulated":
        raise HTTPException(
            status_code=422,
            detail="Only the simulated channel is available in this prototype",
        )
    item = {
        "experiment_id": uuid4(),
        **payload.model_dump(),
        "status": "DRAFT",
        "spend_thb": Decimal("0.00"),
    }
    experiments[item["experiment_id"]] = item
    return item


@app.get("/api/v1/experiments")
async def list_experiments() -> list[dict]:
    return list(experiments.values())


@app.post("/api/v1/experiments/{experiment_id}/approve")
async def approve_experiment(experiment_id: UUID, payload: ApprovalCreate) -> dict:
    experiment = experiments.get(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    hypothesis = hypotheses[experiment["hypothesis_id"]]
    if payload.budget_cap_thb > hypothesis["budget_cap_thb"]:
        raise HTTPException(status_code=422, detail="Approval cap exceeds hypothesis cap")
    approval = {"approval_id": uuid4(), "experiment_id": experiment_id, **payload.model_dump()}
    approvals[experiment_id] = approval
    experiment["status"] = "APPROVED"
    return approval


@app.post("/api/v1/experiments/{experiment_id}/launch")
async def launch_experiment(experiment_id: UUID) -> dict:
    experiment = experiments.get(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    approval = approvals.get(experiment_id)
    cap = approval["budget_cap_thb"] if approval else 0
    if blocked_by_guardrail(experiment["spend_thb"], cap, approval is not None):
        raise HTTPException(status_code=403, detail="BLOCKED_PENDING_APPROVAL")
    experiment["status"] = "RUNNING"
    return experiment


@app.post("/api/v1/experiments/{experiment_id}/pause")
async def pause_experiment(experiment_id: UUID) -> dict:
    experiment = experiments.get(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if experiment["status"] != "RUNNING":
        raise HTTPException(status_code=409, detail="Experiment is not running")
    experiment["status"] = "PAUSED"
    return experiment


@app.post("/api/v1/telemetry", status_code=status.HTTP_201_CREATED)
async def record_telemetry(payload: TelemetryEventRequest) -> dict:
    if payload.event_id in telemetry_events:
        return {**telemetry_events[payload.event_id], "duplicate": True}

    experiment = experiments.get(payload.experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    variant = variants.get(payload.variant_id)
    if variant is None or variant["hypothesis_id"] != experiment["hypothesis_id"]:
        raise HTTPException(status_code=404, detail="Variant not found for experiment")

    event = {"event_id": payload.event_id, **payload.model_dump()}
    telemetry_events[payload.event_id] = event
    return event


def _experiment_metrics(experiment_id: UUID) -> dict:
    events = [
        event for event in telemetry_events.values()
        if event["experiment_id"] == experiment_id
    ]
    by_variant: dict[UUID, dict[str, int | float]] = {}
    for event in events:
        metrics = by_variant.setdefault(
            event["variant_id"],
            {"views": 0, "clicks": 0, "conversions": 0},
        )
        if event["event_type"] == "view":
            metrics["views"] += 1
        elif event["event_type"] == "click":
            metrics["clicks"] += 1
        elif event["event_type"] == "conversion":
            metrics["conversions"] += 1

    for variant_id, metrics in by_variant.items():
        views = int(metrics["views"])
        clicks = int(metrics["clicks"])
        conversions = int(metrics["conversions"])
        metrics["ctr"] = clicks / views if views else 0.0
        metrics["cvr"] = conversions / views if views else 0.0
        metrics["variant_id"] = variant_id
        metrics["status"] = variants[variant_id]["status"]

    return {
        "experiment_id": experiment_id,
        "events": len(events),
        "variants": list(by_variant.values()),
    }


@app.get("/api/v1/experiments/{experiment_id}/metrics")
async def experiment_metrics(experiment_id: UUID) -> dict:
    if experiment_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return _experiment_metrics(experiment_id)


@app.post("/api/v1/experiments/{experiment_id}/evaluate")
async def evaluate_experiment(experiment_id: UUID) -> dict:
    experiment = experiments.get(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    metrics = _experiment_metrics(experiment_id)
    control = next(
        (item for item in metrics["variants"]
         if variants[item["variant_id"]]["is_control"]),
        None,
    )
    treatment = next(
        (item for item in metrics["variants"]
         if not variants[item["variant_id"]]["is_control"]),
        None,
    )
    if control is None or treatment is None:
        return {
            **metrics,
            "decision": "INSUFFICIENT_DATA",
            "reason": "A control and treatment variant are required",
        }

    result = two_proportion_z_test(
        int(control["conversions"]),
        int(control["views"]),
        int(treatment["conversions"]),
        int(treatment["views"]),
    )
    if result.get("insufficient_data"):
        decision = "INSUFFICIENT_DATA"
    else:
        decision = decide(
            int(control["views"]) + int(treatment["views"]),
            100,
            1000,
            result["p_value"],
            0.05,
            float(treatment["cvr"]),
            float(control["cvr"]),
        )
    return {**metrics, **result, "decision": decision}

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.ai import AssetDraft
from app.core.db import engine
from app.schemas.domain import HypothesisCreateRequest, VariantCreateRequest
from app.services.rules import blocked_by_guardrail
from app.services.stats import two_proportion_z_test

app = FastAPI(title="MarketLab API", version="0.1.0")
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
experiments: dict[UUID, dict] = {}
approvals: dict[UUID, dict] = {}
assets: dict[UUID, dict] = {}


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


@app.post("/api/v1/variants", status_code=status.HTTP_201_CREATED)
async def create_variant(payload: VariantCreateRequest) -> dict:
    if payload.hypothesis_id not in hypotheses:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    return {
        "variant_id": uuid4(),
        **payload.model_dump(),
        "status": "DRAFT",
    }


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
    if payload.channel_type not in {"simulated", "google_ads"}:
        raise HTTPException(status_code=422, detail="Unsupported channel")
    item = {
        "experiment_id": uuid4(),
        **payload.model_dump(),
        "status": "DRAFT",
        "spend_thb": Decimal("0.00"),
    }
    experiments[item["experiment_id"]] = item
    return item


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


@app.post("/api/v1/experiments/{experiment_id}/evaluate")
async def evaluate_experiment(experiment_id: UUID) -> dict:
    if experiment_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return two_proportion_z_test(4, 100, 8, 100)

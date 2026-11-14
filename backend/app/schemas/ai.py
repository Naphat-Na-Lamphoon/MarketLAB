from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class HypothesisDraft(BaseModel):
    problem_statement: str = Field(min_length=1, max_length=2000)
    target_segment: str = Field(min_length=1, max_length=1000)
    offer_description: str = Field(min_length=1, max_length=2000)
    pricing_tier: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=3000)


class AssetDraft(BaseModel):
    headline: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=2000)
    call_to_action: str = Field(min_length=1, max_length=120)
    status: Literal["DRAFT"] = "DRAFT"


class AiGenerationResponse(BaseModel):
    prompt_version: str
    model: str
    output: HypothesisDraft | AssetDraft
    status: Literal["DRAFT"] = "DRAFT"

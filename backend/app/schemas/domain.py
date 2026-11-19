from __future__ import annotations

from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class HypothesisCreateRequest(BaseModel):
    problem_statement: str = Field(min_length=1, max_length=2000)
    target_segment: str = Field(min_length=1, max_length=1000)
    offer_description: str = Field(min_length=1, max_length=2000)
    pricing_tier: str = Field(min_length=1, max_length=500)
    budget_cap_thb: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class VariantCreateRequest(BaseModel):
    hypothesis_id: UUID
    is_control: bool = False
    ad_creative_copy: str | None = Field(default=None, max_length=4000)
    page_content: dict[str, str] | None = None


class ExperimentCreateRequest(BaseModel):
    hypothesis_id: UUID
    channel_type: Literal["simulated", "google_ads"] = "simulated"


class TelemetryEventRequest(BaseModel):
    event_id: UUID
    experiment_id: UUID
    variant_id: UUID
    event_type: Literal["view", "click", "conversion", "time_on_page"]
    value: Decimal | None = Field(default=None, ge=0)

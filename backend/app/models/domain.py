from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPk


class User(TimestampMixin, Base):
    __tablename__ = "users"

    user_id: Mapped[UUIDPk]
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="viewer", nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('operator', 'admin', 'viewer')", name="ck_users_role"),
    )


class Hypothesis(TimestampMixin, Base):
    __tablename__ = "hypotheses"

    hypothesis_id: Mapped[UUIDPk]
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    concept_id: Mapped[str] = mapped_column(String(200), nullable=False)
    concept_text: Mapped[str | None] = mapped_column(Text)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    target_segment: Mapped[str] = mapped_column(Text, nullable=False)
    offer_description: Mapped[str] = mapped_column(Text, nullable=False)
    pricing_tier: Mapped[str] = mapped_column(String(500), nullable=False)
    budget_cap_thb: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    baseline_cvr: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    mde_abs: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    alpha: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.05"))
    power: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.80"))
    cost_per_visitor_thb: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.user_id"))

    variants: Mapped[list[Variant]] = relationship(back_populates="hypothesis")
    experiments: Mapped[list[Experiment]] = relationship(back_populates="hypothesis")

    __table_args__ = (
        CheckConstraint("budget_cap_thb > 0", name="ck_hypotheses_budget_positive"),
        CheckConstraint(
            "status IN ('DRAFT', 'READY')", name="ck_hypotheses_status"
        ),
        Index("ix_hypotheses_concept_id", "concept_id"),
    )


class Variant(TimestampMixin, Base):
    __tablename__ = "variants"

    variant_id: Mapped[UUIDPk]
    hypothesis_id: Mapped[UUID] = mapped_column(
        ForeignKey("hypotheses.hypothesis_id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_control: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ad_creative_copy: Mapped[str | None] = mapped_column(Text)
    page_content: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    prompt_template_version: Mapped[str | None] = mapped_column(String(50))

    hypothesis: Mapped[Hypothesis] = relationship(back_populates="variants")
    experiments: Mapped[list[Experiment]] = relationship(back_populates="variant")

    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'APPROVED', 'REJECTED')", name="ck_variants_status"
        ),
        Index("ix_variants_hypothesis_id", "hypothesis_id"),
    )


class Experiment(TimestampMixin, Base):
    __tablename__ = "experiments"

    experiment_id: Mapped[UUIDPk]
    hypothesis_id: Mapped[UUID] = mapped_column(
        ForeignKey("hypotheses.hypothesis_id"), nullable=False
    )
    variant_id: Mapped[UUID] = mapped_column(
        ForeignKey("variants.variant_id"), nullable=False
    )
    channel_type: Mapped[str] = mapped_column(String(30), default="simulated")
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    spend_thb: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    n_min: Mapped[int | None] = mapped_column(Integer)
    n_max: Mapped[int | None] = mapped_column(Integer)

    hypothesis: Mapped[Hypothesis] = relationship(back_populates="experiments")
    variant: Mapped[Variant] = relationship(back_populates="experiments")
    approvals: Mapped[list[Approval]] = relationship(back_populates="experiment")
    adapter_requests: Mapped[list[AdapterRequest]] = relationship(
        back_populates="experiment"
    )
    evaluations: Mapped[list[Evaluation]] = relationship(back_populates="experiment")
    evidence_record: Mapped[EvidenceRecord | None] = relationship(
        back_populates="experiment", uselist=False
    )

    __table_args__ = (
        CheckConstraint(
            "channel_type IN ('simulated', 'google_ads')",
            name="ck_experiments_channel_type",
        ),
        Index("ix_experiments_status", "status"),
    )


class Approval(TimestampMixin, Base):
    __tablename__ = "approvals"

    approval_id: Mapped[UUIDPk]
    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey("experiments.experiment_id"), nullable=False
    )
    approved_by_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id"), nullable=False
    )
    budget_cap_thb: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    experiment: Mapped[Experiment] = relationship(back_populates="approvals")


class AdapterRequest(TimestampMixin, Base):
    __tablename__ = "adapter_requests"

    request_id: Mapped[UUIDPk]
    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey("experiments.experiment_id"), nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    operation: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    response: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    experiment: Mapped[Experiment] = relationship(back_populates="adapter_requests")


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    event_id: Mapped[UUID] = mapped_column(primary_key=True)
    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey("experiments.experiment_id"), nullable=False
    )
    variant_id: Mapped[UUID] = mapped_column(
        ForeignKey("variants.variant_id"), nullable=False
    )
    visitor_id: Mapped[UUID] = mapped_column(nullable=False)
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    value: Mapped[Decimal | None] = mapped_column(Numeric)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_automated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_test: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('view', 'cta_click', 'time_on_page')",
            name="ck_telemetry_event_type",
        ),
        Index("ix_telemetry_experiment_variant_type", "experiment_id", "variant_id", "event_type"),
    )


class Evaluation(TimestampMixin, Base):
    __tablename__ = "evaluations"

    evaluation_id: Mapped[UUIDPk]
    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey("experiments.experiment_id"), nullable=False
    )
    variant_id: Mapped[UUID] = mapped_column(
        ForeignKey("variants.variant_id"), nullable=False
    )
    look_number: Mapped[int] = mapped_column(Integer, nullable=False)
    n_control: Mapped[int] = mapped_column(Integer, nullable=False)
    n_treatment: Mapped[int] = mapped_column(Integer, nullable=False)
    conversions_control: Mapped[int] = mapped_column(Integer, nullable=False)
    conversions_treatment: Mapped[int] = mapped_column(Integer, nullable=False)
    cvr_control: Mapped[Decimal | None] = mapped_column(Numeric)
    cvr_treatment: Mapped[Decimal | None] = mapped_column(Numeric)
    z_score: Mapped[Decimal | None] = mapped_column(Numeric)
    p_value: Mapped[Decimal | None] = mapped_column(Numeric)
    alpha_adjusted: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    statistical_significance: Mapped[bool] = mapped_column(Boolean, nullable=False)
    decision: Mapped[str] = mapped_column(String(30), nullable=False)

    experiment: Mapped[Experiment] = relationship(back_populates="evaluations")


class EvidenceRecord(TimestampMixin, Base):
    __tablename__ = "evidence_records"

    evidence_vector_id: Mapped[UUIDPk]
    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey("experiments.experiment_id"), unique=True, nullable=False
    )
    segment_tag: Mapped[str | None] = mapped_column(String(200))
    offer_tag: Mapped[str | None] = mapped_column(String(200))
    pricing_tier: Mapped[str | None] = mapped_column(String(200))
    outcome: Mapped[str] = mapped_column(String(30), nullable=False)
    conversion_rate: Mapped[Decimal | None] = mapped_column(Numeric)
    winning_variant: Mapped[UUID | None] = mapped_column(ForeignKey("variants.variant_id"))
    sample_size: Mapped[int | None] = mapped_column(Integer)
    p_value: Mapped[Decimal | None] = mapped_column(Numeric)
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(JSON)

    experiment: Mapped[Experiment] = relationship(back_populates="evidence_record")

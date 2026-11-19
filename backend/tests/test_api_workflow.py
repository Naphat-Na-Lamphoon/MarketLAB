from uuid import uuid4

import pytest

from app.main import (
    approve_experiment,
    create_experiment,
    create_hypothesis,
    create_variant,
    evaluate_experiment,
    experiment_metrics,
    launch_experiment,
    pause_experiment,
    record_telemetry,
    telemetry_events,
    variants,
    experiments,
    hypotheses,
    seed_demo_state,
)
from app.main import ApprovalCreate, ExperimentCreate
from app.schemas.domain import (
    HypothesisCreateRequest,
    TelemetryEventRequest,
    VariantCreateRequest,
)


@pytest.fixture(autouse=True)
def clear_in_memory_state():
    hypotheses.clear()
    variants.clear()
    experiments.clear()
    telemetry_events.clear()


def test_demo_seed_provides_role_workspaces_and_running_experiment():
    seed_demo_state()

    assert {item["role"] for item in hypotheses.values()} == {
        "admin",
        "operator",
        "viewer",
    }
    assert len(variants) == 6
    assert len(experiments) == 1
    assert next(iter(experiments.values()))["status"] == "RUNNING"


async def create_demo_experiment():
    hypothesis = await create_hypothesis(
        HypothesisCreateRequest(
            problem_statement="Problem",
            target_segment="Segment",
            offer_description="Offer",
            pricing_tier="100 THB",
            budget_cap_thb=1000,
        )
    )
    control = await create_variant(
        VariantCreateRequest(
            hypothesis_id=hypothesis["hypothesis_id"],
            is_control=True,
        )
    )
    treatment = await create_variant(
        VariantCreateRequest(
            hypothesis_id=hypothesis["hypothesis_id"],
        )
    )
    experiment = await create_experiment(
        ExperimentCreate(hypothesis_id=hypothesis["hypothesis_id"])
    )
    return experiment, control, treatment


@pytest.mark.asyncio
async def test_simulated_workflow_records_idempotent_telemetry_and_metrics():
    experiment, control, treatment = await create_demo_experiment()
    await approve_experiment(
        experiment["experiment_id"],
        ApprovalCreate(
            approved_by_user_id=uuid4(),
            budget_cap_thb=500,
        ),
    )
    await launch_experiment(experiment["experiment_id"])

    event = TelemetryEventRequest(
        event_id=uuid4(),
        experiment_id=experiment["experiment_id"],
        variant_id=control["variant_id"],
        event_type="view",
    )
    first = await record_telemetry(event)
    duplicate = await record_telemetry(event)

    assert first["event_id"] == duplicate["event_id"]
    assert duplicate["duplicate"] is True
    metrics = await experiment_metrics(experiment["experiment_id"])
    assert metrics["events"] == 1

    await pause_experiment(experiment["experiment_id"])
    assert experiments[experiment["experiment_id"]]["status"] == "PAUSED"


@pytest.mark.asyncio
async def test_evaluate_requires_control_and_treatment_data():
    experiment, control, treatment = await create_demo_experiment()
    result = await evaluate_experiment(experiment["experiment_id"])

    assert result["decision"] == "INSUFFICIENT_DATA"
    assert "control and treatment" in result["reason"]

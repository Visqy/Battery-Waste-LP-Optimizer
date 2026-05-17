import pandas as pd
from battery_optimizer.optimizer import solve_lp
from battery_optimizer.results import (
    build_allocation_matrix,
    calculate_supply_usage,
    calculate_facility_utilization,
    build_route_allocation_table,
    build_constraint_table,
    build_economic_summary,
    generate_interpretation,
    process_all_results,
)
from battery_optimizer.default_data import (
    get_default_collection_centers,
    get_default_recycling_facilities,
    get_default_transport_costs,
)


def get_solved_result():
    cc = get_default_collection_centers()
    rf = get_default_recycling_facilities()
    tc = get_default_transport_costs()
    opt_result = solve_lp(cc, rf, tc)
    return opt_result, cc, rf, tc


def test_allocation_matrix_shape():
    opt_result, cc, rf, tc = get_solved_result()
    matrix = build_allocation_matrix(opt_result)
    assert len(matrix) == len(cc)
    for j in rf["rf_id"].tolist():
        assert j in matrix.columns


def test_allocation_matrix_totals_match():
    opt_result, cc, rf, tc = get_solved_result()
    matrix = build_allocation_matrix(opt_result)
    rf_ids = rf["rf_id"].tolist()

    for i in cc["cc_id"].tolist():
        row_total = sum(matrix.loc[i, j] for j in rf_ids)
        expected_total = sum(opt_result["allocations"].get((i, j), 0.0) for j in rf_ids)
        assert abs(row_total - expected_total) < 1e-4


def test_supply_usage_columns():
    opt_result, cc, rf, tc = get_solved_result()
    df = calculate_supply_usage(opt_result, cc)

    for col in ["cc_id", "supply_kg", "allocated_kg", "unused_kg", "usage_pct"]:
        assert col in df.columns


def test_supply_usage_nonnegative_unused():
    opt_result, cc, rf, tc = get_solved_result()
    df = calculate_supply_usage(opt_result, cc)

    for val in df["unused_kg"]:
        assert val >= -1e-4


def test_facility_utilization_columns():
    opt_result, cc, rf, tc = get_solved_result()
    df = calculate_facility_utilization(opt_result, rf)

    for col in ["rf_id", "capacity_kg", "allocated_kg", "unused_capacity_kg", "utilization_pct"]:
        assert col in df.columns


def test_facility_utilization_pct_range():
    opt_result, cc, rf, tc = get_solved_result()
    df = calculate_facility_utilization(opt_result, rf)

    for val in df["utilization_pct"]:
        assert -0.01 <= val <= 100.01


def test_route_table_has_net_cost_and_benefit():
    opt_result, cc, rf, tc = get_solved_result()
    df = build_route_allocation_table(opt_result, cc, rf, tc)

    assert "net_cost_coeff_rp_kg" in df.columns
    assert "route_cost_rp" in df.columns
    assert "route_economic_benefit_rp" in df.columns
    assert len(df) == len(cc) * len(rf)


def test_route_economic_benefit_is_negative_route_cost():
    opt_result, cc, rf, tc = get_solved_result()
    df = build_route_allocation_table(opt_result, cc, rf, tc)

    for _, row in df.iterrows():
        assert abs(row["route_economic_benefit_rp"] + row["route_cost_rp"]) < 1e-4


def test_constraint_table_has_slack():
    opt_result, cc, rf, tc = get_solved_result()
    df = build_constraint_table(opt_result, cc, rf)

    assert "slack_kg" in df.columns
    assert len(df) == len(cc) + len(rf)


def test_economic_summary_has_required_keys():
    opt_result, cc, rf, tc = get_solved_result()
    summary = build_economic_summary(opt_result)

    expected_keys = [
        "objective_value",
        "net_economic_value",
        "net_economic_value_abs",
        "economic_status",
        "economic_value_label",
        "economic_alert_class",
        "economic_badge_class",
        "economic_message",
    ]

    for key in expected_keys:
        assert key in summary


def test_negative_objective_is_positive_net_benefit():
    opt_result, cc, rf, tc = get_solved_result()
    summary = build_economic_summary(opt_result)

    if opt_result["objective_value"] < 0:
        assert summary["economic_status"] == "Positive Net Benefit"
        assert summary["net_economic_value"] > 0
        assert summary["net_economic_value_abs"] > 0
        assert "negative" in summary["economic_message"].lower()


def test_interpretation_is_string():
    opt_result, cc, rf, tc = get_solved_result()
    text = generate_interpretation(opt_result, cc, rf)

    assert isinstance(text, str)
    assert len(text) > 50


def test_interpretation_contains_key_info():
    opt_result, cc, rf, tc = get_solved_result()
    text = generate_interpretation(opt_result, cc, rf)

    assert "Optimal" in text or "optimal" in text
    assert "objective" in text.lower()


def test_interpretation_explains_negative_objective():
    opt_result, cc, rf, tc = get_solved_result()
    text = generate_interpretation(opt_result, cc, rf)

    if opt_result["objective_value"] < 0:
        assert "negative" in text.lower()
        assert "net benefit" in text.lower() or "economic benefit" in text.lower()


def test_process_all_results_returns_all_keys():
    opt_result, cc, rf, tc = get_solved_result()
    processed = process_all_results(opt_result, cc, rf, tc)

    expected_keys = [
        "allocation_matrix",
        "supply_usage",
        "facility_utilization",
        "route_table",
        "constraint_table",
        "economic_summary",
        "interpretation",
    ]

    for key in expected_keys:
        assert key in processed


def test_processed_route_table_contains_benefit_column():
    opt_result, cc, rf, tc = get_solved_result()
    processed = process_all_results(opt_result, cc, rf, tc)

    assert "route_economic_benefit_rp" in processed["route_table"].columns


def test_processed_economic_summary_matches_objective():
    opt_result, cc, rf, tc = get_solved_result()
    processed = process_all_results(opt_result, cc, rf, tc)

    summary = processed["economic_summary"]

    assert summary["objective_value"] == opt_result["objective_value"]
    assert summary["net_economic_value"] == -opt_result["objective_value"]
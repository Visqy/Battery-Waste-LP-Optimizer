import pytest
from battery_optimizer.optimizer import solve_lp
from battery_optimizer.default_data import (
    get_default_collection_centers,
    get_default_recycling_facilities,
    get_default_transport_costs,
)


def get_defaults():
    return (
        get_default_collection_centers(),
        get_default_recycling_facilities(),
        get_default_transport_costs(),
    )


def test_default_data_solves_optimal():
    cc, rf, tc = get_defaults()
    result = solve_lp(cc, rf, tc)
    assert result["status"] == "Optimal"


def test_allocations_nonnegative():
    cc, rf, tc = get_defaults()
    result = solve_lp(cc, rf, tc)
    for val in result["allocations"].values():
        assert val >= -1e-8


def test_supply_not_exceeded():
    cc, rf, tc = get_defaults()
    result = solve_lp(cc, rf, tc)
    supply_map = dict(zip(cc["cc_id"], cc["supply_kg"].astype(float)))
    rf_ids = result["rf_ids"]
    for i in result["cc_ids"]:
        total_alloc = sum(result["allocations"].get((i, j), 0.0) for j in rf_ids)
        assert total_alloc <= supply_map[i] + 1e-4


def test_capacity_not_exceeded():
    cc, rf, tc = get_defaults()
    result = solve_lp(cc, rf, tc)
    cap_map = dict(zip(rf["rf_id"], rf["capacity_kg"].astype(float)))
    cc_ids = result["cc_ids"]
    for j in result["rf_ids"]:
        total_alloc = sum(result["allocations"].get((i, j), 0.0) for i in cc_ids)
        assert total_alloc <= cap_map[j] + 1e-4


def test_objective_value_is_numeric():
    cc, rf, tc = get_defaults()
    result = solve_lp(cc, rf, tc)
    assert result["objective_value"] is not None
    assert isinstance(result["objective_value"], float)


def test_all_supply_allocated_when_capacity_sufficient():
    cc, rf, tc = get_defaults()
    total_supply = float(cc["supply_kg"].sum())
    total_capacity = float(rf["capacity_kg"].sum())
    result = solve_lp(cc, rf, tc)
    if total_capacity >= total_supply:
        total_alloc = sum(result["allocations"].values())
        assert abs(total_alloc - total_supply) < 1.0


def test_supply_slacks_nonnegative():
    cc, rf, tc = get_defaults()
    result = solve_lp(cc, rf, tc)
    for val in result["supply_slacks"].values():
        assert val >= -1e-4


def test_capacity_slacks_nonnegative():
    cc, rf, tc = get_defaults()
    result = solve_lp(cc, rf, tc)
    for val in result["capacity_slacks"].values():
        assert val >= -1e-4


def test_runtime_is_positive():
    cc, rf, tc = get_defaults()
    result = solve_lp(cc, rf, tc)
    assert result["runtime"] > 0


def test_result_contains_all_routes():
    cc, rf, tc = get_defaults()
    result = solve_lp(cc, rf, tc)
    cc_ids = cc["cc_id"].tolist()
    rf_ids = rf["rf_id"].tolist()
    for i in cc_ids:
        for j in rf_ids:
            assert (i, j) in result["allocations"]
import pytest
import pandas as pd
from battery_optimizer.validation import validate_all
from battery_optimizer.default_data import (
    get_default_collection_centers,
    get_default_recycling_facilities,
    get_default_transport_costs,
)


def get_defaults():
    cc = get_default_collection_centers()
    rf = get_default_recycling_facilities()
    tc = get_default_transport_costs()
    return cc, rf, tc


def test_valid_default_data():
    cc, rf, tc = get_defaults()
    result = validate_all(cc, rf, tc)
    assert result["is_valid"] is True
    assert len(result["errors"]) == 0


def test_missing_required_column_cc():
    cc, rf, tc = get_defaults()
    cc_bad = cc.drop(columns=["supply_kg"])
    result = validate_all(cc_bad, rf, tc)
    assert result["is_valid"] is False
    assert any("supply_kg" in e for e in result["errors"])


def test_missing_required_column_rf():
    cc, rf, tc = get_defaults()
    rf_bad = rf.drop(columns=["capacity_kg"])
    result = validate_all(cc, rf_bad, tc)
    assert result["is_valid"] is False
    assert any("capacity_kg" in e for e in result["errors"])


def test_missing_required_column_tc():
    cc, rf, tc = get_defaults()
    tc_bad = tc.drop(columns=["transport_cost_rp_kg"])
    result = validate_all(cc, rf, tc_bad)
    assert result["is_valid"] is False
    assert any("transport_cost_rp_kg" in e for e in result["errors"])


def test_negative_supply():
    cc, rf, tc = get_defaults()
    cc_bad = cc.copy()
    cc_bad.loc[0, "supply_kg"] = -100
    result = validate_all(cc_bad, rf, tc)
    assert result["is_valid"] is False
    assert any("supply_kg" in e and "negative" in e.lower() for e in result["errors"])


def test_negative_capacity():
    cc, rf, tc = get_defaults()
    rf_bad = rf.copy()
    rf_bad.loc[0, "capacity_kg"] = -500
    result = validate_all(cc, rf_bad, tc)
    assert result["is_valid"] is False
    assert any("capacity_kg" in e and "negative" in e.lower() for e in result["errors"])


def test_negative_transport_cost():
    cc, rf, tc = get_defaults()
    tc_bad = tc.copy()
    tc_bad.loc[0, "transport_cost_rp_kg"] = -1000
    result = validate_all(cc, rf, tc_bad)
    assert result["is_valid"] is False
    assert any("transport_cost_rp_kg" in e and "negative" in e.lower() for e in result["errors"])


def test_duplicate_cc_id():
    cc, rf, tc = get_defaults()
    cc_bad = pd.concat([cc, cc.iloc[[0]]], ignore_index=True)
    result = validate_all(cc_bad, rf, tc)
    assert result["is_valid"] is False
    assert any("duplicate" in e.lower() for e in result["errors"])


def test_duplicate_rf_id():
    cc, rf, tc = get_defaults()
    rf_bad = pd.concat([rf, rf.iloc[[0]]], ignore_index=True)
    result = validate_all(cc, rf_bad, tc)
    assert result["is_valid"] is False
    assert any("duplicate" in e.lower() for e in result["errors"])


def test_missing_transport_route():
    cc, rf, tc = get_defaults()
    tc_bad = tc[tc["cc_id"] != "CC01"].copy()
    result = validate_all(cc, rf, tc_bad)
    assert result["is_valid"] is False
    assert any("CC01" in e for e in result["errors"])


def test_supply_exceeds_capacity_generates_warning():
    cc, rf, tc = get_defaults()
    rf_low = rf.copy()
    rf_low["capacity_kg"] = 1000
    result = validate_all(cc, rf_low, tc)
    assert result["is_valid"] is False or len(result["warnings"]) > 0
    total_supply = cc["supply_kg"].sum()
    total_cap = rf_low["capacity_kg"].sum()
    if total_supply > total_cap:
        assert any("supply" in w.lower() and "capacity" in w.lower() for w in result["warnings"])


def test_missing_value_in_required_field():
    cc, rf, tc = get_defaults()
    cc_bad = cc.copy()
    cc_bad.loc[0, "supply_kg"] = None
    result = validate_all(cc_bad, rf, tc)
    assert result["is_valid"] is False
    assert any("missing" in e.lower() for e in result["errors"])
import pandas as pd
from battery_optimizer.config import (
    CC_REQUIRED_COLS, RF_REQUIRED_COLS, TC_REQUIRED_COLS,
)


def _check_required_columns(df, required_cols, table_name, errors):
    if df is None:
        errors.append(f"Table '{table_name}' is missing or could not be loaded.")
        return False
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        errors.append(f"Table '{table_name}' is missing columns: {', '.join(missing)}")
        return False
    return True


def _check_missing_values(df, required_cols, table_name, errors):
    for col in required_cols:
        if col not in df.columns:
            continue
        null_count = df[col].isnull().sum()
        if null_count > 0:
            errors.append(
                f"Table '{table_name}', column '{col}': {null_count} missing value(s)."
            )


def _check_non_negative(df, numeric_cols, table_name, errors):
    for col in numeric_cols:
        if col not in df.columns:
            continue
        neg_count = (df[col] < 0).sum()
        if neg_count > 0:
            errors.append(
                f"Table '{table_name}', column '{col}': {neg_count} negative value(s). "
                f"All values must be >= 0."
            )


def _check_duplicate_ids(df, id_col, table_name, errors):
    if id_col not in df.columns:
        return
    duplicates = df[df.duplicated(subset=[id_col], keep=False)][id_col].unique()
    if len(duplicates) > 0:
        errors.append(
            f"Table '{table_name}': duplicate {id_col} values: {', '.join(str(d) for d in duplicates)}"
        )


def _check_route_completeness(cc_df, rf_df, tc_df, errors):
    if cc_df is None or rf_df is None or tc_df is None:
        return
    if "cc_id" not in cc_df.columns or "rf_id" not in rf_df.columns:
        return
    if "cc_id" not in tc_df.columns or "rf_id" not in tc_df.columns:
        return

    cc_ids = set(cc_df["cc_id"].dropna().unique())
    rf_ids = set(rf_df["rf_id"].dropna().unique())
    existing_routes = set(zip(tc_df["cc_id"], tc_df["rf_id"]))

    missing_routes = []
    for cc_id in sorted(cc_ids):
        for rf_id in sorted(rf_ids):
            if (cc_id, rf_id) not in existing_routes:
                missing_routes.append(f"({cc_id}, {rf_id})")

    if missing_routes:
        errors.append(
            f"Missing transport cost routes: {', '.join(missing_routes)}"
        )


def _generate_warnings(cc_df, rf_df, warnings):
    if cc_df is None or rf_df is None:
        return
    if "supply_kg" not in cc_df.columns or "capacity_kg" not in rf_df.columns:
        return

    total_supply = cc_df["supply_kg"].sum()
    total_capacity = rf_df["capacity_kg"].sum()

    if total_supply > total_capacity:
        warnings.append(
            f"Total supply ({total_supply:,.0f} kg) exceeds total capacity "
            f"({total_capacity:,.0f} kg). Some supply may remain unallocated."
        )
    elif total_supply < total_capacity:
        unused = total_capacity - total_supply
        warnings.append(
            f"Total capacity ({total_capacity:,.0f} kg) exceeds total supply "
            f"({total_supply:,.0f} kg). Approximately {unused:,.0f} kg of capacity "
            f"will remain unused."
        )


def validate_all(cc_df, rf_df, tc_df):
    errors = []
    warnings = []

    cc_cols_ok = _check_required_columns(cc_df, CC_REQUIRED_COLS, "collection_centers", errors)
    rf_cols_ok = _check_required_columns(rf_df, RF_REQUIRED_COLS, "recycling_facilities", errors)
    tc_cols_ok = _check_required_columns(tc_df, TC_REQUIRED_COLS, "transport_costs", errors)

    if cc_cols_ok:
        _check_missing_values(cc_df, CC_REQUIRED_COLS, "collection_centers", errors)
        _check_non_negative(cc_df, ["supply_kg"], "collection_centers", errors)
        _check_duplicate_ids(cc_df, "cc_id", "collection_centers", errors)

    if rf_cols_ok:
        _check_missing_values(rf_df, RF_REQUIRED_COLS, "recycling_facilities", errors)
        _check_non_negative(
            rf_df,
            ["capacity_kg", "processing_cost_rp_kg", "recovery_revenue_rp_kg"],
            "recycling_facilities",
            errors,
        )
        _check_duplicate_ids(rf_df, "rf_id", "recycling_facilities", errors)

    if tc_cols_ok:
        _check_missing_values(tc_df, TC_REQUIRED_COLS, "transport_costs", errors)
        _check_non_negative(tc_df, ["transport_cost_rp_kg"], "transport_costs", errors)

    if cc_cols_ok and rf_cols_ok and tc_cols_ok:
        _check_route_completeness(cc_df, rf_df, tc_df, errors)

    _generate_warnings(cc_df, rf_df, warnings)

    summary = {}
    if cc_df is not None and "supply_kg" in cc_df.columns:
        summary["total_supply_kg"] = float(cc_df["supply_kg"].sum())
        summary["num_collection_centers"] = len(cc_df)
    if rf_df is not None and "capacity_kg" in rf_df.columns:
        summary["total_capacity_kg"] = float(rf_df["capacity_kg"].sum())
        summary["num_recycling_facilities"] = len(rf_df)
    if tc_df is not None:
        summary["num_routes"] = len(tc_df)

    return {
        "errors": errors,
        "warnings": warnings,
        "is_valid": len(errors) == 0,
        "summary": summary,
    }
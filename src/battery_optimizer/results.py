import pandas as pd


def build_allocation_matrix(opt_result):
    cc_ids = opt_result["cc_ids"]
    rf_ids = opt_result["rf_ids"]
    allocations = opt_result["allocations"]

    data = {}
    for j in rf_ids:
        data[j] = [allocations.get((i, j), 0.0) for i in cc_ids]

    df = pd.DataFrame(data, index=cc_ids)
    df.index.name = "cc_id"
    df["total_allocated_kg"] = df[rf_ids].sum(axis=1)
    return df


def calculate_supply_usage(opt_result, cc_df):
    cc_ids = opt_result["cc_ids"]
    allocations = opt_result["allocations"]
    rf_ids = opt_result["rf_ids"]

    supply_map = dict(zip(cc_df["cc_id"], cc_df["supply_kg"].astype(float)))
    name_map = dict(zip(cc_df["cc_id"], cc_df["name"])) if "name" in cc_df.columns else {}

    rows = []
    for i in cc_ids:
        total_alloc = sum(allocations.get((i, j), 0.0) for j in rf_ids)
        supply = supply_map.get(i, 0.0)
        unused = supply - total_alloc
        usage_pct = (total_alloc / supply * 100) if supply > 0 else 0.0
        rows.append(
            {
                "cc_id": i,
                "name": name_map.get(i, i),
                "supply_kg": supply,
                "allocated_kg": total_alloc,
                "unused_kg": unused,
                "usage_pct": usage_pct,
            }
        )
    return pd.DataFrame(rows)


def calculate_facility_utilization(opt_result, rf_df):
    rf_ids = opt_result["rf_ids"]
    allocations = opt_result["allocations"]
    cc_ids = opt_result["cc_ids"]

    capacity_map = dict(zip(rf_df["rf_id"], rf_df["capacity_kg"].astype(float)))
    name_map = dict(zip(rf_df["rf_id"], rf_df["name"])) if "name" in rf_df.columns else {}

    rows = []
    for j in rf_ids:
        total_alloc = sum(allocations.get((i, j), 0.0) for i in cc_ids)
        cap = capacity_map.get(j, 0.0)
        unused = cap - total_alloc
        utilization_pct = (total_alloc / cap * 100) if cap > 0 else 0.0
        rows.append(
            {
                "rf_id": j,
                "name": name_map.get(j, j),
                "capacity_kg": cap,
                "allocated_kg": total_alloc,
                "unused_capacity_kg": unused,
                "utilization_pct": utilization_pct,
            }
        )
    return pd.DataFrame(rows)


def build_route_allocation_table(opt_result, cc_df, rf_df, tc_df):
    cc_ids = opt_result["cc_ids"]
    rf_ids = opt_result["rf_ids"]
    allocations = opt_result["allocations"]

    cc_name_map = dict(zip(cc_df["cc_id"], cc_df["name"])) if "name" in cc_df.columns else {}
    rf_name_map = dict(zip(rf_df["rf_id"], rf_df["name"])) if "name" in rf_df.columns else {}
    proc_cost_map = dict(zip(rf_df["rf_id"], rf_df["processing_cost_rp_kg"].astype(float)))
    rev_map = dict(zip(rf_df["rf_id"], rf_df["recovery_revenue_rp_kg"].astype(float)))

    tc_lookup = {}
    for _, row in tc_df.iterrows():
        tc_lookup[(row["cc_id"], row["rf_id"])] = float(row["transport_cost_rp_kg"])

    rows = []
    for i in cc_ids:
        for j in rf_ids:
            c_ij = tc_lookup.get((i, j), 0.0)
            p_j = proc_cost_map.get(j, 0.0)
            r_j = rev_map.get(j, 0.0)
            net_cost = c_ij + p_j - r_j
            alloc = allocations.get((i, j), 0.0)
            route_cost = net_cost * alloc
            rows.append(
                {
                    "cc_id": i,
                    "cc_name": cc_name_map.get(i, i),
                    "rf_id": j,
                    "rf_name": rf_name_map.get(j, j),
                    "transport_cost_rp_kg": c_ij,
                    "processing_cost_rp_kg": p_j,
                    "recovery_revenue_rp_kg": r_j,
                    "net_cost_coeff_rp_kg": net_cost,
                    "allocated_kg": alloc,
                    "route_cost_rp": route_cost,
                    "route_economic_benefit_rp": -route_cost,
                }
            )
    return pd.DataFrame(rows)


def build_constraint_table(opt_result, cc_df, rf_df):
    rows = []
    cc_name_map = dict(zip(cc_df["cc_id"], cc_df["name"])) if "name" in cc_df.columns else {}
    rf_name_map = dict(zip(rf_df["rf_id"], rf_df["name"])) if "name" in rf_df.columns else {}
    supply_map = dict(zip(cc_df["cc_id"], cc_df["supply_kg"].astype(float)))
    cap_map = dict(zip(rf_df["rf_id"], rf_df["capacity_kg"].astype(float)))

    for i in opt_result["cc_ids"]:
        slack = opt_result["supply_slacks"].get(i)
        shadow = opt_result["supply_shadow"].get(i)
        rows.append(
            {
                "constraint_type": "Supply",
                "id": i,
                "name": cc_name_map.get(i, i),
                "rhs_kg": supply_map.get(i, 0.0),
                "slack_kg": slack if slack is not None else 0.0,
                "shadow_price_rp_kg": shadow,
                "binding": (abs(slack) < 1e-4) if slack is not None else None,
            }
        )

    for j in opt_result["rf_ids"]:
        slack = opt_result["capacity_slacks"].get(j)
        shadow = opt_result["capacity_shadow"].get(j)
        rows.append(
            {
                "constraint_type": "Capacity",
                "id": j,
                "name": rf_name_map.get(j, j),
                "rhs_kg": cap_map.get(j, 0.0),
                "slack_kg": slack if slack is not None else 0.0,
                "shadow_price_rp_kg": shadow,
                "binding": (abs(slack) < 1e-4) if slack is not None else None,
            }
        )

    return pd.DataFrame(rows)


def build_economic_summary(opt_result):
    objective_value = opt_result.get("objective_value")

    if objective_value is None:
        return {
            "objective_value": None,
            "net_economic_value": None,
            "net_economic_value_abs": None,
            "economic_status": "Unknown",
            "economic_value_label": "Estimated Net Economic Value",
            "economic_alert_class": "alert alert-secondary",
            "economic_badge_class": "badge bg-secondary",
            "economic_message": "Economic result is not available.",
        }

    objective_value = float(objective_value)
    net_economic_value = -objective_value
    net_economic_value_abs = abs(net_economic_value)

    if objective_value < 0:
        return {
            "objective_value": objective_value,
            "net_economic_value": net_economic_value,
            "net_economic_value_abs": net_economic_value_abs,
            "economic_status": "Positive Net Benefit",
            "economic_value_label": "Estimated Net Benefit",
            "economic_alert_class": "alert alert-success",
            "economic_badge_class": "badge bg-success",
            "economic_message": (
                "A negative objective value does not indicate a loss. It occurs because "
                "the model minimizes net cost, where transportation and processing costs "
                "are offset by recovered material revenue. In this scenario, recovered "
                "material revenue exceeds total cost, so the result represents a positive "
                "net economic benefit."
            ),
        }

    if objective_value > 0:
        return {
            "objective_value": objective_value,
            "net_economic_value": net_economic_value,
            "net_economic_value_abs": net_economic_value_abs,
            "economic_status": "Net Economic Cost",
            "economic_value_label": "Estimated Net Cost",
            "economic_alert_class": "alert alert-warning",
            "economic_badge_class": "badge bg-warning text-dark",
            "economic_message": (
                "A positive objective value indicates that transportation and processing "
                "costs exceed recovered material revenue. This scenario produces a net "
                "economic cost."
            ),
        }

    return {
        "objective_value": objective_value,
        "net_economic_value": net_economic_value,
        "net_economic_value_abs": 0.0,
        "economic_status": "Break Even",
        "economic_value_label": "Estimated Net Economic Value",
        "economic_alert_class": "alert alert-info",
        "economic_badge_class": "badge bg-info text-dark",
        "economic_message": (
            "The objective value is zero. This indicates a break-even condition where "
            "total cost and recovered material revenue are balanced."
        ),
    }


def generate_interpretation(opt_result, cc_df, rf_df):
    if opt_result["status"] != "Optimal":
        return (
            f"The solver returned status '{opt_result['status']}'. "
            "An optimal solution was not found. Review the input parameters and run validation again."
        )

    economic_summary = build_economic_summary(opt_result)
    obj = float(opt_result["objective_value"])
    net_value_abs = economic_summary["net_economic_value_abs"]
    alloc_vals = list(opt_result["allocations"].values())
    total_alloc = sum(alloc_vals)
    total_supply = float(cc_df["supply_kg"].sum())
    total_capacity = float(rf_df["capacity_kg"].sum())
    unused_supply = total_supply - total_alloc
    unused_capacity = total_capacity - total_alloc
    supply_usage_pct = (total_alloc / total_supply * 100) if total_supply > 0 else 0.0

    rf_ids = opt_result["rf_ids"]
    cc_ids = opt_result["cc_ids"]
    rf_name_map = dict(zip(rf_df["rf_id"], rf_df["name"])) if "name" in rf_df.columns else {}
    cap_map = dict(zip(rf_df["rf_id"], rf_df["capacity_kg"].astype(float)))

    rf_util_parts = []
    for j in rf_ids:
        total_j = sum(opt_result["allocations"].get((i, j), 0.0) for i in cc_ids)
        cap_j = cap_map.get(j, 0.0)
        util_pct = (total_j / cap_j * 100) if cap_j > 0 else 0.0
        name_j = rf_name_map.get(j, j)
        rf_util_parts.append(f"{name_j} is used at {util_pct:.1f}% capacity ({total_j:,.0f} kg)")

    rf_util_text = "; ".join(rf_util_parts)

    binding_supply = [
        i for i in cc_ids
        if opt_result["supply_slacks"].get(i, 1) is not None
        and abs(opt_result["supply_slacks"].get(i, 1)) < 1e-4
    ]
    binding_cap = [
        j for j in rf_ids
        if opt_result["capacity_slacks"].get(j, 1) is not None
        and abs(opt_result["capacity_slacks"].get(j, 1)) < 1e-4
    ]

    cc_name_map = dict(zip(cc_df["cc_id"], cc_df["name"])) if "name" in cc_df.columns else {}
    binding_supply_names = [cc_name_map.get(i, i) for i in binding_supply]
    binding_cap_names = [rf_name_map.get(j, j) for j in binding_cap]

    lines = [
        "The optimization was successfully solved with Optimal status using the CBC solver.",
        f"The total allocated NMC battery waste volume is {total_alloc:,.0f} kg out of {total_supply:,.0f} kg of available supply.",
        f"The supply absorption rate is {supply_usage_pct:.1f}%, with {unused_supply:,.0f} kg of unused supply.",
        f"Facility utilization: {rf_util_text}.",
        f"The model objective value is Rp {obj:,.0f} per year as the minimum net cost objective.",
    ]

    if obj < 0:
        lines.append(
            f"Because the objective value is negative, the result should be interpreted as an estimated net benefit of Rp {net_value_abs:,.0f} per year. "
            "The negative value occurs because recovered material revenue is greater than transportation and processing costs."
        )
    elif obj > 0:
        lines.append(
            f"Because the objective value is positive, the result indicates an estimated net cost of Rp {net_value_abs:,.0f} per year. "
            "In this scenario, total cost remains greater than recovered material revenue."
        )
    else:
        lines.append(
            "The objective value is zero, so the scenario is economically at break-even."
        )

    if binding_supply_names:
        lines.append(
            f"The binding supply constraints are {', '.join(binding_supply_names)}. "
            "All available supply from these collection centers is fully allocated."
        )

    if binding_cap_names:
        lines.append(
            f"The binding capacity constraints are {', '.join(binding_cap_names)}. "
            "These facilities operate at full capacity and act as bottlenecks."
        )

    if total_capacity > total_supply:
        lines.append(
            f"Total facility capacity is {total_capacity:,.0f} kg, which exceeds total supply. "
            f"The system has {unused_capacity:,.0f} kg of unused capacity."
        )

    return " ".join(lines)


def process_all_results(opt_result, cc_df, rf_df, tc_df):
    allocation_matrix = build_allocation_matrix(opt_result)
    supply_usage = calculate_supply_usage(opt_result, cc_df)
    facility_utilization = calculate_facility_utilization(opt_result, rf_df)
    route_table = build_route_allocation_table(opt_result, cc_df, rf_df, tc_df)
    constraint_table = build_constraint_table(opt_result, cc_df, rf_df)
    economic_summary = build_economic_summary(opt_result)
    interpretation = generate_interpretation(opt_result, cc_df, rf_df)

    return {
        "allocation_matrix": allocation_matrix,
        "supply_usage": supply_usage,
        "facility_utilization": facility_utilization,
        "route_table": route_table,
        "constraint_table": constraint_table,
        "economic_summary": economic_summary,
        "interpretation": interpretation,
    }
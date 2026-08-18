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
        is_binding = (abs(slack) < 1e-4) if slack is not None else None
        rows.append(
            {
                "constraint_type": "Supply",
                "id": i,
                "name": cc_name_map.get(i, i),
                "rhs_kg": supply_map.get(i, 0.0),
                "slack_kg": 0.0 if is_binding else (slack if slack is not None else 0.0),
                "shadow_price_rp_kg": shadow,
                "binding": is_binding,
            }
        )

    for j in opt_result["rf_ids"]:
        slack = opt_result["capacity_slacks"].get(j)
        shadow = opt_result["capacity_shadow"].get(j)
        is_binding = (abs(slack) < 1e-4) if slack is not None else None
        rows.append(
            {
                "constraint_type": "Capacity",
                "id": j,
                "name": rf_name_map.get(j, j),
                "rhs_kg": cap_map.get(j, 0.0),
                "slack_kg": 0.0 if is_binding else (slack if slack is not None else 0.0),
                "shadow_price_rp_kg": shadow,
                "binding": is_binding,
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
            "economic_value_label": "Modeled Objective Value",
            "economic_alert_class": "alert alert-secondary",
            "economic_badge_class": "badge bg-secondary",
            "economic_message": "Objective value is not available.",
        }

    objective_value = float(objective_value)
    net_economic_value = -objective_value
    net_economic_value_abs = abs(net_economic_value)

    if objective_value < 0:
        return {
            "objective_value": objective_value,
            "net_economic_value": net_economic_value,
            "net_economic_value_abs": net_economic_value_abs,
            "economic_status": "Net Benefit (Modeled)",
            "economic_value_label": "Modeled Net Benefit",
            "economic_alert_class": "alert alert-secondary",
            "economic_badge_class": "badge bg-secondary",
            "economic_message": (
                "A negative objective value indicates that, under the supplied scenario "
                "parameters, modeled recovered material revenue exceeds the transportation "
                "and processing costs included in the objective function. This value is the "
                "model's calculated result for the scenario parameters supplied by the user."
            ),
        }

    if objective_value > 0:
        return {
            "objective_value": objective_value,
            "net_economic_value": net_economic_value,
            "net_economic_value_abs": net_economic_value_abs,
            "economic_status": "Net Cost (Modeled)",
            "economic_value_label": "Modeled Net Cost",
            "economic_alert_class": "alert alert-secondary",
            "economic_badge_class": "badge bg-secondary",
            "economic_message": (
                "A positive objective value indicates that, under the supplied scenario "
                "parameters, the transportation and processing costs included in the "
                "objective function exceed modeled recovered material revenue. This value "
                "is the model's calculated result for the scenario parameters supplied by "
                "the user."
            ),
        }

    return {
        "objective_value": objective_value,
        "net_economic_value": net_economic_value,
        "net_economic_value_abs": 0.0,
        "economic_status": "Break Even (Modeled)",
        "economic_value_label": "Modeled Objective Value",
        "economic_alert_class": "alert alert-secondary",
        "economic_badge_class": "badge bg-secondary",
        "economic_message": (
            "The objective value is zero, indicating that modeled transportation and "
            "processing costs equal modeled recovered material revenue under the supplied "
            "scenario parameters."
        ),
    }


def calculate_system_metrics(opt_result, cc_df, rf_df):
    allocations = opt_result["allocations"]
    cc_ids = opt_result["cc_ids"]
    rf_ids = opt_result["rf_ids"]

    total_allocated = float(sum(allocations.values()))
    total_supply = float(cc_df["supply_kg"].sum())
    total_capacity = float(rf_df["capacity_kg"].sum())

    unused_supply = total_supply - total_allocated
    unused_capacity = total_capacity - total_allocated

    supply_absorption_pct = (total_allocated / total_supply * 100) if total_supply > 0 else 0.0
    system_capacity_utilization_pct = (total_allocated / total_capacity * 100) if total_capacity > 0 else 0.0

    rf_name_map = dict(zip(rf_df["rf_id"], rf_df["name"])) if "name" in rf_df.columns else {}
    cap_map = dict(zip(rf_df["rf_id"], rf_df["capacity_kg"].astype(float)))
    cc_name_map = dict(zip(cc_df["cc_id"], cc_df["name"])) if "name" in cc_df.columns else {}

    facility_rows = []
    for j in rf_ids:
        allocated_j = sum(allocations.get((i, j), 0.0) for i in cc_ids)
        capacity_j = cap_map.get(j, 0.0)
        utilization_j = (allocated_j / capacity_j * 100) if capacity_j > 0 else 0.0
        facility_rows.append(
            {
                "rf_id": j,
                "name": rf_name_map.get(j, j),
                "allocated_kg": allocated_j,
                "capacity_kg": capacity_j,
                "utilization_pct": utilization_j,
            }
        )

    if facility_rows:
        most_utilized = max(facility_rows, key=lambda item: item["utilization_pct"])
        max_facility_utilization_pct = most_utilized["utilization_pct"]
        most_utilized_facility = most_utilized["name"]
    else:
        max_facility_utilization_pct = 0.0
        most_utilized_facility = "N/A"

    binding_supply = [
        cc_name_map.get(i, i)
        for i in cc_ids
        if opt_result["supply_slacks"].get(i, 1) is not None
        and abs(opt_result["supply_slacks"].get(i, 1)) < 1e-4
    ]

    binding_capacity = [
        rf_name_map.get(j, j)
        for j in rf_ids
        if opt_result["capacity_slacks"].get(j, 1) is not None
        and abs(opt_result["capacity_slacks"].get(j, 1)) < 1e-4
    ]

    return {
        "total_allocated_kg": total_allocated,
        "total_supply_kg": total_supply,
        "total_capacity_kg": total_capacity,
        "unused_supply_kg": unused_supply,
        "unused_capacity_kg": unused_capacity,
        "supply_absorption_pct": supply_absorption_pct,
        "system_capacity_utilization_pct": system_capacity_utilization_pct,
        "max_facility_utilization_pct": max_facility_utilization_pct,
        "most_utilized_facility": most_utilized_facility,
        "binding_supply_centers": binding_supply,
        "binding_capacity_facilities": binding_capacity,
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
    metrics = calculate_system_metrics(opt_result, cc_df, rf_df)

    lines = [
        "The optimization was successfully solved with Optimal status using the CBC solver.",
        f"The total allocated NMC battery waste volume is {metrics['total_allocated_kg']:,.0f} kg out of {metrics['total_supply_kg']:,.0f} kg of available supply.",
        f"The supply absorption rate is {metrics['supply_absorption_pct']:.1f}%, with {metrics['unused_supply_kg']:,.0f} kg of unused supply.",
        f"The system capacity utilization rate is {metrics['system_capacity_utilization_pct']:.1f}%, with {metrics['unused_capacity_kg']:,.0f} kg of unused capacity.",
        f"The model objective value is Rp {obj:,.0f} per year as the minimum net cost objective.",
    ]

    if obj < 0:
        lines.append(
            f"Because the objective value is negative, the result represents a modeled net benefit of Rp {net_value_abs:,.0f} per year. "
            "The negative value occurs because recovered material revenue is greater than transportation and processing costs."
        )
    elif obj > 0:
        lines.append(
            f"Because the objective value is positive, the result represents a modeled net cost of Rp {net_value_abs:,.0f} per year. "
            "In this scenario, total cost remains greater than recovered material revenue."
        )
    else:
        lines.append(
            "The objective value is zero, so the scenario is economically at break-even."
        )

    if metrics["binding_supply_centers"]:
        lines.append(
            f"The binding supply constraints are {', '.join(metrics['binding_supply_centers'])}. "
            "All available supply from these collection centers is fully allocated."
        )

    if metrics["binding_capacity_facilities"]:
        lines.append(
            f"The binding capacity constraints are {', '.join(metrics['binding_capacity_facilities'])}. "
            "These facilities operate at full capacity in this solution."
        )

    lines.append(
        "This interpretation describes properties of the model solution for the "
        "scenario parameters supplied by the user."
    )

    return " ".join(lines)


def process_all_results(opt_result, cc_df, rf_df, tc_df):
    allocation_matrix = build_allocation_matrix(opt_result)
    supply_usage = calculate_supply_usage(opt_result, cc_df)
    facility_utilization = calculate_facility_utilization(opt_result, rf_df)
    route_table = build_route_allocation_table(opt_result, cc_df, rf_df, tc_df)
    constraint_table = build_constraint_table(opt_result, cc_df, rf_df)
    economic_summary = build_economic_summary(opt_result)
    system_metrics = calculate_system_metrics(opt_result, cc_df, rf_df)
    interpretation = generate_interpretation(opt_result, cc_df, rf_df)

    return {
        "allocation_matrix": allocation_matrix,
        "supply_usage": supply_usage,
        "facility_utilization": facility_utilization,
        "route_table": route_table,
        "constraint_table": constraint_table,
        "economic_summary": economic_summary,
        "system_metrics": system_metrics,
        "interpretation": interpretation,
    }
import time
import pulp
import pandas as pd
from battery_optimizer.config import MODEL_NAME, SOLVER_NAME


def solve_lp(cc_df, rf_df, tc_df):
    start_time = time.time()

    cc_ids = cc_df["cc_id"].tolist()
    rf_ids = rf_df["rf_id"].tolist()

    supply = dict(zip(cc_df["cc_id"], cc_df["supply_kg"].astype(float)))
    capacity = dict(zip(rf_df["rf_id"], rf_df["capacity_kg"].astype(float)))
    processing_cost = dict(zip(rf_df["rf_id"], rf_df["processing_cost_rp_kg"].astype(float)))
    recovery_revenue = dict(zip(rf_df["rf_id"], rf_df["recovery_revenue_rp_kg"].astype(float)))

    tc_lookup = {}
    for _, row in tc_df.iterrows():
        tc_lookup[(row["cc_id"], row["rf_id"])] = float(row["transport_cost_rp_kg"])

    prob = pulp.LpProblem(MODEL_NAME, pulp.LpMinimize)

    x = pulp.LpVariable.dicts(
        "x",
        [(i, j) for i in cc_ids for j in rf_ids],
        lowBound=0,
        cat="Continuous",
    )

    prob += pulp.lpSum(
        (tc_lookup[(i, j)] + processing_cost[j] - recovery_revenue[j]) * x[(i, j)]
        for i in cc_ids
        for j in rf_ids
    )

    for i in cc_ids:
        prob += (
            pulp.lpSum(x[(i, j)] for j in rf_ids) <= supply[i],
            f"supply_{i}",
        )

    for j in rf_ids:
        prob += (
            pulp.lpSum(x[(i, j)] for i in cc_ids) <= capacity[j],
            f"capacity_{j}",
        )

    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)

    runtime = time.time() - start_time
    status = pulp.LpStatus[prob.status]

    allocations = {}
    for i in cc_ids:
        for j in rf_ids:
            raw_val = pulp.value(x[(i, j)])
            allocations[(i, j)] = float(raw_val) if raw_val is not None else 0.0

    supply_slacks = {}
    supply_shadow = {}
    for i in cc_ids:
        constraint_key = f"supply_{i}"
        if constraint_key in prob.constraints:
            c = prob.constraints[constraint_key]
            supply_slacks[i] = float(c.slack) if c.slack is not None else 0.0
            supply_shadow[i] = float(c.pi) if hasattr(c, "pi") and c.pi is not None else None
        else:
            supply_slacks[i] = 0.0
            supply_shadow[i] = None

    capacity_slacks = {}
    capacity_shadow = {}
    for j in rf_ids:
        constraint_key = f"capacity_{j}"
        if constraint_key in prob.constraints:
            c = prob.constraints[constraint_key]
            capacity_slacks[j] = float(c.slack) if c.slack is not None else 0.0
            capacity_shadow[j] = float(c.pi) if hasattr(c, "pi") and c.pi is not None else None
        else:
            capacity_slacks[j] = 0.0
            capacity_shadow[j] = None

    obj_val = pulp.value(prob.objective)
    objective_value = float(obj_val) if obj_val is not None else None

    return {
        "status": status,
        "objective_value": objective_value,
        "allocations": allocations,
        "supply_slacks": supply_slacks,
        "supply_shadow": supply_shadow,
        "capacity_slacks": capacity_slacks,
        "capacity_shadow": capacity_shadow,
        "runtime": runtime,
        "cc_ids": cc_ids,
        "rf_ids": rf_ids,
    }
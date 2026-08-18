import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from shiny import module, ui, render
from battery_optimizer.report import export_results_to_excel
from battery_optimizer.io_excel import export_current_configuration


def format_rupiah(value):
    if value is None:
        return "N/A"
    return f"Rp {float(value):,.0f}/year"


def format_rupiah_abs(value):
    if value is None:
        return "N/A"
    return f"Rp {abs(float(value)):,.0f}/year"


def _clamp_near_zero(value, tolerance=1e-6):
    value = float(value)
    return 0.0 if abs(value) < tolerance else value


def format_kg(value):
    if value is None:
        return "N/A"
    return f"{_clamp_near_zero(value):,.0f} kg"


def format_number(value):
    if value is None:
        return "N/A"
    return f"{_clamp_near_zero(value):,.0f}"


def format_rp_value(value):
    if value is None:
        return "N/A"
    return f"Rp {float(value):,.0f}"


def format_percent(value):
    if value is None:
        return "N/A"
    return f"{float(value):.1f}%"


ALLOCATION_MATRIX_LABELS = {
    "cc_id": "Collection Center ID",
    "total_allocated_kg": "Total Allocated (kg/year)",
}

ROUTE_TABLE_LABELS = {
    "cc_id": "Collection Center ID",
    "cc_name": "Collection Center",
    "rf_id": "Recycling Facility ID",
    "rf_name": "Recycling Facility",
    "transport_cost_rp_kg": "Transport Cost (Rp/kg)",
    "processing_cost_rp_kg": "Processing Cost (Rp/kg)",
    "recovery_revenue_rp_kg": "Recovery Revenue (Rp/kg)",
    "net_cost_coeff_rp_kg": "Net Cost Coefficient (Rp/kg)",
    "allocated_kg": "Allocated Volume (kg/year)",
    "route_cost_rp": "Net Cost Objective (Rp/year)",
    "route_economic_benefit_rp": "Route Net Benefit (Rp/year)",
}

CONSTRAINT_TABLE_LABELS = {
    "constraint_type": "Constraint Type",
    "id": "Constraint ID",
    "name": "Name",
    "rhs_kg": "Limit (kg/year)",
    "slack_kg": "Slack (kg/year)",
    "shadow_price_rp_kg": "Shadow Price (Rp/kg)",
    "binding": "Binding Status",
}


@module.ui
def results_ui():
    return ui.nav_panel(
        "Results",
        ui.div(
            ui.h2("Optimization Results"),
            ui.output_ui("results_content"),
            style="padding: 1rem;",
        ),
    )


@module.server
def results_server(input, output, session, state):
    @output(suspend_when_hidden=False)
    @render.ui
    def results_content():
        opt_result = state.optimization_result()
        processed = state.processed_results()

        if opt_result is None:
            return ui.div(
                ui.div(
                    "No optimization results available. Run validation and optimization first.",
                    class_="alert alert-info",
                )
            )

        if opt_result["status"] != "Optimal":
            return ui.div(
                ui.div(
                    f"Solver status: {opt_result['status']}. An optimal solution was not found.",
                    class_="alert alert-warning",
                )
            )

        if processed is None:
            return ui.div(
                ui.div("Results processing failed. Re-run optimization.", class_="alert alert-danger")
            )

        total_alloc = processed["supply_usage"]["allocated_kg"].sum()
        total_unused_supply = processed["supply_usage"]["unused_kg"].sum()
        total_unused_cap = processed["facility_utilization"]["unused_capacity_kg"].sum()
        obj = opt_result["objective_value"]
        runtime = opt_result["runtime"]

        economic_summary = processed.get("economic_summary", {})
        system_metrics = processed.get("system_metrics", {})

        economic_status = economic_summary.get("economic_status", "Unknown")
        economic_value_label = economic_summary.get("economic_value_label", "Modeled Objective Value")
        economic_value_abs = economic_summary.get("net_economic_value_abs")
        economic_message = economic_summary.get("economic_message", "")
        economic_badge_class = economic_summary.get("economic_badge_class", "badge bg-secondary")
        economic_alert_class = economic_summary.get("economic_alert_class", "alert alert-secondary")

        supply_absorption_pct = system_metrics.get("supply_absorption_pct")
        system_capacity_utilization_pct = system_metrics.get("system_capacity_utilization_pct")
        max_facility_utilization_pct = system_metrics.get("max_facility_utilization_pct")

        return ui.div(
            ui.h3("1. Optimization Summary"),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Solver Status"),
                    ui.card_body(ui.div(opt_result["status"], class_="badge bg-secondary")),
                ),
                ui.card(
                    ui.card_header("Objective Status"),
                    ui.card_body(ui.div(economic_status, class_=economic_badge_class)),
                ),
                ui.card(
                    ui.card_header("Supply Absorption"),
                    ui.card_body(ui.p(format_percent(supply_absorption_pct))),
                ),
                ui.card(
                    ui.card_header("System Capacity Utilization"),
                    ui.card_body(ui.p(format_percent(system_capacity_utilization_pct))),
                ),
                col_widths=[3, 3, 3, 3],
            ),
            ui.layout_columns(
                ui.card(
                    ui.card_header(economic_value_label),
                    ui.card_body(ui.p(format_rupiah_abs(economic_value_abs))),
                ),
                ui.card(
                    ui.card_header("Total Allocated"),
                    ui.card_body(ui.p(format_kg(total_alloc))),
                ),
                ui.card(
                    ui.card_header("Unused Supply"),
                    ui.card_body(ui.p(format_kg(total_unused_supply))),
                ),
                ui.card(
                    ui.card_header("Unused Capacity"),
                    ui.card_body(ui.p(format_kg(total_unused_cap))),
                ),
                col_widths=[3, 3, 3, 3],
            ),
            ui.div(
                economic_message,
                class_=economic_alert_class,
                style="margin-top: 1rem;",
            ),
            ui.card(
                ui.card_header("Minimum Net Cost Objective"),
                ui.card_body(
                    ui.p(format_rupiah(obj)),
                    ui.tags.small(f"Solver runtime: {runtime:.4f} s."),
                ),
                style="margin-top: 1rem;",
            ),
            ui.h3("2. Allocation Results", style="margin-top: 1.5rem;"),
            ui.h4("Allocation Matrix (kg/year)"),
            ui.output_table("alloc_matrix_table"),
            ui.h4("Route Allocation Detail", style="margin-top: 1rem;"),
            ui.output_table("route_table"),
            ui.h3("3. Capacity Utilization", style="margin-top: 1.5rem;"),
            ui.p(f"Most utilized facility: {system_metrics.get('most_utilized_facility', 'N/A')} "
                 f"({format_percent(max_facility_utilization_pct)})."),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Facility Utilization (%)"),
                    ui.card_body(ui.output_plot("utilization_chart")),
                ),
                ui.card(
                    ui.card_header("Supply Usage by Collection Center (kg)"),
                    ui.card_body(ui.output_plot("supply_chart")),
                ),
                col_widths=[6, 6],
            ),
            ui.h3("4. Constraint Diagnostics and Shadow Prices", style="margin-top: 1.5rem;"),
            ui.output_table("constraint_table"),
            ui.h3("5. Optimization Result Interpretation", style="margin-top: 1.5rem;"),
            ui.output_ui("interpretation_block"),
            ui.h3("6. Export Results", style="margin-top: 1.5rem;"),
            ui.div(
                ui.download_button("download_results", "Export Results to Excel (.xlsx)", class_="btn-success"),
                ui.download_button("download_configuration", "Export Current Configuration (.xlsx)", class_="btn-primary"),
                style="margin-top: 2rem; display: flex; gap: 12px;",
            ),
        )

    @output(suspend_when_hidden=False)
    @render.table
    def alloc_matrix_table():
        processed = state.processed_results()
        if processed is None:
            return pd.DataFrame()

        df = processed["allocation_matrix"].copy()
        df = df.reset_index()

        for col in df.select_dtypes(include="number").columns:
            df[col] = df[col].map(format_number)

        df = df.rename(columns=ALLOCATION_MATRIX_LABELS)
        return df

    @output(suspend_when_hidden=False)
    @render.table
    def route_table():
        processed = state.processed_results()
        if processed is None:
            return pd.DataFrame()

        df = processed["route_table"].copy()

        rupiah_cols = [
            "transport_cost_rp_kg",
            "processing_cost_rp_kg",
            "recovery_revenue_rp_kg",
            "net_cost_coeff_rp_kg",
            "route_cost_rp",
            "route_economic_benefit_rp",
        ]

        number_cols = [
            "allocated_kg",
        ]

        for col in rupiah_cols:
            if col in df.columns:
                df[col] = df[col].map(format_rp_value)

        for col in number_cols:
            if col in df.columns:
                df[col] = df[col].map(format_number)

        df = df.rename(columns=ROUTE_TABLE_LABELS)
        return df

    @output(suspend_when_hidden=False)
    @render.plot
    def utilization_chart():
        processed = state.processed_results()
        if processed is None:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "No data", ha="center")
            return fig

        df = processed["facility_utilization"]
        fig, ax = plt.subplots(figsize=(6, 3.5))

        bars = ax.bar(
            df["name"] if "name" in df.columns else df["rf_id"],
            df["utilization_pct"],
            color=["#14532D", "#4ADE80"],
        )

        ax.set_ylabel("Utilization (%)")
        ax.set_ylim(0, 110)
        ax.axhline(100, color="red", linestyle="--", linewidth=1, label="Capacity limit")

        for bar, val in zip(bars, df["utilization_pct"]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{val:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        ax.legend()
        plt.tight_layout()
        return fig

    @output(suspend_when_hidden=False)
    @render.plot
    def supply_chart():
        processed = state.processed_results()
        if processed is None:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "No data", ha="center")
            return fig

        opt_result = state.optimization_result()
        df = processed["supply_usage"]
        rf_ids = opt_result["rf_ids"]
        cc_ids = opt_result["cc_ids"]
        allocs = opt_result["allocations"]

        cc_names = (
            df["name"].tolist()
            if "name" in df.columns
            else df["cc_id"].tolist()
        )

        fig, ax = plt.subplots(figsize=(8, 4))
        colors = ["#14532D", "#4ADE80", "#86EFAC", "#DCFCE7"]
        bottom = [0.0] * len(cc_ids)

        for idx_j, j in enumerate(rf_ids):
            vals = [allocs.get((i, j), 0.0) for i in cc_ids]
            ax.bar(
                range(len(cc_ids)),
                vals,
                bottom=bottom,
                label=j,
                color=colors[idx_j % len(colors)],
            )
            bottom = [b + v for b, v in zip(bottom, vals)]

        supply_vals = df["supply_kg"].tolist()

        ax.scatter(
            range(len(cc_ids)),
            supply_vals,
            marker="D",
            color="red",
            s=50,
            zorder=5,
            label="Supply limit",
        )

        ax.set_xticks(range(len(cc_ids)))
        ax.set_xticklabels(cc_names, rotation=30, ha="right", fontsize=8)
        ax.set_ylabel("Volume (kg/year)")
        ax.legend(loc="upper right", fontsize=8)
        plt.tight_layout()
        return fig

    @output(suspend_when_hidden=False)
    @render.table
    def constraint_table():
        processed = state.processed_results()
        if processed is None:
            return pd.DataFrame()

        df = processed["constraint_table"].copy()

        for col in ["rhs_kg", "slack_kg"]:
            if col in df.columns:
                df[col] = df[col].map(format_number)

        if "shadow_price_rp_kg" in df.columns:
            df["shadow_price_rp_kg"] = df["shadow_price_rp_kg"].map(format_rp_value)

        if "binding" in df.columns:
            df["binding"] = df["binding"].map(
                lambda v: "Binding" if v is True else ("Not Binding" if v is False else "N/A")
            )

        df = df.rename(columns=CONSTRAINT_TABLE_LABELS)
        return df

    @output(suspend_when_hidden=False)
    @render.ui
    def interpretation_block():
        processed = state.processed_results()
        if processed is None:
            return ui.div()

        text = processed["interpretation"]

        return ui.card(
            ui.card_header("Optimization Result Interpretation"),
            ui.card_body(ui.p(text)),
            class_="insight-block",
        )

    @render.download(filename="optimization_results.xlsx")
    def download_results():
        opt_result = state.optimization_result()
        processed = state.processed_results()

        if opt_result is None or processed is None:
            ui.notification_show(
                "No optimization results available to export. Run optimization first.",
                type="warning",
                duration=5,
            )
            return

        try:
            cc = state.collection_centers()
            rf = state.recycling_facilities()
            tc = state.transport_costs()

            filepath = export_results_to_excel(opt_result, processed, cc, rf, tc)

            with open(filepath, "rb") as f:
                yield f.read()
        except Exception as exc:
            ui.notification_show(f"Failed to export results: {exc}", type="error", duration=6)

    @render.download(filename="current_configuration.xlsx")
    def download_configuration():
        cc = state.collection_centers()
        rf = state.recycling_facilities()
        tc = state.transport_costs()

        if cc is None or rf is None or tc is None:
            ui.notification_show(
                "No active configuration available to export.",
                type="warning",
                duration=5,
            )
            return

        try:
            filepath = export_current_configuration(
                cc,
                rf,
                tc,
                "outputs/current_configuration.xlsx",
            )

            with open(filepath, "rb") as f:
                yield f.read()
        except Exception as exc:
            ui.notification_show(f"Failed to export configuration: {exc}", type="error", duration=6)
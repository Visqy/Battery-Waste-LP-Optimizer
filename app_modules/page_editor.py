import pandas as pd
from shiny import module, ui, render, reactive
from battery_optimizer.config import TRANSPORT_RATE_RP_PER_KG_PER_KM
from battery_optimizer.default_data import load_default_data


@module.ui
def editor_ui():
    return ui.nav_panel(
        "Parameter Editor",
        ui.div(
            ui.div(
                ui.div("Step 3 · Scenario Editing", class_="label"),
                ui.h2("Scenario Parameter Editor"),
                class_="page-header",
            ),
            ui.p(
                "Edit the active scenario directly in the application. These changes affect "
                "the next validation and optimization run. The mathematical model remains locked.",
                class_="body-text",
            ),
            ui.div(
                ui.tags.strong("Important: "),
                ui.span(
                    "After applying any parameter change, previous validation and optimization results are cleared. "
                    "Run validation again before using the scenario for decision review."
                ),
                class_="alert alert-info",
                style="margin-top: 20px;",
            ),
            ui.div(
                ui.input_action_button(
                    "reload_form",
                    "Reload Form from Active Scenario",
                    class_="btn-secondary",
                ),
                ui.input_action_button(
                    "reset_defaults",
                    "Reset Scenario to Default Data",
                    class_="btn-warning",
                ),
                style="display: flex; gap: 12px; margin-top: 20px;",
            ),
            ui.hr(class_="rule"),
            ui.div(
                ui.div("Supply", class_="label"),
                ui.h3("Collection Centers"),
                class_="sec-head",
            ),
            ui.p(
                "Edit collection center names, provinces, and available annual NMC battery waste supply.",
                class_="body-text",
            ),
            ui.output_ui("cc_editor"),
            ui.div(
                ui.input_action_button(
                    "apply_cc",
                    "Apply Collection Center Changes",
                    class_="btn-primary",
                ),
                style="margin-top: 16px;",
            ),
            ui.hr(class_="rule"),
            ui.div(
                ui.div("Capacity & Economics", class_="label"),
                ui.h3("Recycling Facilities"),
                class_="sec-head",
            ),
            ui.p(
                "Edit facility capacity, processing cost, and recovered material revenue assumptions.",
                class_="body-text",
            ),
            ui.output_ui("rf_editor"),
            ui.div(
                ui.input_action_button(
                    "apply_rf",
                    "Apply Recycling Facility Changes",
                    class_="btn-primary",
                ),
                style="margin-top: 16px;",
            ),
            ui.hr(class_="rule"),
            ui.div(
                ui.div("Routes", class_="label"),
                ui.h3("Transport Costs"),
                class_="sec-head",
            ),
            ui.p(
                "Enter transport cost in Rp/kg for each collection center and recycling facility pair. "
                "Distance is estimated as transport_cost / 20 for reference only.",
                class_="body-text",
            ),
            ui.output_ui("tc_editor"),
            ui.div(
                ui.input_action_button(
                    "apply_tc",
                    "Apply Transport Cost Changes",
                    class_="btn-primary",
                ),
                style="margin-top: 16px;",
            ),
            ui.output_ui("editor_status"),
            class_="page-content",
        ),
    )


@module.server
def editor_server(input, output, session, state):
    form_trigger = reactive.Value(0)
    status_message = reactive.Value("")

    @reactive.effect
    @reactive.event(input.reload_form)
    def _reload():
        form_trigger.set(form_trigger() + 1)
        status_message.set("Form reloaded from the active scenario.")

    @reactive.effect
    @reactive.event(input.reset_defaults)
    def _reset():
        cc, rf, tc = load_default_data()
        state.collection_centers.set(cc)
        state.recycling_facilities.set(rf)
        state.transport_costs.set(tc)
        state.data_source.set("default")
        state.validation_result.set(None)
        state.optimization_result.set(None)
        state.processed_results.set(None)
        form_trigger.set(form_trigger() + 1)
        status_message.set("Scenario reset to default baseline data.")

    @output
    @render.ui
    def cc_editor():
        form_trigger()
        with reactive.isolate():
            cc_df = state.collection_centers()

        rows = []
        for _, row in cc_df.iterrows():
            cc_id = str(row["cc_id"])
            safe_id = cc_id.replace("-", "_")
            rows.append(
                ui.card(
                    ui.card_header(f"Collection Center: {cc_id}"),
                    ui.card_body(
                        ui.layout_columns(
                            ui.input_text(
                                f"cc_name_{safe_id}",
                                "Name",
                                value=str(row.get("name", "")),
                            ),
                            ui.input_text(
                                f"cc_province_{safe_id}",
                                "Province",
                                value=str(row.get("province", "")),
                            ),
                            ui.input_numeric(
                                f"cc_supply_{safe_id}",
                                "Supply (kg/year)",
                                value=float(row.get("supply_kg", 0)),
                                min=0,
                                step=100,
                            ),
                            col_widths=[4, 4, 4],
                        )
                    ),
                    style="margin-bottom: 0.5rem;",
                )
            )
        return ui.div(*rows)

    @output
    @render.ui
    def rf_editor():
        form_trigger()
        with reactive.isolate():
            rf_df = state.recycling_facilities()

        rows = []
        for _, row in rf_df.iterrows():
            rf_id = str(row["rf_id"])
            safe_id = rf_id.replace("-", "_")
            rows.append(
                ui.card(
                    ui.card_header(f"Recycling Facility: {rf_id}"),
                    ui.card_body(
                        ui.layout_columns(
                            ui.input_text(
                                f"rf_name_{safe_id}",
                                "Name",
                                value=str(row.get("name", "")),
                            ),
                            ui.input_text(
                                f"rf_province_{safe_id}",
                                "Province",
                                value=str(row.get("province", "")),
                            ),
                            ui.input_numeric(
                                f"rf_capacity_{safe_id}",
                                "Capacity (kg/year)",
                                value=float(row.get("capacity_kg", 0)),
                                min=0,
                                step=1000,
                            ),
                            ui.input_numeric(
                                f"rf_proc_cost_{safe_id}",
                                "Processing Cost (Rp/kg)",
                                value=float(row.get("processing_cost_rp_kg", 0)),
                                min=0,
                                step=100,
                            ),
                            ui.input_numeric(
                                f"rf_rev_{safe_id}",
                                "Recovered Material Revenue (Rp/kg)",
                                value=float(row.get("recovery_revenue_rp_kg", 0)),
                                min=0,
                                step=100,
                            ),
                            col_widths=[2, 2, 3, 2, 3],
                        )
                    ),
                    style="margin-bottom: 0.5rem;",
                )
            )
        return ui.div(*rows)

    @output
    @render.ui
    def tc_editor():
        form_trigger()
        with reactive.isolate():
            tc_df = state.transport_costs()
            cc_df = state.collection_centers()
            rf_df = state.recycling_facilities()

        cc_ids = cc_df["cc_id"].tolist()
        rf_ids = rf_df["rf_id"].tolist()

        tc_lookup = {}
        for _, row in tc_df.iterrows():
            tc_lookup[(str(row["cc_id"]), str(row["rf_id"]))] = float(row["transport_cost_rp_kg"])

        header_cells = [ui.tags.th("CC / RF")] + [ui.tags.th(str(rf_id)) for rf_id in rf_ids]
        header_row = ui.tags.tr(*header_cells)

        body_rows = []
        for cc_id in cc_ids:
            safe_cc = str(cc_id).replace("-", "_")
            cells = [ui.tags.td(ui.tags.strong(str(cc_id)))]

            for rf_id in rf_ids:
                safe_rf = str(rf_id).replace("-", "_")
                current_val = tc_lookup.get((str(cc_id), str(rf_id)), 0.0)
                cells.append(
                    ui.tags.td(
                        ui.input_numeric(
                            f"tc_{safe_cc}_{safe_rf}",
                            label=None,
                            value=current_val,
                            min=0,
                            step=100,
                            width="120px",
                        )
                    )
                )

            body_rows.append(ui.tags.tr(*cells))

        return ui.div(
            ui.p("Transport Cost Matrix (Rp/kg)", style="font-weight: bold;"),
            ui.tags.table(
                ui.tags.thead(header_row),
                ui.tags.tbody(*body_rows),
                class_="table table-bordered table-sm",
            ),
        )

    @reactive.effect
    @reactive.event(input.apply_cc)
    def _apply_cc():
        with reactive.isolate():
            cc_df = state.collection_centers().copy()

        updated_rows = []
        for _, row in cc_df.iterrows():
            cc_id = str(row["cc_id"])
            safe_id = cc_id.replace("-", "_")

            try:
                new_name = input[f"cc_name_{safe_id}"]()
                new_province = input[f"cc_province_{safe_id}"]()
                new_supply = float(input[f"cc_supply_{safe_id}"]())
            except Exception:
                new_name = row.get("name", "")
                new_province = row.get("province", "")
                new_supply = float(row.get("supply_kg", 0))

            updated_rows.append(
                {
                    "cc_id": cc_id,
                    "name": new_name,
                    "province": new_province,
                    "supply_kg": new_supply,
                }
            )

        state.collection_centers.set(pd.DataFrame(updated_rows))
        state.validation_result.set(None)
        state.optimization_result.set(None)
        state.processed_results.set(None)
        status_message.set("Collection center parameters updated. Run validation before optimization.")

    @reactive.effect
    @reactive.event(input.apply_rf)
    def _apply_rf():
        with reactive.isolate():
            rf_df = state.recycling_facilities().copy()

        updated_rows = []
        for _, row in rf_df.iterrows():
            rf_id = str(row["rf_id"])
            safe_id = rf_id.replace("-", "_")

            try:
                new_name = input[f"rf_name_{safe_id}"]()
                new_province = input[f"rf_province_{safe_id}"]()
                new_cap = float(input[f"rf_capacity_{safe_id}"]())
                new_proc = float(input[f"rf_proc_cost_{safe_id}"]())
                new_rev = float(input[f"rf_rev_{safe_id}"]())
            except Exception:
                new_name = row.get("name", "")
                new_province = row.get("province", "")
                new_cap = float(row.get("capacity_kg", 0))
                new_proc = float(row.get("processing_cost_rp_kg", 0))
                new_rev = float(row.get("recovery_revenue_rp_kg", 0))

            updated_rows.append(
                {
                    "rf_id": rf_id,
                    "name": new_name,
                    "province": new_province,
                    "capacity_kg": new_cap,
                    "processing_cost_rp_kg": new_proc,
                    "recovery_revenue_rp_kg": new_rev,
                }
            )

        state.recycling_facilities.set(pd.DataFrame(updated_rows))
        state.validation_result.set(None)
        state.optimization_result.set(None)
        state.processed_results.set(None)
        status_message.set("Recycling facility parameters updated. Run validation before optimization.")

    @reactive.effect
    @reactive.event(input.apply_tc)
    def _apply_tc():
        with reactive.isolate():
            cc_df = state.collection_centers()
            rf_df = state.recycling_facilities()

        cc_ids = cc_df["cc_id"].tolist()
        rf_ids = rf_df["rf_id"].tolist()

        updated_rows = []
        for cc_id in cc_ids:
            safe_cc = str(cc_id).replace("-", "_")

            for rf_id in rf_ids:
                safe_rf = str(rf_id).replace("-", "_")

                try:
                    cost_val = float(input[f"tc_{safe_cc}_{safe_rf}"]())
                except Exception:
                    cost_val = 0.0

                dist_val = round(cost_val / TRANSPORT_RATE_RP_PER_KG_PER_KM)

                updated_rows.append(
                    {
                        "cc_id": str(cc_id),
                        "rf_id": str(rf_id),
                        "transport_cost_rp_kg": cost_val,
                        "distance_km": dist_val,
                    }
                )

        state.transport_costs.set(pd.DataFrame(updated_rows))
        state.validation_result.set(None)
        state.optimization_result.set(None)
        state.processed_results.set(None)
        status_message.set("Transport cost parameters updated. Run validation before optimization.")

    @output
    @render.ui
    def editor_status():
        msg = status_message()
        if not msg:
            return ui.div()

        return ui.div(
            ui.div(msg, class_="alert alert-success", style="margin-top: 1rem;")
        )
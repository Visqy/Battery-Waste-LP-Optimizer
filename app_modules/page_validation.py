from shiny import module, ui, render, reactive
from battery_optimizer.validation import validate_all


@module.ui
def validation_ui():
    return ui.nav_panel(
        "Validation",
        ui.div(
            ui.h2("Input Validation"),
            ui.p(
                "Run validation to check all input parameters before optimization. "
                "Optimization cannot proceed if any errors exist. Warnings are informational only."
            ),
            ui.input_action_button("run_validation", "Run Validation", class_="btn-primary"),
            ui.output_ui("validation_results"),
            style="padding: 1rem;",
        ),
    )


@module.server
def validation_server(input, output, session, state):
    @reactive.effect
    @reactive.event(input.run_validation)
    def _run():
        cc = state.collection_centers()
        rf = state.recycling_facilities()
        tc = state.transport_costs()
        result = validate_all(cc, rf, tc)
        state.validation_result.set(result)

    @output
    @render.ui
    def validation_results():
        result = state.validation_result()
        if result is None:
            return ui.div(
                ui.div(
                    "Click 'Run Validation' to check the current input data.",
                    class_="alert alert-info",
                    style="margin-top: 1rem;",
                )
            )

        status_color = "success" if result["is_valid"] else "danger"
        status_text = "PASSED - No errors found." if result["is_valid"] else "FAILED - Errors must be fixed before optimization."

        status_block = ui.div(
            ui.div(status_text, class_=f"alert alert-{status_color}"),
            style="margin-top: 1rem;",
        )

        error_block = ui.div()
        if result["errors"]:
            error_items = [ui.tags.li(e) for e in result["errors"]]
            error_block = ui.card(
                ui.card_header(f"Errors ({len(result['errors'])})"),
                ui.card_body(
                    ui.tags.ul(*error_items, style="color: red;")
                ),
                style="margin-top: 1rem; border-left: 4px solid red;",
            )

        warning_block = ui.div()
        if result["warnings"]:
            warn_items = [ui.tags.li(w) for w in result["warnings"]]
            warning_block = ui.card(
                ui.card_header(f"Warnings ({len(result['warnings'])})"),
                ui.card_body(
                    ui.tags.ul(*warn_items, style="color: #856404;")
                ),
                style="margin-top: 1rem; border-left: 4px solid #ffc107;",
            )

        summary = result.get("summary", {})
        summary_items = []
        if "num_collection_centers" in summary:
            summary_items.append(ui.tags.li(f"Collection centers: {summary['num_collection_centers']}"))
        if "num_recycling_facilities" in summary:
            summary_items.append(ui.tags.li(f"Recycling facilities: {summary['num_recycling_facilities']}"))
        if "total_supply_kg" in summary:
            summary_items.append(ui.tags.li(f"Total supply: {summary['total_supply_kg']:,.0f} kg/year"))
        if "total_capacity_kg" in summary:
            summary_items.append(ui.tags.li(f"Total capacity: {summary['total_capacity_kg']:,.0f} kg/year"))
        if "num_routes" in summary:
            summary_items.append(ui.tags.li(f"Transport cost routes: {summary['num_routes']}"))

        summary_block = ui.card(
            ui.card_header("Data Summary"),
            ui.card_body(ui.tags.ul(*summary_items)),
            style="margin-top: 1rem;",
        )

        return ui.div(status_block, error_block, warning_block, summary_block)
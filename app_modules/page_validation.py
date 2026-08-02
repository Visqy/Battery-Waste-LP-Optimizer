from shiny import module, ui, render, reactive
from battery_optimizer.validation import validate_all


@module.ui
def validation_ui():
    return ui.nav_panel(
        "Validation",
        ui.div(
            ui.div(
                ui.div("Step 4 · Feasibility Check", class_="label"),
                ui.h2("Scenario Data Validation"),
                class_="page-header",
            ),
            ui.p(
                "Run validation to check whether the active scenario is complete and suitable for optimization. "
                "Optimization should only be used after all errors are resolved.",
                class_="body-text",
            ),
            ui.div(
                ui.tags.strong("Validation role: "),
                ui.span(
                    "this step checks data completeness, consistency, and feasibility signals before the LP model is solved."
                ),
                class_="alert alert-info",
                style="margin-top: 20px;",
            ),
            ui.div(
                ui.input_action_button("run_validation", "Run Scenario Validation", class_="btn-primary"),
                style="margin-top: 20px;",
            ),
            ui.output_ui("validation_results"),
            class_="page-content",
        ),
    )


@module.server
def validation_server(input, output, session, state):
    @reactive.effect
    @reactive.event(input.run_validation)
    def _run():
        try:
            cc = state.collection_centers()
            rf = state.recycling_facilities()
            tc = state.transport_costs()
            result = validate_all(cc, rf, tc)
            state.validation_result.set(result)
            if result["is_valid"]:
                ui.notification_show("Validation passed.", type="message", duration=4)
            else:
                ui.notification_show(
                    f"Validation failed with {len(result['errors'])} error(s).",
                    type="warning",
                    duration=5,
                )
        except Exception as exc:
            ui.notification_show(f"Validation failed to run: {exc}", type="error", duration=6)

    @output(suspend_when_hidden=False)
    @render.ui
    def validation_results():
        result = state.validation_result()
        if result is None:
            return ui.div(
                ui.div(
                    "Click 'Run Scenario Validation' to check the active scenario before optimization.",
                    class_="alert alert-info",
                    style="margin-top: 1rem;",
                )
            )

        status_color = "success" if result["is_valid"] else "danger"
        status_text = (
            "PASSED - The scenario is ready for optimization."
            if result["is_valid"]
            else "FAILED - Fix all errors before optimization."
        )

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
                    ui.p("These issues block optimization and must be fixed."),
                    ui.tags.ul(*error_items, style="color: var(--red-600);"),
                ),
                style="margin-top: 1rem; border-left: 4px solid var(--red-600);",
            )

        warning_block = ui.div()
        if result["warnings"]:
            warn_items = [ui.tags.li(w) for w in result["warnings"]]
            warning_block = ui.card(
                ui.card_header(f"Warnings ({len(result['warnings'])})"),
                ui.card_body(
                    ui.p("Warnings do not block optimization, but they should be reviewed before interpreting results."),
                    ui.tags.ul(*warn_items, style="color: var(--amber-600);"),
                ),
                style="margin-top: 1rem; border-left: 4px solid var(--amber-400);",
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
            ui.card_header("Scenario Data Summary"),
            ui.card_body(
                ui.p("Use this summary to confirm the active scenario before running optimization."),
                ui.tags.ul(*summary_items),
            ),
            style="margin-top: 1rem;",
        )

        return ui.div(status_block, error_block, warning_block, summary_block)
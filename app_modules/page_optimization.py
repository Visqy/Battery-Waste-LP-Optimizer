from shiny import module, ui, render, reactive
from battery_optimizer.optimizer import solve_lp
from battery_optimizer.results import process_all_results


def formula_block(content):
    return ui.div(
        ui.HTML(content),
        class_="formula-block",
    )


@module.ui
def optimization_ui():
    return ui.nav_panel(
        "Optimization",
        ui.div(
            ui.div(
                ui.div("Step 5 · Solve", class_="label"),
                ui.h2("Scenario Optimization"),
                class_="page-header",
            ),
            ui.p(
                "Run the locked Linear Programming model to evaluate the active scenario. "
                "The result will be translated into decision indicators in the Results tab.",
                class_="body-text",
            ),
            ui.hr(class_="rule rule--sm"),
            ui.div(
                ui.div("Execution", class_="label"),
                ui.h3("Run Scenario Optimization"),
                class_="sec-head",
            ),
            ui.output_ui("validation_gate"),
            ui.div(
                ui.input_action_button(
                    "run_optimization",
                    "Run Optimization",
                    class_="btn-success btn-lg",
                ),
                style="margin-top: 16px;",
            ),
            ui.output_ui("opt_status"),
            ui.hr(class_="rule"),
            ui.div(
                ui.div(
                    ui.div("Solver", class_="label"),
                    ui.tags.ul(
                        ui.tags.li("Solver: COIN-OR CBC via PuLP"),
                        ui.tags.li("Model type: Linear Programming, single-objective"),
                        ui.tags.li("Decision role: evaluate allocation, capacity use, and net economic outcome"),
                        ui.tags.li("Objective: minimize total net cost"),
                        ui.tags.li(ui.HTML(r"Decision variables: \(x_{ij} \geq 0\), continuous")),
                        ui.tags.li("Constraints: supply limits and capacity limits"),
                    ),
                    class_="col-zone-col",
                ),
                ui.div(
                    ui.div("Locked Model", class_="label"),
                    formula_block(
                        r"""
                        \[
                        \min Z =
                        \sum_{i \in I}
                        \sum_{j \in J}
                        \left(C_{ij} + P_{j} - R_{j}\right)x_{ij}
                        \]
                        """
                    ),
                    ui.p("Subject to:"),
                    formula_block(
                        r"""
                        \[
                        \sum_{j \in J} x_{ij} \leq S_{i},
                        \quad \forall i \in I
                        \]
                        """
                    ),
                    formula_block(
                        r"""
                        \[
                        \sum_{i \in I} x_{ij} \leq Cap_{j},
                        \quad \forall j \in J
                        \]
                        """
                    ),
                    formula_block(
                        r"""
                        \[
                        x_{ij} \geq 0,
                        \quad \forall i \in I,\ j \in J
                        \]
                        """
                    ),
                    formula_block(
                        r"""
                        \[
                        y_{j} = 1,
                        \quad \forall j \in J
                        \]
                        """
                    ),
                    class_="col-zone-col",
                ),
                class_="col-zone-2",
            ),
            class_="page-content",
        ),
    )


@module.server
def optimization_server(input, output, session, state):
    @output(suspend_when_hidden=False)
    @render.ui
    def validation_gate():
        val_result = state.validation_result()
        if val_result is None:
            return ui.div(
                ui.div(
                    "Validation has not been run. Go to the Validation tab and validate the active scenario first.",
                    class_="alert alert-warning",
                    style="margin-bottom: 1rem;",
                )
            )

        if not val_result["is_valid"]:
            return ui.div(
                ui.div(
                    f"Validation failed with {len(val_result['errors'])} error(s). "
                    "Fix all errors in the Parameter Editor or Excel input, then re-run validation before optimization.",
                    class_="alert alert-danger",
                    style="margin-bottom: 1rem;",
                )
            )

        return ui.div(
            ui.div(
                "Validation passed. The active scenario is ready for optimization.",
                class_="alert alert-success",
                style="margin-bottom: 1rem;",
            )
        )

    @reactive.effect
    @reactive.event(input.run_optimization)
    def _run_opt():
        val_result = state.validation_result()
        if val_result is None:
            ui.notification_show(
                "Please run scenario validation first.",
                type="error",
                duration=4,
            )
            return

        if not val_result["is_valid"]:
            ui.notification_show(
                "The active scenario still has validation errors. Fix them before optimization.",
                type="error",
                duration=4,
            )
            return

        try:
            cc = state.collection_centers()
            rf = state.recycling_facilities()
            tc = state.transport_costs()

            opt_result = solve_lp(cc, rf, tc)
            state.optimization_result.set(opt_result)

            if opt_result["status"] == "Optimal":
                processed = process_all_results(opt_result, cc, rf, tc)
                state.processed_results.set(processed)
                ui.notification_show(
                    f"Optimization complete. Status: Optimal. Runtime: {opt_result['runtime']:.3f}s",
                    type="message",
                    duration=5,
                )
            else:
                state.processed_results.set(None)
                ui.notification_show(
                    f"Optimization returned status: {opt_result['status']}. Review scenario parameters.",
                    type="warning",
                    duration=6,
                )
        except Exception as exc:
            state.processed_results.set(None)
            ui.notification_show(f"Optimization failed to run: {exc}", type="error", duration=6)

    @output(suspend_when_hidden=False)
    @render.ui
    def opt_status():
        opt_result = state.optimization_result()
        if opt_result is None:
            return ui.div()

        status = opt_result["status"]
        obj = opt_result["objective_value"]
        rt = opt_result["runtime"]

        color = "success" if status == "Optimal" else "danger"
        obj_text = f"Rp {obj:,.2f}" if obj is not None else "N/A"

        return ui.div(
            ui.hr(),
            ui.h4("Last Scenario Optimization"),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Solver Status"),
                    ui.card_body(
                        ui.div(status, class_=f"badge bg-{color}", style="font-size: 1.1em;")
                    ),
                ),
                ui.card(
                    ui.card_header("Minimum Net Cost Objective (Rp/year)"),
                    ui.card_body(
                        ui.p(obj_text, style="font-weight: bold;"),
                        ui.tags.small(
                            "Open the Results tab for objective status, allocation results, and constraint diagnostics."
                        ),
                    ),
                ),
                ui.card(
                    ui.card_header("Runtime (seconds)"),
                    ui.card_body(ui.p(f"{rt:.4f}")),
                ),
                col_widths=[4, 4, 4],
            ),
            style="margin-top: 1rem;",
        )
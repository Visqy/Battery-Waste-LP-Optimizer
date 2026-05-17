from shiny import module, ui


@module.ui
def home_ui():
    return ui.nav_panel(
        "Home",
        ui.div(
            ui.div(
                ui.h1("NMC Battery Recycling Policy Decision Support Tool"),
                ui.p(
                    "A decision support interface for evaluating allocation, capacity, and economic outcomes "
                    "in the NMC electric vehicle battery recycling supply chain on Java Island, Indonesia."
                ),
                ui.p(
                    "The software is designed for researchers, planners, and policy stakeholders who need "
                    "transparent scenario-based evidence for recycling network assessment."
                ),
                style="padding: 2rem; background: #eaf4fb; border-radius: 8px; margin-bottom: 1.5rem;",
            ),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Decision Questions"),
                    ui.card_body(
                        ui.tags.ul(
                            ui.tags.li("Can the current recycling network absorb the available NMC battery waste supply?"),
                            ui.tags.li("Does the scenario generate a positive net economic benefit?"),
                            ui.tags.li("Is there unused supply or unused facility capacity?"),
                            ui.tags.li("Which facilities may become bottlenecks under the current scenario?"),
                            ui.tags.li("What follow-up analysis should be considered before policy action?"),
                        )
                    ),
                ),
                ui.card(
                    ui.card_header("Model Scope"),
                    ui.card_body(
                        ui.p("Single-objective Linear Programming model for allocation planning."),
                        ui.p("The model minimizes net cost while respecting supply and capacity constraints."),
                        ui.HTML(
                            r"""
                            <p>
                            Derived from the Kasy et al. (2024) MILP framework with
                            \(y_{j} = 1\) for all \(j\).
                            </p>
                            """
                        ),
                    ),
                ),
                ui.card(
                    ui.card_header("Locked Model"),
                    ui.card_body(
                        ui.HTML(
                            r"""
                            <p>
                            Objective:
                            \[
                            \min Z =
                            \sum_{i \in I}
                            \sum_{j \in J}
                            \left(C_{ij} + P_{j} - R_{j}\right)x_{ij}
                            \]
                            </p>
                            """
                        ),
                        ui.p("Users may edit parameters, but the objective function and constraints remain locked."),
                    ),
                ),
                col_widths=[4, 4, 4],
            ),
            ui.h3("Stakeholder Workflow", style="margin-top: 1.5rem;"),
            ui.layout_columns(
                ui.card(
                    ui.card_header("1. Define Scenario"),
                    ui.card_body(
                        ui.p("Use default data, upload a new Excel input, or edit parameters directly in the application.")
                    ),
                ),
                ui.card(
                    ui.card_header("2. Validate Data"),
                    ui.card_body(
                        ui.p("Check whether supply, capacity, cost, and route data are complete and feasible for optimization.")
                    ),
                ),
                ui.card(
                    ui.card_header("3. Run Optimization"),
                    ui.card_body(
                        ui.p("Solve the locked LP model using PuLP and CBC.")
                    ),
                ),
                ui.card(
                    ui.card_header("4. Review Decision Summary"),
                    ui.card_body(
                        ui.p("Read the executive decision summary, policy insight, and key indicators before reviewing technical tables.")
                    ),
                ),
                ui.card(
                    ui.card_header("5. Export Evidence"),
                    ui.card_body(
                        ui.p("Download the result workbook or export the current configuration for scenario reuse.")
                    ),
                ),
                col_widths=[2, 2, 2, 3, 3],
            ),
            ui.h3("Key Outputs", style="margin-top: 1.5rem;"),
            ui.tags.ul(
                ui.tags.li("Economic status and estimated net benefit or net cost"),
                ui.tags.li("Supply absorption rate and unused supply"),
                ui.tags.li("Capacity utilization and unused capacity"),
                ui.tags.li("Policy priority and recommended next analysis"),
                ui.tags.li("Allocation matrix and route allocation details"),
                ui.tags.li("Constraint slack and shadow price for technical review"),
            ),
            ui.h3("Data Units", style="margin-top: 1.5rem;"),
            ui.tags.ul(
                ui.tags.li("Volume: kilograms (kg) per year"),
                ui.tags.li("Monetary values: Indonesian Rupiah (Rp) per kg"),
                ui.tags.li("Reference period: Peak operating period, Period 4, Kasy et al. 2024"),
            ),
            style="padding: 1rem;",
        ),
    )


@module.server
def home_server(input, output, session, state):
    pass
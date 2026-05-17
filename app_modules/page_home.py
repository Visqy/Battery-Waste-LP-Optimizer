from shiny import module, ui


@module.ui
def home_ui():
    return ui.nav_panel(
        "Home",
        ui.div(
            ui.div(
                ui.h1("NMC Battery Recycling Supply Chain Optimizer"),
                ui.p(
                    "Decision support tool for optimizing the collection and recycling "
                    "of Nickel-Manganese-Cobalt (NMC) electric vehicle battery waste "
                    "on Java Island, Indonesia."
                ),
                style="padding: 2rem; background: #eaf4fb; border-radius: 8px; margin-bottom: 1.5rem;",
            ),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Model Type"),
                    ui.card_body(
                        ui.p("Single-objective Linear Programming (LP)"),
                        ui.p("Minimizes total net operating cost of the recycling supply chain."),
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
                    ui.card_header("Network Scale"),
                    ui.card_body(
                        ui.p("8 Collection Centers: Jakarta, Bekasi, Bandung, Surabaya, Tangerang, Bogor, Semarang, Yogyakarta"),
                        ui.p("2 Recycling Facilities: RF Jakarta, RF Surabaya"),
                        ui.HTML(
                            r"""
                            <p>
                            16 decision variables \(x_{ij}\) and 10 main constraints in the default network.
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
                        ui.p("Constraints: supply limits, capacity limits, and non-negativity."),
                        ui.p("Users may only edit parameters. The model formulation is locked."),
                    ),
                ),
                col_widths=[4, 4, 4],
            ),
            ui.h3("Workflow", style="margin-top: 1.5rem;"),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Step 1: Load Data"),
                    ui.card_body(ui.p("Use default data or upload an Excel file via the Upload Data tab.")),
                ),
                ui.card(
                    ui.card_header("Step 2: Edit Parameters"),
                    ui.card_body(ui.p("Adjust supply, capacity, costs, and revenues in the Parameter Editor tab.")),
                ),
                ui.card(
                    ui.card_header("Step 3: Validate"),
                    ui.card_body(ui.p("Run input validation. Fix all errors before proceeding.")),
                ),
                ui.card(
                    ui.card_header("Step 4: Optimize"),
                    ui.card_body(ui.p("Run the LP optimization with PuLP/CBC solver.")),
                ),
                ui.card(
                    ui.card_header("Step 5: View Results"),
                    ui.card_body(ui.p("Inspect allocation matrix, utilization, costs, and interpretation.")),
                ),
                ui.card(
                    ui.card_header("Step 6: Export"),
                    ui.card_body(ui.p("Download the full results or current configuration as Excel files.")),
                ),
                col_widths=[2, 2, 2, 2, 2, 2],
            ),
            ui.h3("Data Units", style="margin-top: 1.5rem;"),
            ui.tags.ul(
                ui.tags.li("Volume: kilograms (kg) per year"),
                ui.tags.li("Monetary values: Indonesian Rupiah (Rp) per kg"),
                ui.tags.li("Reference period: Peak operating period (Period 4, Kasy et al. 2024)"),
            ),
            style="padding: 1rem;",
        ),
    )


@module.server
def home_server(input, output, session, state):
    pass
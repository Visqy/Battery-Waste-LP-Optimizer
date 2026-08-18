from shiny import module, ui


def _wf_step(num: str, title: str, desc: str):
    """Helper: render one workflow step for the workflow-zone grid."""
    return ui.div(
        ui.div(num, class_="wf-num"),
        ui.div(title, class_="wf-title"),
        ui.div(desc, class_="wf-desc"),
        class_="wf-step",
    )


@module.ui
def home_ui():
    return ui.nav_panel(
        "Home",
        ui.div(
            ui.div(
                ui.div(
                    "Allocation Analysis Tool · Java Island, Indonesia",
                    class_="label",
                ),
                ui.h1("NMC Battery Recycling Allocation Optimizer"),
                ui.p(
                    "An open-source Shiny for Python application for linear-programming-based "
                    "battery recycling allocation analysis in the NMC electric vehicle battery "
                    "recycling supply chain on Java Island, Indonesia.",
                    class_="body-text",
                ),
                ui.p(
                    "The application validates scenario data, solves a documented linear "
                    "programming model, and presents allocation, capacity utilization, "
                    "constraint diagnostics, and exportable optimization results for "
                    "researchers, planners, and supply-chain analysts.",
                    class_="body-text",
                ),
                class_="page-header",
            ),
            ui.hr(class_="rule rule--lg"),
            ui.div(
                ui.div(
                    ui.div("Analysis Questions", class_="label"),
                    ui.tags.ul(
                        ui.tags.li(
                            "Can the current recycling network absorb the available "
                            "NMC battery waste supply?"
                        ),
                        ui.tags.li(
                            "What is the modeled net benefit or net cost for the scenario?"
                        ),
                        ui.tags.li(
                            "Is there unused supply or unused facility capacity?"
                        ),
                        ui.tags.li(
                            "Which facilities reach a binding capacity constraint under the current scenario?"
                        ),
                        ui.tags.li(
                            "What follow-up scenario or sensitivity analysis should be considered next?"
                        ),
                        class_="q-list",
                    ),
                    class_="col-zone-col",
                ),
                ui.div(
                    ui.div("Model Scope", class_="label"),
                    ui.p(
                        "Single-objective Linear Programming model for allocation planning.",
                        class_="scope-p",
                    ),
                    ui.p(
                        "The model minimizes net cost while respecting supply and capacity constraints.",
                        class_="scope-p",
                    ),
                    ui.HTML(
                        r"""<p class="scope-p">Derived from the Kasy et al. (2024) MILP framework """
                        r"""with \(y_j = 1\) for all \(j\).</p>"""
                    ),
                    class_="col-zone-col",
                ),
                ui.div(
                    ui.div("Locked Model", class_="label"),
                    ui.p(
                        "Objective function (read-only):",
                        style="font-size:12.5px; color:var(--text-3); margin-bottom:8px;",
                    ),
                    ui.div(
                        ui.HTML(
                            r"""\[\min Z = \sum_{i \in I}\sum_{j \in J}"""
                            r"""(C_{ij} + P_j - R_j)\,x_{ij}\]"""
                        ),
                        class_="formula-block",
                    ),
                    ui.p(
                        "Users may edit input parameters. The objective function and "
                        "constraints remain locked throughout the session.",
                        class_="formula-note",
                    ),
                    class_="col-zone-col",
                ),
                class_="col-zone",
            ),
            ui.hr(class_="rule rule--lg"),
            ui.div(
                ui.div("Workflow", class_="label"),
                ui.h2("User Workflow"),
                class_="sec-head",
            ),
            ui.div(
                _wf_step(
                    "01", "Define Scenario",
                    "Use default data, upload a new Excel input, or edit parameters "
                    "directly in the application.",
                ),
                _wf_step(
                    "02", "Validate Data",
                    "Check whether supply, capacity, cost, and route data are complete "
                    "and feasible for optimization.",
                ),
                _wf_step(
                    "03", "Run Optimization",
                    "Solve the locked LP model using PuLP and CBC solver backend.",
                ),
                _wf_step(
                    "04", "Review Summary",
                    "Read the optimization summary and key indicators before "
                    "reviewing allocation and constraint tables.",
                ),
                _wf_step(
                    "05", "Export Evidence",
                    "Download the result workbook or export the current configuration "
                    "for scenario reuse.",
                ),
                class_="workflow-zone",
            ),
            ui.hr(class_="rule rule--lg"),
            ui.div(
                ui.div("Outputs", class_="label"),
                ui.h2("Key Outputs"),
                class_="sec-head",
            ),
            ui.div(
                ui.div(
                    ui.span("01", class_="out-n"),
                    "Modeled objective status and net benefit or net cost",
                    class_="out-item",
                ),
                ui.div(
                    ui.span("02", class_="out-n"),
                    "Supply absorption rate and unused supply volume",
                    class_="out-item",
                ),
                ui.div(
                    ui.span("03", class_="out-n"),
                    "Capacity utilization and unused facility capacity per node",
                    class_="out-item",
                ),
                ui.div(
                    ui.span("04", class_="out-n"),
                    "Excel export of optimization results and current scenario configuration",
                    class_="out-item",
                ),
                ui.div(
                    ui.span("05", class_="out-n"),
                    "Optimal allocation table with routes and flow volumes",
                    class_="out-item",
                ),
                ui.div(
                    ui.span("06", class_="out-n"),
                    "Constraint slack and shadow price for technical review",
                    class_="out-item",
                ),
                class_="out-grid",
            ),
            ui.hr(class_="rule"),
            ui.div(ui.div("Data Units", class_="label"), style="margin-bottom:14px;"),
            ui.div(
                ui.div(
                    ui.span("—", class_="out-n"),
                    "Volume: kilograms (kg) per year",
                    class_="out-item",
                ),
                ui.div(
                    ui.span("—", class_="out-n"),
                    "Monetary values: Indonesian Rupiah (Rp) per kg",
                    class_="out-item",
                ),
                ui.div(
                    ui.span("—", class_="out-n"),
                    "Reference period: Illustrative baseline scenario, Period 4 projection, Kasy et al. 2024",
                    class_="out-item",
                    style="border-bottom: none;",
                ),
                ui.div(
                    ui.span("—", class_="out-n"),
                    "Solver: PuLP with CBC backend, Python 3.12",
                    class_="out-item",
                    style="border-bottom: none;",
                ),
                class_="out-grid",
            ),
            class_="page-content",
        ),
    )


@module.server
def home_server(input, output, session, state):
    pass

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
            # ── Page Header ──────────────────────────────────────────────────
            ui.div(
                ui.div(
                    "Decision Support Tool · Java Island, Indonesia",
                    class_="label",
                ),
                ui.h1("NMC Battery Recycling Policy Decision Support Tool"),
                ui.p(
                    "A decision support interface for evaluating allocation, capacity, "
                    "and economic outcomes in the NMC electric vehicle battery recycling "
                    "supply chain on Java Island, Indonesia.",
                    class_="body-text",
                ),
                ui.p(
                    "The software is designed for researchers, planners, and policy "
                    "stakeholders who need transparent scenario-based evidence for "
                    "recycling network assessment.",
                    class_="body-text",
                ),
                class_="page-header",
            ),
            ui.hr(class_="rule rule--lg"),
            # ── Three-Column Zone ────────────────────────────────────────────
            ui.div(
                # Column 1: Decision Questions
                ui.div(
                    ui.div("Decision Questions", class_="label"),
                    ui.tags.ul(
                        ui.tags.li(
                            "Can the current recycling network absorb the available "
                            "NMC battery waste supply?"
                        ),
                        ui.tags.li(
                            "Does the scenario generate a positive net economic benefit?"
                        ),
                        ui.tags.li(
                            "Is there unused supply or unused facility capacity?"
                        ),
                        ui.tags.li(
                            "Which facilities may become bottlenecks under the current scenario?"
                        ),
                        ui.tags.li(
                            "What follow-up analysis should be considered before policy action?"
                        ),
                        class_="q-list",
                    ),
                    class_="col-zone-col",
                ),
                # Column 2: Model Scope
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
                # Column 3: Locked Model
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
            # ── Stakeholder Workflow ─────────────────────────────────────────
            ui.div(
                ui.div("Workflow", class_="label"),
                ui.h2("Stakeholder Workflow"),
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
                    "Read the executive decision summary, policy insight, and key "
                    "indicators before reviewing technical tables.",
                ),
                _wf_step(
                    "05", "Export Evidence",
                    "Download the result workbook or export the current configuration "
                    "for scenario reuse.",
                ),
                class_="workflow-zone",
            ),
            ui.hr(class_="rule rule--lg"),
            # ── Key Outputs ──────────────────────────────────────────────────
            ui.div(
                ui.div("Outputs", class_="label"),
                ui.h2("Key Outputs"),
                class_="sec-head",
            ),
            ui.div(
                ui.div(
                    ui.span("01", class_="out-n"),
                    "Economic status and estimated net benefit or net cost",
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
                    "Policy priority score and recommended next-step analysis",
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
            # ── Data Units ───────────────────────────────────────────────────
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
                    "Reference period: Peak operating period, Period 4, Kasy et al. 2024",
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

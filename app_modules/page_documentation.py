from shiny import module, ui
from battery_optimizer.config import REFERENCE, APP_VERSION


def math_cell(content):
    return ui.HTML(content)


def formula_block(content):
    return ui.div(
        ui.HTML(content),
        style="background: #f4f4f4; padding: 1rem; border-radius: 4px; margin-bottom: 0.75rem;",
    )


@module.ui
def documentation_ui():
    return ui.nav_panel(
        "Documentation",
        ui.div(
            ui.h2("Model Documentation"),
            ui.navset_tab(
                ui.nav_panel(
                    "Overview",
                    ui.div(
                        ui.h3("Software Overview"),
                        ui.p(
                            "This software is a GUI-based decision support tool for optimizing "
                            "the supply chain of Nickel-Manganese-Cobalt (NMC) electric vehicle "
                            "battery recycling on Java Island, Indonesia."
                        ),
                        ui.p(f"Version: {APP_VERSION}"),
                        ui.p(f"Reference: {REFERENCE}"),
                        ui.h3("Model Origin"),
                        ui.HTML(
                            r"""
                            <p>
                            The model is derived from a multi-objective Mixed Integer Linear
                            Programming (MILP) framework developed by Kasy et al. (2024).
                            For this implementation, the model is simplified to a single-objective
                            Linear Programming (LP) problem by setting \(y_{j} = 1\) for all \(j\).
                            </p>
                            """
                        ),
                        ui.h3("Simplifications Applied"),
                        ui.tags.ol(
                            ui.tags.li(
                                ui.HTML(
                                    r"""
                                    S1. Elimination of binary variable \(y_{j}\): all recycling facilities
                                    are assumed to be active, \(y_{j} = 1\) for all \(j\). This converts the
                                    MILP into a pure LP.
                                    """
                                )
                            ),
                            ui.tags.li(
                                ui.HTML(
                                    r"""
                                    S2. Single-objective: only the economic objective \(Z_{1}\) is optimized.
                                    Environmental objective \(Z_{2}\) and material recovery objective \(Z_{3}\)
                                    are excluded.
                                    """
                                )
                            ),
                        ),
                    ),
                ),
                ui.nav_panel(
                    "Indices and Parameters",
                    ui.div(
                        ui.h3("Indices and Sets"),
                        ui.tags.table(
                            ui.tags.thead(
                                ui.tags.tr(
                                    ui.tags.th("Symbol"),
                                    ui.tags.th("Type"),
                                    ui.tags.th("Range"),
                                    ui.tags.th("Description"),
                                )
                            ),
                            ui.tags.tbody(
                                ui.tags.tr(ui.tags.td(math_cell(r"\(i\)")), ui.tags.td("Index"), ui.tags.td("1,...,m"), ui.tags.td("Index for collection centers")),
                                ui.tags.tr(ui.tags.td(math_cell(r"\(j\)")), ui.tags.td("Index"), ui.tags.td("1,...,n"), ui.tags.td("Index for recycling facilities")),
                                ui.tags.tr(ui.tags.td(math_cell(r"\(I\)")), ui.tags.td("Set"), ui.tags.td(math_cell(r"\(|I| = m\)")), ui.tags.td("Set of all collection centers")),
                                ui.tags.tr(ui.tags.td(math_cell(r"\(J\)")), ui.tags.td("Set"), ui.tags.td(math_cell(r"\(|J| = n\)")), ui.tags.td("Set of all recycling facilities")),
                            ),
                            class_="table table-bordered table-sm",
                        ),
                        ui.h3("Model Parameters"),
                        ui.tags.table(
                            ui.tags.thead(
                                ui.tags.tr(
                                    ui.tags.th("Symbol"),
                                    ui.tags.th("Unit"),
                                    ui.tags.th("Description"),
                                    ui.tags.th("Editable"),
                                )
                            ),
                            ui.tags.tbody(
                                ui.tags.tr(ui.tags.td(math_cell(r"\(C_{ij}\)")), ui.tags.td("Rp/kg"), ui.tags.td("Transport cost from collection center i to recycling facility j"), ui.tags.td("Yes")),
                                ui.tags.tr(ui.tags.td(math_cell(r"\(P_{j}\)")), ui.tags.td("Rp/kg"), ui.tags.td("Processing cost per kg at recycling facility j"), ui.tags.td("Yes")),
                                ui.tags.tr(ui.tags.td(math_cell(r"\(R_{j}\)")), ui.tags.td("Rp/kg"), ui.tags.td("Recovery revenue per kg from recycling facility j"), ui.tags.td("Yes")),
                                ui.tags.tr(ui.tags.td(math_cell(r"\(S_{i}\)")), ui.tags.td("kg/year"), ui.tags.td("Annual battery waste supply at collection center i"), ui.tags.td("Yes")),
                                ui.tags.tr(ui.tags.td(math_cell(r"\(Cap_{j}\)")), ui.tags.td("kg/year"), ui.tags.td("Annual processing capacity of recycling facility j"), ui.tags.td("Yes")),
                                ui.tags.tr(ui.tags.td(math_cell(r"\(y_{j}\)")), ui.tags.td("Binary"), ui.tags.td("Facility activation decision, locked at 1 for all j"), ui.tags.td("No, locked at 1")),
                            ),
                            class_="table table-bordered table-sm",
                        ),
                        ui.h3("Decision Variable"),
                        ui.HTML(
                            r"""
                            <p>
                            \(x_{ij}\): volume of NMC battery waste, in kg/year, allocated from
                            collection center \(i\) to recycling facility \(j\).
                            </p>
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
                        ui.HTML(
                            r"""
                            <p>
                            Total variables: \(m \times n\). For the default network, this equals
                            \(8 \times 2 = 16\) decision variables.
                            </p>
                            """
                        ),
                    ),
                ),
                ui.nav_panel(
                    "Objective and Constraints",
                    ui.div(
                        ui.h3("Objective Function"),
                        ui.p("Minimize total net operating cost:"),
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
                        ui.HTML(
                            r"""
                            <p>
                            The net cost coefficient is defined as
                            \( \tilde{c}_{ij} = C_{ij} + P_{j} - R_{j} \).
                            It is typically negative because
                            \(R_{j}\) is greater than \(P_{j} + C_{ij}\).
                            This means the optimizer will allocate as much volume as possible,
                            subject to supply and capacity constraints.
                            </p>
                            """
                        ),
                        ui.h3("Constraints"),
                        ui.h4("1. Supply Constraint"),
                        formula_block(
                            r"""
                            \[
                            \sum_{j \in J} x_{ij} \leq S_{i},
                            \quad \forall i \in I
                            \]
                            """
                        ),
                        ui.HTML(
                            r"""
                            <p>
                            Total volume shipped from collection center \(i\) cannot exceed its
                            available supply \(S_{i}\).
                            </p>
                            """
                        ),
                        ui.h4("2. Capacity Constraint"),
                        formula_block(
                            r"""
                            \[
                            \sum_{i \in I} x_{ij} \leq Cap_{j},
                            \quad \forall j \in J
                            \]
                            """
                        ),
                        ui.HTML(
                            r"""
                            <p>
                            Total volume received by recycling facility \(j\) cannot exceed its
                            annual processing capacity \(Cap_{j}\).
                            </p>
                            """
                        ),
                        ui.h4("3. Non-Negativity"),
                        formula_block(
                            r"""
                            \[
                            x_{ij} \geq 0,
                            \quad \forall i \in I,\ j \in J
                            \]
                            """
                        ),
                        ui.h3("Standard Form"),
                        ui.HTML(
                            r"""
                            <p>
                            After adding slack variables \(s_{i}^{sup}\) for supply and
                            \(s_{j}^{cap}\) for capacity, the model has \(m+n=10\) equality
                            constraints and \(m \times n + m + n = 26\) variables in standard
                            form for the default \(8 \times 2\) network.
                            </p>
                            """
                        ),
                    ),
                ),
                ui.nav_panel(
                    "Sensitivity Analysis",
                    ui.div(
                        ui.h3("Shadow Prices"),
                        ui.p(
                            "Shadow prices, or dual variables, indicate how much the objective value "
                            "changes per unit increase in the right-hand side of each constraint."
                        ),
                        ui.tags.ul(
                            ui.tags.li(
                                ui.HTML(
                                    r"""
                                    Shadow price for supply constraint \(i\), denoted as
                                    \(\lambda_{i}^{sup}\): value of one additional kg of supply
                                    at collection center \(i\).
                                    """
                                )
                            ),
                            ui.tags.li(
                                ui.HTML(
                                    r"""
                                    Shadow price for capacity constraint \(j\), denoted as
                                    \(\lambda_{j}^{cap}\): value of one additional kg of capacity
                                    at recycling facility \(j\).
                                    """
                                )
                            ),
                        ),
                        ui.h3("Slack Variables"),
                        ui.tags.ul(
                            ui.tags.li(ui.HTML(r"\(s_{i}^{sup} > 0\): unused supply at collection center \(i\), non-binding.")),
                            ui.tags.li(ui.HTML(r"\(s_{i}^{sup} = 0\): all supply at collection center \(i\) is allocated, binding constraint.")),
                            ui.tags.li(ui.HTML(r"\(s_{j}^{cap} > 0\): idle capacity at recycling facility \(j\).")),
                            ui.tags.li(ui.HTML(r"\(s_{j}^{cap} = 0\): facility \(j\) is at full capacity and acts as a bottleneck.")),
                        ),
                    ),
                ),
                ui.nav_panel(
                    "Assumptions and Limitations",
                    ui.div(
                        ui.h3("Assumptions"),
                        ui.tags.ol(
                            ui.tags.li(ui.HTML(r"All recycling facilities are active: \(y_{j}=1\) for all \(j\).")),
                            ui.tags.li("Deterministic model: supply, capacity, and cost parameters are assumed to be known and constant for the planning period."),
                            ui.tags.li("Single planning period: all parameters refer to one year."),
                            ui.tags.li("Proportional costs: total transport cost is proportional to volume allocated on each route."),
                            ui.tags.li("Homogeneous material: all battery waste is treated as equivalent NMC material."),
                        ),
                        ui.h3("Limitations"),
                        ui.tags.ol(
                            ui.tags.li(ui.HTML(r"Environmental objective \(Z_{2}\), carbon emissions, is not included.")),
                            ui.tags.li(ui.HTML(r"Material recovery efficiency objective \(Z_{3}\) is not included.")),
                            ui.tags.li(ui.HTML(r"Facility location decisions using binary \(y_{j}\) variables are not optimized.")),
                            ui.tags.li("Uncertainty and stochastic supply variations are not modeled."),
                            ui.tags.li("Multi-period planning is not supported."),
                            ui.tags.li("Intermediate processing nodes, such as sortation centers, are not modeled."),
                        ),
                        ui.h3("Future Development"),
                        ui.HTML(
                            r"""
                            <p>
                            Full integration of \(Z_{2}\), \(Z_{3}\), and binary \(y_{j}\)
                            variables as described in Kasy et al. (2024) is identified as the
                            primary direction for future development.
                            </p>
                            """
                        ),
                    ),
                ),
                ui.nav_panel(
                    "References",
                    ui.div(
                        ui.h3("References"),
                        ui.tags.ol(
                            ui.tags.li(
                                "Kasy, F.I., Hisjam, M., Jauhari, W.A., & Hassan, S.A.H.S. (2024). "
                                "Optimizing the Supply Chain for Recycling Electric Vehicle NMC Batteries. "
                                "Jurnal Optimasi Sistem Industri, 23(2), 207-226. "
                                "https://doi.org/10.25077/josi.v23.n2.p207-226.2024"
                            ),
                            ui.tags.li(
                                "Tadaros, M., Migdalas, A., Samuelsson, B., & Segerstedt, A. (2022). "
                                "Location of facilities and network design for reverse logistics of "
                                "lithium-ion batteries in Sweden. Operational Research, 22, 3789-3811."
                            ),
                            ui.tags.li(
                                "Hillier, F.S., & Lieberman, G.J. (2015). "
                                "Introduction to Operations Research (10th ed.). McGraw-Hill Education."
                            ),
                            ui.tags.li(
                                "Bazaraa, M.S., Jarvis, J.J., & Sherali, H.D. (2010). "
                                "Linear Programming and Network Flows (4th ed.). John Wiley & Sons."
                            ),
                        ),
                    ),
                ),
            ),
            style="padding: 1rem;",
        ),
    )


@module.server
def documentation_server(input, output, session, state):
    pass
import os
from shiny import module, ui, render, reactive
from battery_optimizer.io_excel import create_excel_template
from battery_optimizer.config import (
    TEMPLATE_PATH,
    SHEET_CC,
    SHEET_RF,
    SHEET_TC,
    CC_REQUIRED_COLS,
    RF_REQUIRED_COLS,
    TC_REQUIRED_COLS,
)


@module.ui
def template_ui():
    return ui.nav_panel(
        "Template",
        ui.div(
            ui.h2("Download Scenario Input Template"),
            ui.p(
                "Use this template to prepare a recycling supply chain scenario outside the application. "
                "The completed workbook can be uploaded later as the active scenario."
            ),
            ui.card(
                ui.card_header("Scenario Workbook"),
                ui.card_body(
                    ui.p(
                        "Download the Excel template, fill in collection centers, recycling facilities, "
                        "and route-level transport costs, then upload the completed file in the Upload Data tab."
                    ),
                    ui.p(
                        "The model formulation is locked. The workbook only changes scenario parameters.",
                        style="font-size: 0.95em; color: #555;",
                    ),
                    ui.download_button(
                        "download_template",
                        "Download battery_input_template.xlsx",
                        class_="btn-primary",
                    ),
                ),
            ),
            ui.h3("Required Sheet Structure", style="margin-top: 1.5rem;"),
            ui.layout_columns(
                ui.card(
                    ui.card_header(f"Sheet: {SHEET_CC}"),
                    ui.card_body(
                        ui.p(
                            "Use this sheet to define available NMC battery waste supply at each collection center.",
                            style="font-size: 0.9em; color: #555;",
                        ),
                        ui.tags.table(
                            ui.tags.thead(
                                ui.tags.tr(
                                    ui.tags.th("Column"),
                                    ui.tags.th("Type"),
                                    ui.tags.th("Description"),
                                )
                            ),
                            ui.tags.tbody(
                                ui.tags.tr(
                                    ui.tags.td("cc_id"),
                                    ui.tags.td("Text"),
                                    ui.tags.td("Unique collection center ID, e.g. CC01"),
                                ),
                                ui.tags.tr(
                                    ui.tags.td("name"),
                                    ui.tags.td("Text"),
                                    ui.tags.td("City or collection location name"),
                                ),
                                ui.tags.tr(
                                    ui.tags.td("province"),
                                    ui.tags.td("Text"),
                                    ui.tags.td("Province name"),
                                ),
                                ui.tags.tr(
                                    ui.tags.td("supply_kg"),
                                    ui.tags.td("Numeric"),
                                    ui.tags.td("Annual available NMC battery waste supply in kg"),
                                ),
                            ),
                            class_="table table-bordered table-sm",
                        ),
                    ),
                ),
                ui.card(
                    ui.card_header(f"Sheet: {SHEET_RF}"),
                    ui.card_body(
                        ui.p(
                            "Use this sheet to define recycling facility capacity, processing cost, and recovered material revenue.",
                            style="font-size: 0.9em; color: #555;",
                        ),
                        ui.tags.table(
                            ui.tags.thead(
                                ui.tags.tr(
                                    ui.tags.th("Column"),
                                    ui.tags.th("Type"),
                                    ui.tags.th("Description"),
                                )
                            ),
                            ui.tags.tbody(
                                ui.tags.tr(
                                    ui.tags.td("rf_id"),
                                    ui.tags.td("Text"),
                                    ui.tags.td("Unique recycling facility ID, e.g. RF01"),
                                ),
                                ui.tags.tr(
                                    ui.tags.td("name"),
                                    ui.tags.td("Text"),
                                    ui.tags.td("Facility name"),
                                ),
                                ui.tags.tr(
                                    ui.tags.td("province"),
                                    ui.tags.td("Text"),
                                    ui.tags.td("Province name"),
                                ),
                                ui.tags.tr(
                                    ui.tags.td("capacity_kg"),
                                    ui.tags.td("Numeric"),
                                    ui.tags.td("Annual processing capacity in kg"),
                                ),
                                ui.tags.tr(
                                    ui.tags.td("processing_cost_rp_kg"),
                                    ui.tags.td("Numeric"),
                                    ui.tags.td("Processing cost in Rp/kg"),
                                ),
                                ui.tags.tr(
                                    ui.tags.td("recovery_revenue_rp_kg"),
                                    ui.tags.td("Numeric"),
                                    ui.tags.td("Recovered material revenue in Rp/kg"),
                                ),
                            ),
                            class_="table table-bordered table-sm",
                        ),
                    ),
                ),
                ui.card(
                    ui.card_header(f"Sheet: {SHEET_TC}"),
                    ui.card_body(
                        ui.p(
                            "Use this sheet to define route-level transport costs between collection centers and facilities.",
                            style="font-size: 0.9em; color: #555;",
                        ),
                        ui.tags.table(
                            ui.tags.thead(
                                ui.tags.tr(
                                    ui.tags.th("Column"),
                                    ui.tags.th("Type"),
                                    ui.tags.th("Description"),
                                )
                            ),
                            ui.tags.tbody(
                                ui.tags.tr(
                                    ui.tags.td("cc_id"),
                                    ui.tags.td("Text"),
                                    ui.tags.td("Collection center ID. Must match the collection_centers sheet."),
                                ),
                                ui.tags.tr(
                                    ui.tags.td("rf_id"),
                                    ui.tags.td("Text"),
                                    ui.tags.td("Recycling facility ID. Must match the recycling_facilities sheet."),
                                ),
                                ui.tags.tr(
                                    ui.tags.td("transport_cost_rp_kg"),
                                    ui.tags.td("Numeric"),
                                    ui.tags.td("Transport cost in Rp/kg"),
                                ),
                                ui.tags.tr(
                                    ui.tags.td("distance_km"),
                                    ui.tags.td("Numeric, optional"),
                                    ui.tags.td("Road distance in km. Used as reference only."),
                                ),
                            ),
                            class_="table table-bordered table-sm",
                        ),
                        ui.p(
                            "One row is required for every collection center and recycling facility pair. "
                            "For the default network, 8 collection centers and 2 facilities require 16 route rows.",
                            style="margin-top: 0.5rem; font-size: 0.9em; color: #555;",
                        ),
                    ),
                ),
                col_widths=[4, 4, 4],
            ),
            ui.div(
                ui.tags.strong("Before upload: "),
                ui.span(
                    "check that all IDs match across sheets, all numeric values are non-negative, "
                    "and every route pair is included."
                ),
                class_="alert alert-info",
                style="margin-top: 1.5rem;",
            ),
            style="padding: 1rem;",
        ),
    )


@module.server
def template_server(input, output, session, state):
    @render.download(filename="battery_input_template.xlsx")
    def download_template():
        path = create_excel_template(TEMPLATE_PATH)
        with open(path, "rb") as f:
            yield f.read()
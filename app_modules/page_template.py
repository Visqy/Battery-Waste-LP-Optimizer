import os
from shiny import module, ui, render, reactive
from battery_optimizer.io_excel import create_excel_template
from battery_optimizer.config import TEMPLATE_PATH, SHEET_CC, SHEET_RF, SHEET_TC, CC_REQUIRED_COLS, RF_REQUIRED_COLS, TC_REQUIRED_COLS


@module.ui
def template_ui():
    return ui.nav_panel(
        "Template",
        ui.div(
            ui.h2("Download Excel Input Template"),
            ui.card(
                ui.card_header("Instructions"),
                ui.card_body(
                    ui.p(
                        "Download the template below, fill in your data following the column "
                        "specifications, and upload the completed file in the Upload Data tab."
                    ),
                    ui.download_button("download_template", "Download battery_input_template.xlsx", class_="btn-primary"),
                ),
            ),
            ui.h3("Sheet Structure", style="margin-top: 1.5rem;"),
            ui.layout_columns(
                ui.card(
                    ui.card_header(f"Sheet: {SHEET_CC}"),
                    ui.card_body(
                        ui.tags.table(
                            ui.tags.thead(
                                ui.tags.tr(
                                    ui.tags.th("Column"),
                                    ui.tags.th("Type"),
                                    ui.tags.th("Description"),
                                )
                            ),
                            ui.tags.tbody(
                                ui.tags.tr(ui.tags.td("cc_id"), ui.tags.td("Text"), ui.tags.td("Unique collection center ID, e.g. CC01")),
                                ui.tags.tr(ui.tags.td("name"), ui.tags.td("Text"), ui.tags.td("City or location name")),
                                ui.tags.tr(ui.tags.td("province"), ui.tags.td("Text"), ui.tags.td("Province name")),
                                ui.tags.tr(ui.tags.td("supply_kg"), ui.tags.td("Numeric"), ui.tags.td("Annual supply of battery waste in kg")),
                            ),
                            class_="table table-bordered table-sm",
                        )
                    ),
                ),
                ui.card(
                    ui.card_header(f"Sheet: {SHEET_RF}"),
                    ui.card_body(
                        ui.tags.table(
                            ui.tags.thead(
                                ui.tags.tr(
                                    ui.tags.th("Column"),
                                    ui.tags.th("Type"),
                                    ui.tags.th("Description"),
                                )
                            ),
                            ui.tags.tbody(
                                ui.tags.tr(ui.tags.td("rf_id"), ui.tags.td("Text"), ui.tags.td("Unique recycling facility ID, e.g. RF01")),
                                ui.tags.tr(ui.tags.td("name"), ui.tags.td("Text"), ui.tags.td("Facility name")),
                                ui.tags.tr(ui.tags.td("province"), ui.tags.td("Text"), ui.tags.td("Province name")),
                                ui.tags.tr(ui.tags.td("capacity_kg"), ui.tags.td("Numeric"), ui.tags.td("Annual processing capacity in kg")),
                                ui.tags.tr(ui.tags.td("processing_cost_rp_kg"), ui.tags.td("Numeric"), ui.tags.td("Processing cost in Rp/kg")),
                                ui.tags.tr(ui.tags.td("recovery_revenue_rp_kg"), ui.tags.td("Numeric"), ui.tags.td("Recovery revenue in Rp/kg")),
                            ),
                            class_="table table-bordered table-sm",
                        )
                    ),
                ),
                ui.card(
                    ui.card_header(f"Sheet: {SHEET_TC}"),
                    ui.card_body(
                        ui.tags.table(
                            ui.tags.thead(
                                ui.tags.tr(
                                    ui.tags.th("Column"),
                                    ui.tags.th("Type"),
                                    ui.tags.th("Description"),
                                )
                            ),
                            ui.tags.tbody(
                                ui.tags.tr(ui.tags.td("cc_id"), ui.tags.td("Text"), ui.tags.td("Collection center ID (must match collection_centers sheet)")),
                                ui.tags.tr(ui.tags.td("rf_id"), ui.tags.td("Text"), ui.tags.td("Recycling facility ID (must match recycling_facilities sheet)")),
                                ui.tags.tr(ui.tags.td("transport_cost_rp_kg"), ui.tags.td("Numeric"), ui.tags.td("Transport cost in Rp/kg")),
                                ui.tags.tr(ui.tags.td("distance_km"), ui.tags.td("Numeric (optional)"), ui.tags.td("Road distance in km (reference only)")),
                            ),
                            class_="table table-bordered table-sm",
                        ),
                        ui.p(
                            "One row required for every (cc_id, rf_id) pair. "
                            "If there are 8 collection centers and 2 facilities, the sheet must have 16 rows.",
                            style="margin-top: 0.5rem; font-size: 0.9em; color: #555;",
                        ),
                    ),
                ),
                col_widths=[4, 4, 4],
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
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


def _struct_table(rows):
    """Build a column-definition table from a list of (column, type, description) tuples."""
    return ui.tags.table(
        ui.tags.thead(
            ui.tags.tr(
                ui.tags.th("Column"),
                ui.tags.th("Type"),
                ui.tags.th("Description"),
            )
        ),
        ui.tags.tbody(
            *[
                ui.tags.tr(
                    ui.tags.td(col),
                    ui.tags.td(typ),
                    ui.tags.td(desc),
                )
                for col, typ, desc in rows
            ]
        ),
    )


@module.ui
def template_ui():
    return ui.nav_panel(
        "Template",
        ui.div(
            ui.div(
                ui.div("Step 1 · Scenario Preparation", class_="label"),
                ui.h2("Download Scenario Input Template"),
                class_="page-header",
            ),
            ui.p(
                "Use this template to prepare a recycling supply chain scenario outside "
                "the application. The completed workbook can be uploaded later as the "
                "active scenario.",
                class_="body-text",
            ),
            ui.hr(class_="rule rule--sm"),
            ui.div(
                ui.div("Workbook", class_="label"),
                ui.h3("Scenario Workbook"),
                class_="sec-head",
            ),
            ui.p(
                "Download the Excel template, fill in collection centers, recycling "
                "facilities, and route-level transport costs, then upload the completed "
                "file in the Upload Data tab.",
                class_="body-text",
            ),
            ui.p(
                "The model formulation is locked. The workbook only changes scenario parameters.",
                class_="formula-note",
            ),
            ui.div(
                ui.download_button(
                    "download_template",
                    "Download battery_input_template.xlsx",
                    class_="btn-primary",
                ),
                style="margin-top: 20px;",
            ),
            ui.hr(class_="rule"),
            ui.div(
                ui.div("Reference", class_="label"),
                ui.h3("Required Sheet Structure"),
                class_="sec-head",
            ),
            ui.div(
                ui.div(
                    ui.div(f"Sheet: {SHEET_CC}", class_="label"),
                    ui.p(
                        "Use this sheet to define available NMC battery waste supply at "
                        "each collection center.",
                        class_="scope-p",
                    ),
                    _struct_table(
                        [
                            ("cc_id", "Text", "Unique collection center ID, e.g. CC01"),
                            ("name", "Text", "City or collection location name"),
                            ("province", "Text", "Province name"),
                            ("supply_kg", "Numeric", "Annual available NMC battery waste supply in kg"),
                        ]
                    ),
                    class_="col-zone-col",
                ),
                ui.div(
                    ui.div(f"Sheet: {SHEET_RF}", class_="label"),
                    ui.p(
                        "Use this sheet to define recycling facility capacity, processing "
                        "cost, and recovered material revenue.",
                        class_="scope-p",
                    ),
                    _struct_table(
                        [
                            ("rf_id", "Text", "Unique recycling facility ID, e.g. RF01"),
                            ("name", "Text", "Facility name"),
                            ("province", "Text", "Province name"),
                            ("capacity_kg", "Numeric", "Annual processing capacity in kg"),
                            ("processing_cost_rp_kg", "Numeric", "Processing cost in Rp/kg"),
                            ("recovery_revenue_rp_kg", "Numeric", "Recovered material revenue in Rp/kg"),
                        ]
                    ),
                    class_="col-zone-col",
                ),
                ui.div(
                    ui.div(f"Sheet: {SHEET_TC}", class_="label"),
                    ui.p(
                        "Use this sheet to define route-level transport costs between "
                        "collection centers and facilities.",
                        class_="scope-p",
                    ),
                    _struct_table(
                        [
                            ("cc_id", "Text", "Collection center ID. Must match the collection_centers sheet."),
                            ("rf_id", "Text", "Recycling facility ID. Must match the recycling_facilities sheet."),
                            ("transport_cost_rp_kg", "Numeric", "Transport cost in Rp/kg"),
                            ("distance_km", "Numeric, optional", "Road distance in km. Used as reference only."),
                        ]
                    ),
                    ui.p(
                        "One row is required for every collection center and recycling "
                        "facility pair. For the default network, 8 collection centers and "
                        "2 facilities require 16 route rows.",
                        class_="formula-note",
                    ),
                    class_="col-zone-col",
                ),
                class_="col-zone",
            ),
            ui.div(
                ui.tags.strong("Before upload: "),
                ui.span(
                    "check that all IDs match across sheets, all numeric values are "
                    "non-negative, and every route pair is included."
                ),
                class_="alert alert-info",
                style="margin-top: 32px;",
            ),
            class_="page-content",
        ),
    )


@module.server
def template_server(input, output, session, state):
    @render.download(filename="battery_input_template.xlsx")
    def download_template():
        path = create_excel_template(TEMPLATE_PATH)
        with open(path, "rb") as f:
            yield f.read()

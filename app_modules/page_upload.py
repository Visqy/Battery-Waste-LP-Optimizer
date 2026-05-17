from shiny import module, ui, render, reactive, req
from battery_optimizer.io_excel import read_excel_input
from battery_optimizer.config import TRANSPORT_RATE_RP_PER_KG_PER_KM
import pandas as pd


@module.ui
def upload_ui():
    return ui.nav_panel(
        "Upload Data",
        ui.div(
            ui.h2("Upload Excel Input File"),
            ui.card(
                ui.card_header("File Upload"),
                ui.card_body(
                    ui.input_file(
                        "file_upload",
                        "Select .xlsx file",
                        accept=[".xlsx"],
                        multiple=False,
                    ),
                    ui.output_ui("upload_status"),
                ),
            ),
            ui.output_ui("preview_section"),
            style="padding: 1rem;",
        ),
    )


@module.server
def upload_server(input, output, session, state):
    upload_errors = reactive.Value([])
    upload_success = reactive.Value(False)

    @reactive.effect
    @reactive.event(input.file_upload)
    def _handle_upload():
        file_info = input.file_upload()
        if file_info is None or len(file_info) == 0:
            return

        filepath = file_info[0]["datapath"]
        cc_df, rf_df, tc_df, errors = read_excel_input(filepath)

        if errors:
            upload_errors.set(errors)
            upload_success.set(False)
            return

        if "distance_km" not in tc_df.columns and tc_df is not None:
            if "transport_cost_rp_kg" in tc_df.columns:
                tc_df = tc_df.copy()
                tc_df["distance_km"] = (
                    tc_df["transport_cost_rp_kg"] / TRANSPORT_RATE_RP_PER_KG_PER_KM
                ).round(0).astype(int)

        state.collection_centers.set(cc_df)
        state.recycling_facilities.set(rf_df)
        state.transport_costs.set(tc_df)
        state.data_source.set("uploaded")
        state.validation_result.set(None)
        state.optimization_result.set(None)
        state.processed_results.set(None)
        upload_errors.set([])
        upload_success.set(True)

    @output
    @render.ui
    def upload_status():
        errors = upload_errors()
        if upload_success():
            source = state.data_source()
            cc = state.collection_centers()
            rf = state.recycling_facilities()
            tc = state.transport_costs()
            return ui.div(
                ui.div(
                    f"File uploaded successfully. "
                    f"Loaded {len(cc)} collection centers, "
                    f"{len(rf)} recycling facilities, "
                    f"{len(tc)} transport cost routes.",
                    class_="alert alert-success",
                )
            )
        if errors:
            error_items = [ui.tags.li(e) for e in errors]
            return ui.div(
                ui.div(
                    ui.p("Upload failed with the following errors:"),
                    ui.tags.ul(*error_items),
                    class_="alert alert-danger",
                )
            )
        ds = state.data_source()
        return ui.div(
            ui.div(
                f"Currently using: {ds} data. Upload a file to replace.",
                class_="alert alert-info",
            )
        )

    @output
    @render.ui
    def preview_section():
        if not upload_success():
            return ui.div()

        cc = state.collection_centers()
        rf = state.recycling_facilities()
        tc = state.transport_costs()

        return ui.div(
            ui.h3("Data Preview", style="margin-top: 1.5rem;"),
            ui.navset_tab(
                ui.nav_panel(
                    "Collection Centers",
                    ui.output_table("preview_cc"),
                ),
                ui.nav_panel(
                    "Recycling Facilities",
                    ui.output_table("preview_rf"),
                ),
                ui.nav_panel(
                    "Transport Costs",
                    ui.output_table("preview_tc"),
                ),
            ),
        )

    @output
    @render.table
    def preview_cc():
        req(upload_success())
        return state.collection_centers()

    @output
    @render.table
    def preview_rf():
        req(upload_success())
        return state.recycling_facilities()

    @output
    @render.table
    def preview_tc():
        req(upload_success())
        return state.transport_costs()
from shiny import module, ui, render, reactive, req
from battery_optimizer.io_excel import read_excel_input
from battery_optimizer.config import TRANSPORT_RATE_RP_PER_KG_PER_KM


@module.ui
def upload_ui():
    return ui.nav_panel(
        "Upload Data",
        ui.div(
            ui.div(
                ui.div("Step 2 · Scenario Input", class_="label"),
                ui.h2("Upload Scenario Data"),
                class_="page-header",
            ),
            ui.p(
                "Upload a completed Excel workbook to replace the active scenario. "
                "After upload, run validation before optimization.",
                class_="body-text",
            ),
            ui.hr(class_="rule rule--sm"),
            ui.card(
                ui.card_header("Scenario File Upload"),
                ui.card_body(
                    ui.input_file(
                        "file_upload",
                        "Select .xlsx scenario file",
                        accept=[".xlsx"],
                        multiple=False,
                    ),
                    ui.tags.small(
                        "The file must follow the template structure: collection_centers, recycling_facilities, and transport_costs.",
                    ),
                    ui.output_ui("upload_status"),
                ),
            ),
            ui.output_ui("preview_section"),
            class_="page-content",
        ),
    )


@module.server
def upload_server(input, output, session, state):
    upload_errors = reactive.Value([])
    upload_success = reactive.Value(False)

    @reactive.effect
    @reactive.event(input.file_upload)
    def _handle_upload():
        try:
            file_info = input.file_upload()
            if file_info is None or len(file_info) == 0:
                return

            filepath = file_info[0]["datapath"]
            cc_df, rf_df, tc_df, errors = read_excel_input(filepath)

            if errors:
                upload_errors.set(errors)
                upload_success.set(False)
                ui.notification_show(
                    f"Upload failed with {len(errors)} issue(s). See details below.",
                    type="error",
                    duration=6,
                )
                return

            if tc_df is not None and "distance_km" not in tc_df.columns:
                if "transport_cost_rp_kg" in tc_df.columns:
                    tc_df = tc_df.copy()
                    tc_df["distance_km"] = (
                        tc_df["transport_cost_rp_kg"] / TRANSPORT_RATE_RP_PER_KG_PER_KM
                    ).round(0).astype(int)

            state.collection_centers.set(cc_df)
            state.recycling_facilities.set(rf_df)
            state.transport_costs.set(tc_df)
            state.data_source.set("uploaded scenario")
            state.validation_result.set(None)
            state.optimization_result.set(None)
            state.processed_results.set(None)
            upload_errors.set([])
            upload_success.set(True)
            ui.notification_show("Scenario uploaded successfully.", type="message", duration=4)
        except Exception as exc:
            upload_errors.set([f"Unexpected error while reading file: {exc}"])
            upload_success.set(False)
            ui.notification_show(f"Upload failed: {exc}", type="error", duration=6)

    @output(suspend_when_hidden=False)
    @render.ui
    def upload_status():
        errors = upload_errors()

        if upload_success():
            cc = state.collection_centers()
            rf = state.recycling_facilities()
            tc = state.transport_costs()
            return ui.div(
                ui.div(
                    ui.tags.strong("Scenario uploaded successfully. "),
                    ui.span(
                        f"Loaded {len(cc)} collection centers, "
                        f"{len(rf)} recycling facilities, and "
                        f"{len(tc)} transport cost routes. Run validation before optimization."
                    ),
                    class_="alert alert-success",
                    style="margin-top: 1rem;",
                )
            )

        if errors:
            error_items = [ui.tags.li(e) for e in errors]
            return ui.div(
                ui.div(
                    ui.p("Upload failed. Fix the following issue(s) in the Excel workbook:"),
                    ui.tags.ul(*error_items),
                    class_="alert alert-danger",
                    style="margin-top: 1rem;",
                )
            )

        ds = state.data_source()
        return ui.div(
            ui.div(
                f"Current active data source: {ds}. Upload a scenario file to replace it.",
                class_="alert alert-info",
                style="margin-top: 1rem;",
            )
        )

    @output(suspend_when_hidden=False)
    @render.ui
    def preview_section():
        if not upload_success():
            return ui.div()

        return ui.div(
            ui.h3("Uploaded Scenario Preview", style="margin-top: 1.5rem;"),
            ui.p(
                "Review the uploaded records below. If the scenario is correct, continue to the Validation tab.",
                style="color: var(--text-muted);",
            ),
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

    @output(suspend_when_hidden=False)
    @render.table
    def preview_cc():
        req(upload_success())
        return state.collection_centers()

    @output(suspend_when_hidden=False)
    @render.table
    def preview_rf():
        req(upload_success())
        return state.recycling_facilities()

    @output(suspend_when_hidden=False)
    @render.table
    def preview_tc():
        req(upload_success())
        return state.transport_costs()
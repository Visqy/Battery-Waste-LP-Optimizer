import os
import pandas as pd
from battery_optimizer.config import (
    SHEET_CC,
    SHEET_RF,
    SHEET_TC,
    REQUIRED_SHEETS,
    CC_REQUIRED_COLS,
    RF_REQUIRED_COLS,
    TC_REQUIRED_COLS,
    TEMPLATE_PATH,
    TRANSPORT_RATE_RP_PER_KG_PER_KM,
)


def normalize_columns(df):
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df


def read_excel_input(filepath):
    errors = []

    try:
        with pd.ExcelFile(filepath, engine="openpyxl") as xl:
            missing_sheets = [s for s in REQUIRED_SHEETS if s not in xl.sheet_names]

            if missing_sheets:
                errors.append(f"Missing required sheets: {', '.join(missing_sheets)}")
                return None, None, None, errors

            try:
                cc_df = normalize_columns(pd.read_excel(xl, sheet_name=SHEET_CC))
            except Exception as exc:
                errors.append(f"Cannot read sheet '{SHEET_CC}': {exc}")
                cc_df = None

            try:
                rf_df = normalize_columns(pd.read_excel(xl, sheet_name=SHEET_RF))
            except Exception as exc:
                errors.append(f"Cannot read sheet '{SHEET_RF}': {exc}")
                rf_df = None

            try:
                tc_df = normalize_columns(pd.read_excel(xl, sheet_name=SHEET_TC))
            except Exception as exc:
                errors.append(f"Cannot read sheet '{SHEET_TC}': {exc}")
                tc_df = None

    except Exception as exc:
        return None, None, None, [f"Cannot open file: {exc}"]

    if tc_df is not None and "distance_km" not in tc_df.columns:
        if "transport_cost_rp_kg" in tc_df.columns:
            tc_df["distance_km"] = (
                tc_df["transport_cost_rp_kg"] / TRANSPORT_RATE_RP_PER_KG_PER_KM
            ).round(0).astype(int)

    return cc_df, rf_df, tc_df, errors


def save_default_excel(cc_df, rf_df, tc_df, filepath):
    directory = os.path.dirname(filepath)

    if directory:
        os.makedirs(directory, exist_ok=True)

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        cc_df.to_excel(writer, sheet_name=SHEET_CC, index=False)
        rf_df.to_excel(writer, sheet_name=SHEET_RF, index=False)
        tc_df.to_excel(writer, sheet_name=SHEET_TC, index=False)

    return filepath


def create_excel_template(filepath=None):
    if filepath is None:
        filepath = TEMPLATE_PATH

    directory = os.path.dirname(filepath)

    if directory:
        os.makedirs(directory, exist_ok=True)

    cc_template = pd.DataFrame(columns=CC_REQUIRED_COLS)
    cc_template.loc[0] = ["CC01", "Jakarta", "DKI Jakarta", 258480]

    rf_template = pd.DataFrame(columns=RF_REQUIRED_COLS)
    rf_template.loc[0] = ["RF01", "RF Jakarta", "DKI Jakarta", 365000, 28360, 238400]

    tc_cols = TC_REQUIRED_COLS + ["distance_km"]
    tc_template = pd.DataFrame(columns=tc_cols)
    tc_template.loc[0] = ["CC01", "RF01", 2000, 100]

    instructions = pd.DataFrame(
        {
            "Sheet": [SHEET_CC, SHEET_RF, SHEET_TC],
            "Description": [
                "Collection centers with supply_kg per year",
                "Recycling facilities with capacity, processing cost, recovery revenue",
                "Transport cost in Rp/kg for each CC-RF pair. distance_km is optional.",
            ],
            "Required Columns": [
                ", ".join(CC_REQUIRED_COLS),
                ", ".join(RF_REQUIRED_COLS),
                ", ".join(TC_REQUIRED_COLS),
            ],
        }
    )

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        instructions.to_excel(writer, sheet_name="instructions", index=False)
        cc_template.to_excel(writer, sheet_name=SHEET_CC, index=False)
        rf_template.to_excel(writer, sheet_name=SHEET_RF, index=False)
        tc_template.to_excel(writer, sheet_name=SHEET_TC, index=False)

    return filepath

def export_current_configuration(cc_df, rf_df, tc_df, filepath):
    directory = os.path.dirname(filepath)

    if directory:
        os.makedirs(directory, exist_ok=True)

    metadata = pd.DataFrame(
        {
            "field": [
                "configuration_type",
                "model_type",
                "objective",
                "editable_parameters",
                "locked_model",
                "volume_unit",
                "currency",
            ],
            "value": [
                "current_user_configuration",
                "Linear Programming",
                "Minimize net economic cost",
                "supply, capacity, transportation cost, processing cost, recovery revenue",
                "objective function, constraints, solver logic",
                "kg/year",
                "IDR",
            ],
        }
    )

    scenario_notes = pd.DataFrame(
        {
            "notes": [
                "This workbook stores the current active input configuration exported from the GUI.",
                "The model formulation is locked. Only parameter values are exported.",
                "This file can be uploaded again as an input configuration.",
            ]
        }
    )

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        metadata.to_excel(writer, sheet_name="metadata", index=False)
        cc_df.to_excel(writer, sheet_name=SHEET_CC, index=False)
        rf_df.to_excel(writer, sheet_name=SHEET_RF, index=False)
        tc_df.to_excel(writer, sheet_name=SHEET_TC, index=False)
        scenario_notes.to_excel(writer, sheet_name="scenario_notes", index=False)

    return filepath
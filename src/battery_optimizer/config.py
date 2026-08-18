SOLVER_NAME = "CBC"
DEFAULT_DATA_PATH = "data/default_parameters.xlsx"
TEMPLATE_PATH = "data/battery_input_template.xlsx"
RESULTS_PATH = "data/optimization_results.xlsx"
CONFIG_EXPORT_PATH = "outputs/current_configuration.xlsx"

SHEET_CC = "collection_centers"
SHEET_RF = "recycling_facilities"
SHEET_TC = "transport_costs"
REQUIRED_SHEETS = [SHEET_CC, SHEET_RF, SHEET_TC]

CC_REQUIRED_COLS = ["cc_id", "name", "province", "supply_kg"]
RF_REQUIRED_COLS = [
    "rf_id", "name", "province",
    "capacity_kg", "processing_cost_rp_kg", "recovery_revenue_rp_kg",
]
TC_REQUIRED_COLS = ["cc_id", "rf_id", "transport_cost_rp_kg"]

TRANSPORT_RATE_RP_PER_KG_PER_KM = 20.0

APP_TITLE = "NMC Battery Recycling Allocation Optimizer"
APP_VERSION = "1.0.0"
REFERENCE = "Kasy et al. (2024), Jurnal Optimasi Sistem Industri, 23(2), 207-226"
MODEL_NAME = "NMC_Battery_LP"
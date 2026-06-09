import os
import pandas as pd
from battery_optimizer.config import (
    DEFAULT_DATA_PATH,
    TRANSPORT_RATE_RP_PER_KG_PER_KM,
)


def get_default_collection_centers():
    return pd.DataFrame(
        {
            "cc_id": ["CC01", "CC02", "CC03", "CC04", "CC05", "CC06", "CC07", "CC08"],
            "name": [
                "Jakarta", "Bekasi", "Bandung", "Surabaya",
                "Tangerang", "Bogor", "Semarang", "Yogyakarta",
            ],
            "province": [
                "DKI Jakarta", "Jawa Barat", "Jawa Barat", "Jawa Timur",
                "Banten", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta",
            ],
            "supply_kg": [258480, 59165, 17908, 57737, 47358, 3808, 23652, 5203],
        }
    )


def get_default_recycling_facilities():
    return pd.DataFrame(
        {
            "rf_id": ["RF01", "RF02"],
            "name": ["RF Jakarta", "RF Surabaya"],
            "province": ["DKI Jakarta", "Jawa Timur"],
            "capacity_kg": [365000, 365000],
            "processing_cost_rp_kg": [28360, 28360],
            "recovery_revenue_rp_kg": [238400, 238400],
        }
    )


def get_default_transport_costs():
    rows = [
        ("CC01", "RF01", 2000),
        ("CC01", "RF02", 17600),
        ("CC02", "RF01", 3000),
        ("CC02", "RF02", 17000),
        ("CC03", "RF01", 5800),
        ("CC03", "RF02", 15200),
        ("CC04", "RF01", 17600),
        ("CC04", "RF02", 2000),
        ("CC05", "RF01", 3200),
        ("CC05", "RF02", 18000),
        ("CC06", "RF01", 4400),
        ("CC06", "RF02", 16800),
        ("CC07", "RF01", 10200),
        ("CC07", "RF02", 8600),
        ("CC08", "RF01", 13000),
        ("CC08", "RF02", 6200),
    ]
    df = pd.DataFrame(rows, columns=["cc_id", "rf_id", "transport_cost_rp_kg"])
    df["distance_km"] = (
        df["transport_cost_rp_kg"] / TRANSPORT_RATE_RP_PER_KG_PER_KM
    ).round(0).astype(int)
    return df


def load_default_data():
    from battery_optimizer.io_excel import save_default_excel

    cc = get_default_collection_centers()
    rf = get_default_recycling_facilities()
    tc = get_default_transport_costs()

    if not os.path.exists(DEFAULT_DATA_PATH):
        os.makedirs(os.path.dirname(DEFAULT_DATA_PATH), exist_ok=True)
        save_default_excel(cc, rf, tc, DEFAULT_DATA_PATH)

    return cc, rf, tc
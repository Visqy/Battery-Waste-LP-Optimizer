from dataclasses import dataclass, field
from typing import List


@dataclass
class CollectionCenterSchema:
    required_columns: List[str] = field(
        default_factory=lambda: ["cc_id", "name", "province", "supply_kg"]
    )
    numeric_columns: List[str] = field(
        default_factory=lambda: ["supply_kg"]
    )
    id_column: str = "cc_id"


@dataclass
class RecyclingFacilitySchema:
    required_columns: List[str] = field(
        default_factory=lambda: [
            "rf_id", "name", "province",
            "capacity_kg", "processing_cost_rp_kg", "recovery_revenue_rp_kg",
        ]
    )
    numeric_columns: List[str] = field(
        default_factory=lambda: [
            "capacity_kg", "processing_cost_rp_kg", "recovery_revenue_rp_kg"
        ]
    )
    id_column: str = "rf_id"


@dataclass
class TransportCostSchema:
    required_columns: List[str] = field(
        default_factory=lambda: ["cc_id", "rf_id", "transport_cost_rp_kg"]
    )
    numeric_columns: List[str] = field(
        default_factory=lambda: ["transport_cost_rp_kg"]
    )
    optional_columns: List[str] = field(
        default_factory=lambda: ["distance_km"]
    )
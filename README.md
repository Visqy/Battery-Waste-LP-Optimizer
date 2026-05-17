# NMC Battery Recycling Supply Chain Optimizer

A GUI-based decision support tool for optimizing the supply chain of
Nickel-Manganese-Cobalt (NMC) electric vehicle battery recycling on
Java Island, Indonesia.

Model reference: Kasy et al. (2024), Jurnal Optimasi Sistem Industri, 23(2), 207-226.

## Software Purpose

This software implements a single-objective Linear Programming (LP) model
to minimize the total net operating cost of the NMC battery recycling
supply chain. The model is derived from the MILP framework by Kasy et al.
(2024) with the simplification y_j = 1 (all facilities assumed active).

## Installation

Requirements: Python 3.10+

Install the package and dependencies:

    pip install -e ".[test]"

Or install dependencies manually:

    pip install shiny>=0.9.0 pandas>=2.0.0 openpyxl>=3.1.0 pulp>=2.7.0 matplotlib>=3.7.0

## Run Command

    shiny run app.py --reload

Open the browser at http://127.0.0.1:8000

## Test Command

    pytest tests/

## Project Structure

    app.py                           Main Shiny application entry point
    app_modules/__init__.py
        state.py                     Shared reactive state
        page_home.py                 Home page
        page_template.py             Template download
        page_upload.py               Excel file upload
        page_editor.py               Parameter editor
        page_validation.py           Input validation
        page_optimization.py         LP optimization runner
        page_results.py              Results display and export
        page_documentation.py        Model documentation
    src/
        battery_optimizer/
            __init__.py
            config.py                Constants
            schema.py                Table schema definitions
            default_data.py          Default baseline data
            io_excel.py              Excel read/write
            validation.py            Input validation logic
            optimizer.py             PuLP LP solver
            results.py               Results processing
            report.py                Excel report export
    tests/
        test_validation.py
        test_optimizer.py
        test_excel_io.py
        test_results.py
    data/                            Auto-generated on first run
        default_parameters.xlsx
        battery_input_template.xlsx
        optimization_results.xlsx
    requirements.txt
    pyproject.toml
    README.md

## Excel Input Format

The input Excel file must contain three sheets:

Sheet: collection_centers
Columns: cc_id, name, province, supply_kg

Sheet: recycling_facilities
Columns: rf_id, name, province, capacity_kg, processing_cost_rp_kg, recovery_revenue_rp_kg

Sheet: transport_costs
Columns: cc_id, rf_id, transport_cost_rp_kg [, distance_km (optional)]
One row per (cc_id, rf_id) pair. All pairs must be present.

## Default Baseline Data

Source: Kasy et al. (2024), Period 4 (peak operating conditions)

Collection centers (8):
CC01 Jakarta, DKI Jakarta, supply = 258,480 kg/year
CC02 Bekasi, Jawa Barat, supply = 59,165 kg/year
CC03 Bandung, Jawa Barat, supply = 17,908 kg/year
CC04 Surabaya, Jawa Timur, supply = 57,737 kg/year
CC05 Tangerang, Banten, supply = 29,447 kg/year
CC06 Bogor, Jawa Barat, supply = 3,808 kg/year
CC07 Semarang, Jawa Tengah, supply = 23,652 kg/year
CC08 Yogyakarta, DI Yogyakarta, supply = 5,203 kg/year

Recycling facilities (2):
RF01 RF Jakarta, capacity = 365,000 kg/year, P = 28,360 Rp/kg, R = 238,400 Rp/kg
RF02 RF Surabaya, capacity = 365,000 kg/year, P = 28,360 Rp/kg, R = 238,400 Rp/kg

## Locked Model

The LP model formulation is locked. Users cannot modify the objective
function, constraint structure, solver, or model type.

Objective (minimize):
Z = sum\_{i,j} (C_ij + P_j - R_j) \* x_ij

Supply constraint (for each collection center i):
sum_j x_ij <= S_i

Capacity constraint (for each recycling facility j):
sum_i x_ij <= Cap_j

Non-negativity:
x_ij >= 0

Assumption: y_j = 1 for all j (all recycling facilities are active)

## Editable Parameters

Users may edit the following via the Parameter Editor tab or by uploading
a custom Excel file:

S_i : supply_kg per collection center
Cap_j : capacity_kg per recycling facility
C_ij : transport_cost_rp_kg per route
P_j : processing_cost_rp_kg per recycling facility
R_j : recovery_revenue_rp_kg per recycling facility
Names and provinces of collection centers and recycling facilities

## Outputs

The Results tab displays:

- Solver status, objective value, runtime
- Total allocated volume, unused supply, unused capacity
- Allocation matrix (CC x RF)
- Route allocation table with net cost coefficients
- Facility utilization chart
- Supply usage chart
- Constraint slack and shadow price table
- Automatic interpretation in Bahasa Indonesia

Export: Click "Export Results to Excel" to download a multi-sheet .xlsx file.

## Assumptions and Limitations

1. y_j = 1: all recycling facilities are assumed active.
2. Deterministic: no uncertainty in supply, capacity, or cost.
3. Single-period: one annual planning period.
4. Single-objective: only economic cost Z1 is optimized.
5. Environmental (Z2) and material recovery (Z3) objectives not included.
6. Facility location decisions not optimized.

## Reference

Kasy, F.I., Hisjam, M., Jauhari, W.A., & Hassan, S.A.H.S. (2024).
Optimizing the Supply Chain for Recycling Electric Vehicle NMC Batteries.
Jurnal Optimasi Sistem Industri, 23(2), 207-226.
https://doi.org/10.25077/josi.v23.n2.p207-226.2024

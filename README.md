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
    app_modules/init.py
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
            init.py
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

### Collection Centers

| ID   | Collection Center | Province      | Supply (kg/year) |
| ---- | ----------------- | ------------- | ---------------: |
| CC01 | Jakarta           | DKI Jakarta   |          258,480 |
| CC02 | Bekasi            | Jawa Barat    |           59,165 |
| CC03 | Bandung           | Jawa Barat    |           17,908 |
| CC04 | Surabaya          | Jawa Timur    |           57,737 |
| CC05 | Tangerang         | Banten        |           29,447 |
| CC06 | Bogor             | Jawa Barat    |            3,808 |
| CC07 | Semarang          | Jawa Tengah   |           23,652 |
| CC08 | Yogyakarta        | DI Yogyakarta |            5,203 |

### Recycling Facilities

| ID   | Recycling Facility | Capacity (kg/year) | Processing Cost (Rp/kg) | Recovery Revenue (Rp/kg) |
| ---- | ------------------ | -----------------: | ----------------------: | -----------------------: |
| RF01 | RF Jakarta         |            365,000 |                  28,360 |                  238,400 |
| RF02 | RF Surabaya        |            365,000 |                  28,360 |                  238,400 |

## Locked Model

The LP model formulation is locked. Users cannot modify the objective
function, constraint structure, solver, or model type.

Objective (minimize):
$Z = \sum_{i,j} (C_ij + P_j - R_j) * x_{ij}$

Supply constraint (for each collection center i):
$\sum_j x_{ij} \leq S_i$

Capacity constraint (for each recycling facility j):
$\sum_i x_{ij} \leq Cap_j$

Non-negativity:
$x_{ij} \geq$$ 0$

Assumption: $y_j = 1$ for all $j$ (all recycling facilities are active)

## Editable Parameters

Users may edit the following via the Parameter Editor tab or by uploading
a custom Excel file:

$S_i $   : supply_kg per collection center
  $Cap_j$ : capacity*kg per recycling facility
$C*{ij}$ : transport_cost_rp_kg per route
$P_j$ : processing_cost_rp_kg per recycling facility
$R_j$ : recovery_revenue_rp_kg per recycling facility
Names and provinces of collection centers and recycling facilities

## Outputs

The Results tab displays:

- Solver status, objective value, runtime
- Total allocated volume, unused supply, unused capacity
- Allocation matrix ($CC \times RF$)
- Route allocation table with net cost coefficients
- Facility utilization chart
- Supply usage chart
- Constraint slack and shadow price table
- Automatic interpretation in Bahasa Indonesia

Export: Click "Export Results to Excel" to download a multi-sheet .xlsx file.

## Assumptions and Limitations

1. $y_j = 1$: all recycling facilities are assumed active.
2. Deterministic: no uncertainty in supply, capacity, or cost.
3. Single-period: one annual planning period.
4. Single-objective: only economic cost $Z_1$ is optimized.
5. Environmental ($Z_2$) and material recovery ($Z_3$) objectives not included.
6. Facility location decisions not optimized.

## Reference

Kasy, F.I., Hisjam, M., Jauhari, W.A., & Hassan, S.A.H.S. (2024).
Optimizing the Supply Chain for Recycling Electric Vehicle NMC Batteries.
Jurnal Optimasi Sistem Industri, 23(2), 207-226.
https://doi.org/10.25077/josi.v23.n2.p207-226.2024

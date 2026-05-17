# NMC Battery Recycling Supply Chain Optimizer

A Shiny for Python decision support tool for optimizing the supply chain of Nickel-Manganese-Cobalt (NMC) electric vehicle battery recycling on Java Island, Indonesia.

The software implements a single-objective Linear Programming (LP) model for route allocation between collection centers and recycling facilities. It supports default baseline data, Excel-based input, manual parameter adjustment, validation, optimization, result visualization, and Excel export.

Model reference: Kasy et al. (2024), Jurnal Optimasi Sistem Industri, 23(2), 207-226.

## 1. Software Purpose

This software provides a reproducible graphical interface for solving an LP-based NMC battery recycling supply chain allocation problem.

The main purpose is to support:

- Input preparation through an Excel template
- Manual adjustment of supply, capacity, cost, and revenue parameters
- Input validation before optimization
- LP optimization using PuLP and CBC
- Result interpretation through tables, charts, and exportable Excel reports
- Reuse of the current configuration through an exportable input workbook

The model formulation is locked. Users can edit parameter values, but they cannot change the objective function, constraints, solver logic, or model type.

## 2. Installation

### Requirements

- Python 3.10 or newer
- pip
- A modern web browser

### Recommended installation

Create and activate a virtual environment first.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".$test$"
```

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".$test$"
```

## 3. Usage

Run the application from the project root directory:

```bash
python -m shiny run app.py --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## 4. Test Command

Run all tests:

```bash
python -m pytest
```

Expected result:

```text
All tests should pass.
```

The test suite covers:

- Default data loading
- Excel input and output
- Input validation
- LP optimization
- Result processing
- Economic interpretation

## 5. Project Structure

```text
battery-optimizer/
|-- app.py
|-- pyproject.toml
|-- README.md
|-- LICENSE
|-- CITATION.cff
|-- requirements.txt
|-- app_modules/
|   |-- __init__.py
|   |-- mathjax.py
|   |-- state.py
|   |-- page_home.py
|   |-- page_template.py
|   |-- page_upload.py
|   |-- page_editor.py
|   |-- page_validation.py
|   |-- page_optimization.py
|   |-- page_results.py
|   |-- page_documentation.py
|-- src/
|   |-- battery_optimizer/
|       |-- __init__.py
|       |-- config.py
|       |-- schema.py
|       |-- default_data.py
|       |-- io_excel.py
|       |-- validation.py
|       |-- optimizer.py
|       |-- results.py
|       |-- report.py
|-- tests/
|   |-- test_validation.py
|   |-- test_optimizer.py
|   |-- test_excel_io.py
|   |-- test_results.py
|-- data/
|   |-- default_parameters.xlsx
|-- templates/
|   |-- battery_input_template.xlsx
|-- outputs/
|   |-- optimization_results.xlsx
|   |-- current_configuration.xlsx
|-- examples/
|   |-- README.md
```

## 6. Input Format

The software accepts an Excel input workbook with the following required sheets:

```text
collection_centers
recycling_facilities
transport_costs
```

The workbook may also include optional sheets:

```text
metadata
scenario_notes
```

### Sheet: collection_centers

| Column    | Description                                     | Required |
| --------- | ----------------------------------------------- | -------- |
| cc_id     | Collection center ID                            | Yes      |
| name      | Collection center name                          | Yes      |
| province  | Province name                                   | Yes      |
| supply_kg | Annual available NMC battery waste supply in kg | Yes      |

### Sheet: recycling_facilities

| Column                 | Description                               | Required |
| ---------------------- | ----------------------------------------- | -------- |
| rf_id                  | Recycling facility ID                     | Yes      |
| name                   | Recycling facility name                   | Yes      |
| province               | Province name                             | Yes      |
| capacity_kg            | Annual facility processing capacity in kg | Yes      |
| processing_cost_rp_kg  | Processing cost in Rp per kg              | Yes      |
| recovery_revenue_rp_kg | Recovered material revenue in Rp per kg   | Yes      |

### Sheet: transport_costs

| Column               | Description                      | Required |
| -------------------- | -------------------------------- | -------- |
| cc_id                | Collection center ID             | Yes      |
| rf_id                | Recycling facility ID            | Yes      |
| transport_cost_rp_kg | Transportation cost in Rp per kg | Yes      |
| distance_km          | Route distance in km             | No       |

Every collection center and recycling facility pair must appear in the transport_costs sheet.

## 7. Default Baseline Data

Source: Kasy et al. (2024), Period 4, peak operating conditions.

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

## 8. Model Formulation

The model is a single-objective Linear Programming model.

### Sets

- $I$: set of collection centers
- $J$: set of recycling facilities

### Decision Variable

$x_{ij} \geq 0$

where $x_{ij}$ is the NMC battery waste volume allocated from collection center (i) to recycling facility (j).

### Parameters

- $S_i$: available supply at collection center $i$
- $Cap_j$: processing capacity at recycling facility $j$
- $C_{ij}$: transportation cost from collection center $i$ to recycling facility $j$
- $P_j$: processing cost at recycling facility $j$
- $R_j$: recovered material revenue at recycling facility $j$

### Objective Function

$
\min Z =
\sum_{i \in I}
\sum_{j \in J}
\left(C_{ij} + P_j - R_j\right)x_{ij}
$

### Supply Constraint

$\sum_{j \in J} x_{ij} \leq S_i,\quad \forall i \in I$

### Capacity Constraint

$\sum_{i \in I} x_{ij} \leq Cap_j,\quad \forall j \in J$

### Non-Negativity Constraint

$x_{ij} \geq 0,\quad \forall i \in I,\ j \in J$

### Facility Activation Assumption

$y_j = 1,\quad \forall j \in J$

All recycling facilities are assumed active. Facility location decisions are not optimized in this implementation.

## 9. Editable Parameters

Users may edit the following parameters through the Parameter Editor tab or by uploading a custom Excel file:

| Symbol      | Software Column        | Description                                       |
| ----------- | ---------------------- | ------------------------------------------------- |
| $S_i$     | supply_kg              | Supply per collection center                      |
| $Cap_j$   | capacity_kg            | Capacity per recycling facility                   |
| $C\_{ij}$ | transport_cost_rp_kg   | Transportation cost per route                     |
| $P_j$     | processing_cost_rp_kg  | Processing cost per recycling facility            |
| $R_j$     | recovery_revenue_rp_kg | Recovered material revenue per recycling facility |

Users may also edit collection center names, recycling facility names, and province labels.

## 10. Output Format

The Results tab displays:

- Solver status
- Economic status
- Minimum net cost objective
- Estimated net benefit or estimated net cost
- Total allocated volume
- Unused supply
- Unused capacity
- Runtime
- Allocation matrix
- Route allocation table
- Facility utilization chart
- Supply usage chart
- Constraint slack and shadow price table
- Automatic interpretation

## 11. Excel Export

The software supports two export types.

### Export Results to Excel

This workbook contains:

```text
summary
allocation_matrix
route_allocation
facility_utilization
supply_usage
constraints
interpretation
```

Currency values are exported as numeric Excel values with Rupiah formatting where applicable.

### Export Current Configuration

This workbook stores the currently active input configuration. It follows the same structure as the input template and can be uploaded again.

Expected sheets:

```text
metadata
collection_centers
recycling_facilities
transport_costs
scenario_notes
```

## 12. Example Workflow

1. Open the application.
2. Use the default baseline data or download the Excel template.
3. Upload a filled Excel input file or edit parameters in the GUI.
4. Run validation.
5. Fix all validation errors if any.
6. Run optimization.
7. Review the allocation matrix, route allocation table, utilization charts, and interpretation.
8. Export the result workbook.
9. Export the current configuration if the scenario should be reused later.

## 13. Assumptions and Limitations

1. All recycling facilities are assumed active: (y_j = 1).
2. The model is deterministic.
3. The model uses one annual planning period.
4. Costs and revenues are proportional to allocated volume.
5. Only the economic objective is optimized.
6. Environmental impact is not included.
7. Material recovery efficiency is not optimized as a separate objective.
8. Facility location decisions are not optimized.
9. Multi-period planning is not supported.
10. Stochastic supply and demand uncertainty are not modeled.

## 14. Citation

If you use this software, cite both the software and the model reference.

Software citation:

```text
Your Name. (2026). NMC Battery Recycling Supply Chain Optimizer. Version 1.0.0. MIT License.
```

Model reference:

```text
Kasy, F. I., Hisjam, M., Jauhari, W. A., & Hassan, S. A. H. S. (2024). Optimizing the Supply Chain for Recycling Electric Vehicle NMC Batteries. Jurnal Optimasi Sistem Industri, 23(2), 207-226. https://doi.org/10.25077/josi.v23.n2.p207-226.2024
```

## 15. License

This project is released under the MIT License.

# NMC Battery Recycling Allocation Optimizer

An open-source Shiny for Python application for linear-programming-based battery recycling allocation analysis in the Nickel-Manganese-Cobalt (NMC) electric vehicle battery recycling supply chain on Java Island, Indonesia.

The software implements a locked single-objective Linear Programming (LP) model. It supports Excel-based scenario input, manual parameter editing, input validation, optimization, allocation and constraint diagnostics, technical result inspection, and Excel export.

Model reference: Kasy et al. (2024), Jurnal Optimasi Sistem Industri, 23(2), 207-226.

## Intended Users

This software is designed for:

- Researchers studying reverse logistics and battery recycling optimization
- Supply-chain planners and analysts who need scenario-based allocation evidence
- Public sector planners working on electric vehicle battery waste management
- Technical users who need transparent LP-based allocation results

The software does not provide validated policy prescriptions or automatic real-world investment recommendations. It provides structured optimization evidence to support further analysis.

## Main Analysis Questions

The software helps answer:

- Can the current recycling network absorb the available NMC battery waste supply?
- What is the modeled net benefit or net cost for the scenario?
- Is there unused supply that remains unallocated?
- Is there unused processing capacity?
- Which recycling facilities reach a binding capacity constraint?
- What follow-up scenario or sensitivity analysis should be considered next?

## Installation

### Requirements

- Python 3.10 or newer
- pip
- A modern web browser

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

## Running the Application

Run the application from the project root directory:

```bash
python -m shiny run app.py --reload
```

Open the browser at:

```text
http://127.0.0.1:8000
```

## Testing

Run all tests:

```bash
python -m pytest
```

The current test suite covers:

- Default data loading
- Excel input and output
- Input validation
- LP optimization
- Result processing
- Excel report export

## Repository Structure

```text
battery-optimizer/
|-- app.py
|-- pyproject.toml
|-- requirements.txt
|-- README.md
|-- USER_GUIDE.md
|-- LICENSE
|-- CITATION.cff
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
|   |-- test_report.py
|-- data/
|   |-- battery_input_template.xlsx
|   |-- default_parameters.xlsx
|-- outputs/
|   |-- .gitkeep
|-- examples/
|   |-- README.md
|   |-- sample_input.xlsx
|   |-- sample_output.xlsx
```

## Input Format

The software accepts an Excel input workbook with the following required sheets:

```text
collection_centers
recycling_facilities
transport_costs
```

Optional sheets may include:

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

## Default Baseline Data

The default scenario follows Kasy et al. (2024), Period 4, peak operating conditions.

### Collection Centers

| ID   | Collection Center | Province      | Supply (kg/year) |
| ---- | ----------------- | ------------- | ---------------: |
| CC01 | Jakarta           | DKI Jakarta   |          258,480 |
| CC02 | Bekasi            | Jawa Barat    |           59,165 |
| CC03 | Bandung           | Jawa Barat    |           17,908 |
| CC04 | Surabaya          | Jawa Timur    |           57,737 |
| CC05 | Tangerang         | Banten        |           47,358 |
| CC06 | Bogor             | Jawa Barat    |            3,808 |
| CC07 | Semarang          | Jawa Tengah   |           23,652 |
| CC08 | Yogyakarta        | DI Yogyakarta |            5,203 |

### Recycling Facilities

| ID   | Recycling Facility | Capacity (kg/year) | Processing Cost (Rp/kg) | Recovery Revenue (Rp/kg) |
| ---- | ------------------ | -----------------: | ----------------------: | -----------------------: |
| RF01 | RF Jakarta         |            365,000 |                  28,360 |                  238,400 |
| RF02 | RF Surabaya        |            365,000 |                  28,360 |                  238,400 |

## Model Formulation

The software implements a single-objective Linear Programming model.

### Sets

- $I$: set of collection centers
- $J$: set of recycling facilities

### Decision Variable

$x_{ij} \geq 0$

where $x_{ij}$ is the NMC battery waste volume allocated from collection center (i) to recycling facility (j).

### Parameters

- $S_i$: available supply at collection center (i)
- $Cap_j$: processing capacity at recycling facility (j)
- $C_{ij}$: transportation cost from collection center (i) to recycling facility (j)
- $P_j$: processing cost at recycling facility (j)
- $R_j$: recovered material revenue at recycling facility (j)

### Objective Function

$\min Z =\sum_{i \in I}\sum_{j \in J}\left(C_{ij} + P_j - R_j\right)x_{ij}$

### Constraints

$\sum_{j \in J} x_{ij} \leq S_i,\quad \forall i \in I$

$\sum_{i \in I} x_{ij} \leq Cap_j,\quad \forall j \in J$

$x_{ij} \geq 0,\quad \forall i \in I,\ j \in J$

### Facility Activation Assumption

$y_j = 1,\quad \forall j \in J$

All recycling facilities are assumed active. Facility location decisions are not optimized in this implementation.

## Optimization Summary Outputs

The Results page displays an optimization summary before allocation and constraint tables.

Main indicators include:

- Solver status
- Objective status (modeled net benefit, net cost, or break even)
- Modeled net benefit or modeled net cost
- Supply absorption percentage
- System capacity utilization percentage
- Maximum facility utilization percentage

These indicators are computed directly from the LP solution for the scenario parameters supplied by the user.

## Technical Outputs

The software also displays:

- Solver status
- Minimum net cost objective
- Total allocated volume
- Unused supply
- Unused capacity
- Runtime
- Allocation matrix
- Route allocation table
- Facility utilization chart
- Supply usage chart
- Constraint slack and shadow price table
- Technical interpretation

## Excel Export

The software supports two export types.

### Export Results to Excel

Expected sheets:

```text
diagnostics_summary
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

Expected sheets:

```text
metadata
collection_centers
recycling_facilities
transport_costs
scenario_notes
```

The current configuration workbook can be uploaded again as a reusable scenario.

## Example Workflow

1. Open the application.
2. Use the default baseline data or download the Excel template.
3. Upload a filled Excel input file or edit parameters in the GUI.
4. Run validation.
5. Fix all validation errors if any.
6. Run optimization.
7. Review the executive decision summary.
8. Review policy insight and recommended next analysis.
9. Inspect technical tables and charts.
10. Export the result workbook.
11. Export the current configuration if the scenario should be reused later.

## Assumptions and Limitations

1. All recycling facilities are assumed active: $y_j = 1$.
2. The model is deterministic.
3. The model uses one annual planning period.
4. Costs and revenues are proportional to allocated volume.
5. Only the economic objective is optimized.
6. Environmental impact is not included.
7. Material recovery efficiency is not optimized as a separate objective.
8. Facility location decisions are not optimized.
9. Multi-period planning is not supported.
10. Stochastic supply and demand uncertainty are not modeled.
11. The software does not provide validated policy prescriptions or automatic real-world investment recommendations; results should be interpreted alongside domain expertise.

## Citation

If you use this software, cite both the software and the model reference.

Software citation:

```text
Chaerani, D., Napitupulu, H., Saputra, M. P. A., & Sabiq, M. I. (2026). NMC Battery Recycling Allocation Optimizer. Version 1.0.0. MIT License. https://github.com/Visqy/NMC-Battery-Recycling-Allocation-Optimizer
```

Model reference:

```text
Kasy, F. I., Hisjam, M., Jauhari, W. A., & Hassan, S. A. H. S. (2024). Optimizing the Supply Chain for Recycling Electric Vehicle NMC Batteries. Jurnal Optimasi Sistem Industri, 23(2), 207-226. https://doi.org/10.25077/josi.v23.n2.p207-226.2024
```

## License

This project is released under the MIT License.

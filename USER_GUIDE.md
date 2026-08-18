# User Guide

## 1. Purpose

This guide explains how to use the NMC Battery Recycling Allocation Optimizer.

The software helps users evaluate supply allocation, facility capacity, and modeled economic outcome for NMC electric vehicle battery recycling on Java Island, Indonesia.

The software does not provide validated policy prescriptions or automatic real-world investment recommendations. It provides transparent scenario-based evidence to support further analysis.

## 2. Intended Users

This guide is written for:

- Researchers
- Supply-chain planners and analysts
- Recycling infrastructure analysts
- Public sector planners
- Technical staff preparing input data
- Reviewers evaluating the software workflow

## 3. Main Workflow

The recommended workflow is:

```text
Prepare input data
Run validation
Run optimization
Review optimization summary
Review technical results
Export results
Export current configuration if needed
```

## 4. Starting the Application

Run the application from the project root directory:

```bash
python -m shiny run app.py --reload
```

Open:

```text
http://127.0.0.1:8000
```

## 5. Home Page

The Home page explains the software scope, model scope, locked model, user workflow, key outputs, and data units.

Use this page to understand what the software can and cannot answer.

The main analysis questions are:

- Can the current recycling network absorb available NMC battery waste supply?
- What is the modeled net benefit or net cost for the scenario?
- Is there unused supply?
- Is there unused facility capacity?
- Which facilities reach a binding capacity constraint?
- What follow-up scenario or sensitivity analysis should be considered next?

## 6. Template Page

Use the Template page to download the Excel input template.

The input workbook must include:

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

The template is useful when preparing a new scenario outside the GUI.

## 7. Upload Data Page

Use the Upload Data page to upload a completed Excel input file.

After upload, the application replaces the active dataset with the uploaded data.

A valid upload must contain:

- Collection center data
- Recycling facility data
- Complete transport cost routes
- Non-negative numeric values
- Matching IDs across sheets

If upload fails, check the error message and revise the Excel file.

## 8. Parameter Editor Page

Use the Parameter Editor page to edit the active scenario directly in the GUI.

Editable values include:

- Collection center name
- Collection center province
- Supply in kg/year
- Recycling facility name
- Recycling facility province
- Capacity in kg/year
- Processing cost in Rp/kg
- Recovery revenue in Rp/kg
- Route transport cost in Rp/kg

The model formulation cannot be edited. The objective function, constraints, solver logic, and model type remain locked.

After editing parameters, run validation again.

## 9. Validation Page

Use the Validation page before optimization.

Validation checks:

- Required sheets
- Required columns
- Missing values
- Duplicate IDs
- Negative values
- Complete route matrix
- Total supply
- Total capacity
- Number of routes

Optimization should not be run if validation fails.

Warnings do not block optimization, but users should review them before interpreting the result.

## 10. Optimization Page

Use the Optimization page to run the locked LP model.

The model uses PuLP and the CBC solver.

The optimization step produces:

- Solver status
- Objective value
- Runtime
- Route allocation
- Supply slack
- Capacity slack
- Shadow price when available

If the solver status is not Optimal, the model did not converge to a feasible optimum; review input data before proceeding.

## 11. Results Page

The Results page presents optimization summary metrics first, followed by allocation, capacity, and constraint detail.

### 1. Optimization Summary

This section shows:

- Solver status
- Objective status (modeled net benefit, net cost, or break even)
- Supply absorption percentage
- System capacity utilization percentage
- Modeled net benefit or modeled net cost
- Total allocated, unused supply, and unused capacity

All values are computed directly from the LP solution for the scenario parameters supplied by the user.

### Minimum Net Cost Objective

This shows the LP objective value.

A negative objective value indicates that, under the supplied scenario parameters, modeled recovered material revenue exceeds transportation and processing costs. This is the model's calculated result for the scenario parameters supplied by the user.

### 2. Allocation Results

**Allocation Matrix** shows how much NMC battery waste is allocated from each collection center to each recycling facility.

**Route Allocation Detail** shows route-level allocation and economic coefficients, including:

- Transport cost
- Processing cost
- Recovery revenue
- Net cost coefficient
- Allocated volume
- Route net benefit

### 3. Capacity Utilization

Shows the most utilized facility and its utilization percentage, plus charts for:

- Facility utilization
- Supply usage by collection center

### 4. Constraint Diagnostics and Shadow Prices

This table shows:

- Supply constraints
- Capacity constraints
- Slack values
- Shadow prices
- Binding status

A binding constraint has no slack and indicates that the constraint limits the optimal solution.

### 5. Optimization Result Interpretation and 6. Export Results

The interpretation section restates the summary metrics as plain-language text. Use the export buttons to download the result workbook or the current scenario configuration.

## 12. Interpreting Main Indicators

### Objective Status

Net Benefit (Modeled) means modeled recovered material revenue exceeds transportation and processing costs in the objective function.

Net Cost (Modeled) means transportation and processing costs exceed modeled recovered material revenue.

Break Even (Modeled) means the two are balanced.

These labels describe a property of the model solution for the scenario parameters supplied by the user.

### Supply Absorption and Capacity Utilization

Supply Absorption (%) is the share of total available supply the model allocates.

System Capacity Utilization (%) is the share of total facility capacity used by the allocation.

These are reported as percentages and totals directly from the solution; the software does not classify them into qualitative categories.

## 13. Export Results

Use Export Results to Excel to download the optimization result workbook.

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

The diagnostics_summary and summary sheets are intended for quick review.

The technical sheets are intended for detailed verification and further analysis.

## 14. Export Current Configuration

Use Export Current Configuration to download the active input scenario.

Expected sheets:

```text
metadata
collection_centers
recycling_facilities
transport_costs
scenario_notes
```

This file can be uploaded again later as a reusable scenario.

## 15. Recommended Review Order

For a quick review, use this order:

1. Read Objective Status.
2. Read Supply Absorption and System Capacity Utilization.
3. Check whether unused supply or unused capacity exists.
4. Review binding capacity constraints.
5. Export diagnostics_summary and summary for discussion.
6. Use technical tables only when detailed verification is required.

## 16. Important Limitations

1. The model is deterministic.
2. The model uses one annual planning period.
3. All recycling facilities are assumed active.
4. Facility location decisions are not optimized.
5. Environmental impact is not included.
6. Material recovery efficiency is not optimized as a separate objective.
7. Uncertainty is not modeled.
8. Objective status and net benefit/cost values are the model's calculated results for the scenario parameters supplied by the user.
9. The software does not provide validated policy prescriptions or automatic real-world investment recommendations.

## 17. Troubleshooting

### Upload fails

Check that the workbook contains all required sheets and columns.

### Validation fails

Open the Validation tab and review all error messages.

### Optimization does not run

Run validation first and fix all errors.

### Objective value is negative

This can be valid. A negative objective value indicates that, under the supplied scenario parameters, modeled recovered material revenue exceeds transportation and processing costs. This is the model's calculated result for the scenario parameters supplied by the user.

### Export file cannot be opened

Close any currently open version of the exported Excel file and export again.

## 18. Suggested Scenario Analysis

Users can test scenarios such as:

- Higher future battery waste supply
- Lower or higher recovered material revenue
- Higher transport cost
- Facility capacity expansion
- Alternative route cost assumptions
- Reduced facility capacity
- New collection center scenarios

Each scenario should be validated and exported separately.

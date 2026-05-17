import os
import pandas as pd
import tempfile
from battery_optimizer.io_excel import (
    create_excel_template,
    save_default_excel,
    read_excel_input,
    export_current_configuration,
)
from battery_optimizer.default_data import (
    get_default_collection_centers,
    get_default_recycling_facilities,
    get_default_transport_costs,
)
from battery_optimizer.config import SHEET_CC, SHEET_RF, SHEET_TC


def get_defaults():
    return (
        get_default_collection_centers(),
        get_default_recycling_facilities(),
        get_default_transport_costs(),
    )


def test_create_excel_template():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "template.xlsx")
        result_path = create_excel_template(path)

        assert os.path.exists(result_path)

        with pd.ExcelFile(result_path, engine="openpyxl") as xl:
            assert SHEET_CC in xl.sheet_names
            assert SHEET_RF in xl.sheet_names
            assert SHEET_TC in xl.sheet_names


def test_save_default_excel():
    cc, rf, tc = get_defaults()

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "default.xlsx")
        result_path = save_default_excel(cc, rf, tc, path)

        assert os.path.exists(result_path)


def test_read_excel_input_valid():
    cc, rf, tc = get_defaults()

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "input.xlsx")
        save_default_excel(cc, rf, tc, path)

        cc_out, rf_out, tc_out, errors = read_excel_input(path)

        assert len(errors) == 0
        assert cc_out is not None
        assert rf_out is not None
        assert tc_out is not None
        assert len(cc_out) == len(cc)
        assert len(rf_out) == len(rf)
        assert len(tc_out) == len(tc)


def test_read_excel_input_missing_sheet():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "bad.xlsx")
        df = pd.DataFrame({"col": [1, 2]})

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="only_sheet", index=False)

        cc_out, rf_out, tc_out, errors = read_excel_input(path)

        assert cc_out is None
        assert rf_out is None
        assert tc_out is None
        assert len(errors) > 0
        assert any("Missing" in e or "missing" in e for e in errors)


def test_read_excel_input_invalid_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "not_excel.txt")

        with open(path, "w") as f:
            f.write("not an excel file")

        cc_out, rf_out, tc_out, errors = read_excel_input(path)

        assert cc_out is None
        assert rf_out is None
        assert tc_out is None
        assert len(errors) > 0


def test_template_has_example_rows():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "template.xlsx")
        create_excel_template(path)

        with pd.ExcelFile(path, engine="openpyxl") as xl:
            cc_df = pd.read_excel(xl, sheet_name=SHEET_CC)

        assert len(cc_df) >= 1


def test_default_data_columns():
    cc, rf, tc = get_defaults()

    assert "cc_id" in cc.columns
    assert "supply_kg" in cc.columns
    assert "rf_id" in rf.columns
    assert "capacity_kg" in rf.columns
    assert "transport_cost_rp_kg" in tc.columns

def test_export_current_configuration():
    cc, rf, tc = get_defaults()

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "current_configuration.xlsx")
        result_path = export_current_configuration(cc, rf, tc, path)

        assert os.path.exists(result_path)

        with pd.ExcelFile(result_path, engine="openpyxl") as xl:
            assert "metadata" in xl.sheet_names
            assert SHEET_CC in xl.sheet_names
            assert SHEET_RF in xl.sheet_names
            assert SHEET_TC in xl.sheet_names
            assert "scenario_notes" in xl.sheet_names
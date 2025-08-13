"""
Streamlit UI for creating a new ETL config (wizard flow).
Each step is a function. Auto-detect logic is imported from ai_autodetect.py.
Config YAML output matches configs/docs standards.
"""
import streamlit as st
import pandas as pd
import yaml
import os
from pathlib import Path
from src.ui.ai_autodetect import autodetect_file_settings, autodetect_column_types

USER_CONFIGS_DIR = Path("configs/saved")
USER_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

def step_extract_settings(session_state):
    """
    Step 1: Extract Settings UI. Handles extract config fields and auto-detect.
    Returns True if step is complete.
    """
    st.header("Step 1: Extract Settings")
    show_advanced = st.checkbox("Show Advanced Extract Options", value=False)
    autodetect_file = st.text_input("File path to auto-detect settings (optional)", value="")
    autodetect_clicked = st.button("Auto-Detect Settings")
    autodetect_result = {}
    if autodetect_clicked and autodetect_file:
        try:
            autodetect_result = autodetect_file_settings(autodetect_file)
            # Set session state BEFORE widget creation, then rerun
            st.session_state["delimiter"] = autodetect_result["delimiter"]
            st.session_state["encoding"] = autodetect_result["encoding"]
            st.session_state["header"] = autodetect_result["header"]
            st.session_state["quotechar"] = autodetect_result["quotechar"]
            st.success(f"Auto-detected: Delimiter '{autodetect_result['delimiter']}', Encoding '{autodetect_result['encoding']}', Header Row {autodetect_result['header']}, Quotechar '{autodetect_result['quotechar']}'")
            st.rerun()
        except Exception as e:
            st.warning(f"Auto-detect failed: {e}")
    st.caption("Give your config a friendly name, e.g., 'Customer Master Import'.")
    config_name = st.text_input("Configuration Name")
    if "delimiter" not in st.session_state:
        st.session_state["delimiter"] = ","
    delimiter = st.text_input("Delimiter", value=st.session_state["delimiter"], key="delimiter")
    if "encoding" not in st.session_state:
        st.session_state["encoding"] = "utf-8"
    encoding = st.selectbox("Encoding", options=["utf-8", "latin1", "utf-16"], index=["utf-8", "latin1", "utf-16"].index(st.session_state["encoding"]) if st.session_state["encoding"] in ["utf-8", "latin1", "utf-16"] else 0, key="encoding")
    if "header" not in st.session_state:
        st.session_state["header"] = 0
    header = st.number_input("Header Row Index", min_value=0, value=st.session_state["header"], key="header")
    if "quotechar" not in st.session_state:
        st.session_state["quotechar"] = '"'
    quotechar = st.text_input("Quote Character", value=st.session_state["quotechar"], key="quotechar")
    if "skiprows" not in st.session_state:
        st.session_state["skiprows"] = ""
    skiprows = st.session_state["skiprows"]
    if "na_values" not in st.session_state:
        st.session_state["na_values"] = ""
    na_values = st.session_state["na_values"]
    extract_output = True
    if show_advanced:
        skiprows = st.text_input("Skip Rows (optional)", value=skiprows, key="skiprows")
        na_values = st.text_input("NA Values (optional)", value=na_values if na_values else "NA,N/A,", key="na_values")
        extract_output = st.checkbox("Write Extract Output File", value=True)
    # Save to session_state
    st.session_state["config_name"] = config_name
    # Removed all assignments to st.session_state for widget keys after widget creation
    # Step complete only if user clicks Continue
    # Step complete if config_name and delimiter are set (auto-advance)
    return bool(config_name and delimiter)

def step_file_preview(session_state):
    """
    Step 2: File Preview UI. Handles file upload and preview DataFrame.
    Returns True if preview is confirmed.
    """
    st.header("Step 2: File Preview")
    uploaded_file = st.file_uploader("Upload a file to preview data (optional, but recommended)")
    if "preview_confirmed" not in st.session_state:
        st.session_state["preview_confirmed"] = False
    preview_confirmed = st.session_state["preview_confirmed"]
    df_preview = None
    if uploaded_file is not None:
        if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != uploaded_file:
            st.session_state["preview_confirmed"] = False
            st.session_state["last_uploaded_file"] = uploaded_file
    if uploaded_file is not None and not preview_confirmed:
        import tempfile
        try:
            uploaded_file.seek(0)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp_in:
                tmp_in.write(uploaded_file.read())
                tmp_in_path = tmp_in.name
            # Build extract config for preview
            skiprows = st.session_state.get("skiprows", "")
            skiprows_val = None
            if skiprows:
                skiprows_clean = [s.strip() for s in skiprows.split(",") if s.strip()]
                if len(skiprows_clean) == 1:
                    try:
                        skiprows_val = int(skiprows_clean[0])
                    except Exception:
                        skiprows_val = skiprows_clean
                elif len(skiprows_clean) > 1:
                    try:
                        skiprows_val = [int(s) for s in skiprows_clean]
                    except Exception:
                        skiprows_val = skiprows_clean
            extract_config_dict = {
                "extract": {
                    "delimiter": st.session_state["delimiter"],
                    "encoding": st.session_state["encoding"],
                    "header": st.session_state["header"],
                    "quotechar": st.session_state["quotechar"],
                    "skiprows": skiprows_val,
                    "na_values": [v.strip() for v in st.session_state["na_values"].split(",") if v.strip()] if st.session_state["na_values"] else None,
                    "output": False,
                },
                "transform": {},
                "load": {},
            }
            with tempfile.NamedTemporaryFile(delete=False, suffix='.yaml', mode='w', encoding='utf-8') as tmp_yaml:
                yaml.dump(extract_config_dict, tmp_yaml, sort_keys=False)
                tmp_yaml_path = tmp_yaml.name
            st.info(f"Using temp YAML config: {tmp_yaml_path}")
            with open(tmp_yaml_path, "r", encoding="utf-8") as yfile:
                st.code(yfile.read(), language="yaml")
            import sys
            sys.path.insert(0, str(Path('src').resolve()))
            from extract.extract import run_extract
            df_preview = run_extract(tmp_in_path, tmp_yaml_path, return_df=True)
            st.markdown("#### Data Preview (first 10 rows):")
            st.dataframe(df_preview.head(10))
            if st.button("Preview looks correct. Continue to column type selection."):
                st.session_state["preview_confirmed"] = True
                st.session_state["df_preview"] = df_preview
                preview_confirmed = True
        except Exception as e:
            st.warning(f"Could not preview file: {e}")
        finally:
            try:
                if 'tmp_in_path' in locals() and os.path.exists(tmp_in_path):
                    os.remove(tmp_in_path)
                if 'tmp_yaml_path' in locals() and os.path.exists(tmp_yaml_path):
                    os.remove(tmp_yaml_path)
            except Exception:
                pass
    return uploaded_file is not None and st.session_state["preview_confirmed"]

def step_column_types(session_state):
    """
    Step 3: Column Types UI. Lets user review/adjust column types, with auto-detect option.
    Returns True if types are confirmed.
    """
    st.header("Step 3: Specify Column Types")
    df_preview = session_state.get("df_preview")
    if df_preview is None:
        st.warning("No preview DataFrame available. Please complete previous steps.")
        return False
    type_options = ["string", "int", "float", "bool", "date"]
    if "column_types" not in session_state:
        session_state["column_types"] = autodetect_column_types(df_preview)
    if st.button("Auto-Detect Column Types"):
        session_state["column_types"] = autodetect_column_types(df_preview)
        st.success("Auto-detected column types.")
    st.write("**Column Type Selection Table**")
    for col in df_preview.columns:
        default_type = session_state["column_types"].get(col, "string")
        selected_type = st.selectbox(
            f"Type for {col}",
            options=type_options,
            index=type_options.index(default_type) if default_type in type_options else 0,
            key=f"coltype_{col}"
        )
        session_state["column_types"][col] = selected_type
    if st.button("Confirm Column Types and Continue to Transform Settings", key="confirm_column_types_btn_step3"):
        session_state["confirmed_column_types"] = dict(session_state["column_types"])
        session_state["column_types_confirmed"] = True
    if "column_types_confirmed" not in session_state:
        session_state["column_types_confirmed"] = False
    return session_state["column_types_confirmed"]

def step_filters(session_state):
    """
    Step 4: Filter Builder UI. Lets user add filters, stored in session_state["filters"].
    Returns True if user is ready to save config.
    """
    st.header("Step 4: Add Filters")
    if "filters" not in session_state:
        session_state["filters"] = []
    confirmed_types = session_state.get('confirmed_column_types', {})
    if not confirmed_types:
        st.warning("No confirmed column types. Please complete previous steps.")
        return False
    filter_col = st.selectbox("Column to filter on", options=list(confirmed_types.keys()), key="filter_col_select")
    col_type = confirmed_types[filter_col]
    col_type_norm = str(col_type).strip().lower()
    if col_type_norm in ("int", "float"):
        op_options = ["equals", "not equal", "greater than", "less than", "greater or equal", "less or equal"]
    elif col_type_norm == "date":
        op_options = ["equals", "not equal", "after", "before", "between"]
    else:
        op_options = ["equals", "not equal", "contains", "not contains", "starts with", "ends with"]
    filter_op = st.selectbox("Operation", options=op_options, key="filter_op_select")
    def cast_filter_value(val, typ):
        if typ == "int":
            try:
                return int(val)
            except Exception:
                return val
        elif typ == "float":
            try:
                return float(val)
            except Exception:
                return val
        elif typ == "bool":
            if str(val).lower() in ("true", "1", "yes"):
                return True
            elif str(val).lower() in ("false", "0", "no"):
                return False
            else:
                return val
        else:
            return val
    with st.form("add_filter_form", clear_on_submit=True):
        if col_type_norm == "date" and filter_op == "between":
            filter_val1 = st.text_input("Start Date (YYYY-MM-DD or similar)", key="filter_val1")
            filter_val2 = st.text_input("End Date (YYYY-MM-DD or similar)", key="filter_val2")
            filter_val = (filter_val1, filter_val2)
            casted_val = (filter_val1, filter_val2)
        else:
            filter_val = st.text_input("Value", key="filter_val")
            if filter_op in ["in", "not in"]:
                vals = [v.strip() for v in filter_val.split(",") if v.strip()]
                casted_val = [cast_filter_value(v, col_type_norm) for v in vals]
            else:
                casted_val = cast_filter_value(filter_val, col_type_norm)
        add_filter = st.form_submit_button("Add Filter")
        if add_filter:
            session_state["filters"].append({
                "column": filter_col,
                "type": col_type,
                "operation": filter_op,
                "value": casted_val
            })
            st.success(f"Added filter: {filter_col} {filter_op} {casted_val}")
    if session_state["filters"]:
        st.markdown("**Current Filters:**")
        for i, f in enumerate(session_state["filters"]):
            st.write(f"{i+1}. {f['column']} ({f['type']}) {f['operation']} {f['value']}")
    # Always show confirm button, even if no filters
    confirm_filters = st.button("Confirm Filters and Continue", key="confirm_filters_btn_step4")
    if confirm_filters:
        session_state["filters_confirmed"] = True
        return True
    return False

def step_save_config(session_state):
    """
    Step 5: Save Config UI. Writes config YAML using row_filters format.
    """
    st.header("Step 5: Save Config")
    config_name = session_state.get("config_name", "")
    delimiter = session_state.get("delimiter", ",")
    encoding = session_state.get("encoding", "utf-8")
    header = session_state.get("header", 0)
    quotechar = session_state.get("quotechar", '"')
    skiprows = session_state.get("skiprows", "")
    na_values = session_state.get("na_values", "")
    extract_output = session_state.get("extract_output", True)
    column_types = session_state.get("column_types", {})
    filters_list = session_state.get("filters", [])
    transform_output = session_state.get("transform_output", False)
    # Convert skiprows to int or list of ints if needed
    skiprows_val = None
    if skiprows:
        skiprows_clean = [s.strip() for s in skiprows.split(",") if s.strip()]
        if len(skiprows_clean) == 1:
            try:
                skiprows_val = int(skiprows_clean[0])
            except Exception:
                skiprows_val = skiprows_clean
        elif len(skiprows_clean) > 1:
            try:
                skiprows_val = [int(s) for s in skiprows_clean]
            except Exception:
                skiprows_val = skiprows_clean
    # Convert filters list to row_filters dict as per docs
    row_filters = {}
    op_map = {
        "equals": "equals",
        "not equal": "not_equals",
        "greater than": "gt",
        "less than": "lt",
        "greater or equal": "ge",
        "less or equal": "le",
        "in": "in",
        "not in": "not_in",
        "contains": "contains",
        "not contains": "not_contains",
        "starts with": "startswith",
        "ends with": "endswith",
        "after": "gt",
        "before": "lt",
        "between": "between",  # Special handling below
    }
    for f in filters_list:
        op = op_map.get(f["operation"], f["operation"])
        col = f["column"]
        val = f["value"]
        if op == "between" and isinstance(val, (tuple, list)) and len(val) == 2:
            if "between" not in row_filters:
                row_filters["between"] = {}
            row_filters["between"][col] = {"start": val[0], "end": val[1]}
        else:
            if op not in row_filters:
                row_filters[op] = {}
            row_filters[op][col] = val
    config_dict = {
        "extract": {
            "delimiter": delimiter,
            "encoding": encoding,
            "header": header,
            "quotechar": quotechar,
            "skiprows": skiprows_val,
            "na_values": [v.strip() for v in na_values.split(",") if v.strip()] if na_values else None,
            "output": extract_output,
        },
        "columns": column_types if column_types else None,
        "transform": {
            "output": transform_output,
            "row_filters": row_filters if row_filters else None
        },
        "load": {"output": True},
    }
    config_path = USER_CONFIGS_DIR / f"{config_name.replace(' ', '_').lower()}.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_dict, f, sort_keys=False)
    st.success(f"Config '{config_name}' saved!")
    return True

def main():
    st.title("SimpleETL: Config Builder")
    session_state = st.session_state

    # Track which step is currently being edited
    if "current_step" not in session_state:
        session_state["current_step"] = 1

    # Step 1: Extract settings
    with st.expander("Step 1: Extract Settings", expanded=True):
        extract_complete = step_extract_settings(session_state) if session_state["current_step"] == 1 else step_extract_settings(session_state)
        if extract_complete and session_state["current_step"] == 1:
            session_state["extract_complete"] = True
            session_state["current_step"] = 2
            # Reset downstream steps
            for k in ["preview_complete", "column_types_complete", "filters_complete", "column_types_confirmed", "filters", "df_preview"]:
                if k in session_state:
                    del session_state[k]
            st.rerun()
        elif not extract_complete:
            session_state["extract_complete"] = False

    # Step 2: File preview
    with st.expander("Step 2: File Preview", expanded=session_state.get("current_step", 1) >= 2):
        preview_disabled = session_state.get("current_step", 1) != 2
        preview_complete = False
        if session_state.get("extract_complete"):
            if session_state["current_step"] == 2:
                preview_complete = step_file_preview(session_state)
                if preview_complete:
                    session_state["preview_complete"] = True
                    session_state["current_step"] = 3
                    # Reset downstream steps
                    for k in ["column_types_complete", "filters_complete", "column_types_confirmed", "filters"]:
                        if k in session_state:
                            del session_state[k]
                    st.rerun()
            else:
                # Show summary/disabled
                st.info("Preview complete. (Edit previous steps to change)")
        else:
            st.info("Complete Step 1 to enable this step.")

    # Step 3: Column types
    with st.expander("Step 3: Specify Column Types", expanded=session_state.get("current_step", 1) >= 3):
        coltypes_disabled = session_state.get("current_step", 1) != 3
        coltypes_complete = False
        if session_state.get("preview_complete"):
            if session_state["current_step"] == 3:
                coltypes_complete = step_column_types(session_state)
                if session_state.get("column_types_confirmed"):
                    session_state["column_types_complete"] = True
                    session_state["current_step"] = 4
                    # Reset downstream steps
                    for k in ["filters_complete", "filters"]:
                        if k in session_state:
                            del session_state[k]
                    # Do NOT delete confirmed_column_types here
                    st.rerun()
            else:
                st.info("Column types confirmed. (Edit previous steps to change)")
        else:
            st.info("Complete Step 2 to enable this step.")

    # Step 4: Filters (dedicated screen)
    if session_state.get("column_types_complete"):
        if session_state.get("current_step", 1) == 4:
            st.title("SimpleETL: Config Builder")
            st.header("Step 4: Add Filters")
            filters_complete = step_filters(session_state)
            if filters_complete:
                session_state["filters_complete"] = True
                session_state["current_step"] = 5
                st.rerun()
            st.stop()
        elif session_state.get("filters_complete"):
            with st.expander("Step 4: Add Filters", expanded=True):
                st.info("Filters confirmed. (Edit previous steps to change)")
                # Show summary of filters
                filters = session_state.get("filters", [])
                if filters:
                    st.markdown("**Current Filters:**")
                    for i, f in enumerate(filters):
                        st.write(f"{i+1}. {f['column']} ({f['type']}) {f['operation']} {f['value']}")
    else:
        with st.expander("Step 4: Add Filters", expanded=False):
            st.info("Complete Step 3 to enable this step.")

    # Step 5: Save config
    if session_state.get("filters_complete"):
        with st.expander("Step 5: Save Config", expanded=session_state.get("current_step", 1) == 5):
            step_save_config(session_state)

if __name__ == "__main__":
    main()

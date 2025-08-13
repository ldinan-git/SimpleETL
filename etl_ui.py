"""
Streamlit UI for running the SimpleETL pipeline and creating ETL configs.
Lets the user create a config via a guided form, save it, and select a config to run ETL.
"""

import streamlit as st
import os
import sys
import yaml
from pathlib import Path

st.title("SimpleETL: Config Builder & ETL Runner")
st.markdown("""
This UI lets you create a new ETL configuration (without editing YAML), save it, and run your ETL pipeline.
""")

USER_CONFIGS_DIR = Path("configs/saved")
USER_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

# --- Choose to create or use existing config ---
st.header("1. Choose Config Mode")
config_mode = st.radio(
    "Would you like to create a new config or use an existing one?",
    ("Create New Config", "Use Existing Config")
)

if config_mode == "Create New Config":
    st.header("2. Create a New Config")
    st.markdown("""
    **Extract Settings** control how your input file is read. For most business CSVs, the defaults are correct. Only change these if you know your file is different.
    - **Delimiter**: The character that separates columns (comma, tab, etc).
    - **Encoding**: How text is stored in the file. UTF-8 is standard for most business files.
    - **Header Row Index**: Which row contains the column names (0 = first row).
    - **Quote Character**: Used to wrap text fields that contain the delimiter.
    - **Advanced Options**: For files with special missing value codes or extra header rows.
    """)
    show_advanced = st.checkbox("Show Advanced Extract Options", value=False)
    # --- AI Assist: Auto-detect extract settings from a file ---
    st.subheader("AI Assist: Auto-Detect Extract Settings")
    autodetect_file = st.text_input("File path to auto-detect settings (optional)", value="")
    autodetect_clicked = st.button("Auto-Detect Settings")

    # Defaults
    autodetect_result = {}
    if autodetect_clicked and autodetect_file:
        autodetect_result = {"delimiter": ",", "encoding": "utf-8", "header": 0, "quotechar": '"'}
        try:
            import chardet
            # Guess encoding
            with open(autodetect_file, "rb") as f:
                raw = f.read(4096)
                enc_guess = chardet.detect(raw)
                autodetect_result["encoding"] = enc_guess["encoding"] or "utf-8"
            # Guess delimiter and quotechar
            with open(autodetect_file, "r", encoding=autodetect_result["encoding"], errors="replace") as f:
                sample = f.read(4096)
                import csv
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                autodetect_result["delimiter"] = dialect.delimiter
                autodetect_result["quotechar"] = getattr(dialect, "quotechar", '"') or '"'
                # Guess header: if first row is all strings, likely header
                lines = sample.splitlines()
                if lines:
                    first_row = next(csv.reader([lines[0]], delimiter=autodetect_result["delimiter"]))
                    autodetect_result["header"] = 0 if all(any(c.isalpha() for c in col) for col in first_row) else 1
            st.success(f"Auto-detected: Delimiter '{autodetect_result['delimiter']}', Encoding '{autodetect_result['encoding']}', Header Row {autodetect_result['header']}, Quotechar '{autodetect_result['quotechar']}'")
        except Exception as e:
            st.warning(f"Auto-detect failed: {e}")

    # Use detected or default values for the form
    import pandas as pd
    st.caption("Give your config a friendly name, e.g., 'Customer Master Import'.")
    config_name = st.text_input("Configuration Name")
    st.subheader("Extract Settings (CSV/Delimited)")
    st.caption("The character that separates columns. Default is comma. Only change if your file uses a different delimiter. E.g., use \\t for tab-delimited files.")
    if "delimiter" not in st.session_state:
        st.session_state["delimiter"] = autodetect_result.get("delimiter", ",")
    delimiter = st.text_input("Delimiter", value=st.session_state["delimiter"], key="delimiter")
    st.caption("How text is stored in the file. UTF-8 is standard for business files. Only change if you know your file uses a different encoding.")
    if "encoding" not in st.session_state:
        st.session_state["encoding"] = autodetect_result.get("encoding", "utf-8")
    encoding = st.selectbox("Encoding", options=["utf-8", "latin1", "utf-16"], index=["utf-8", "latin1", "utf-16"].index(st.session_state["encoding"]) if st.session_state["encoding"] in ["utf-8", "latin1", "utf-16"] else 0, key="encoding")
    st.caption("Row number for column headers (0 = first row). Only change if your file has extra header rows.")
    if "header" not in st.session_state:
        st.session_state["header"] = autodetect_result.get("header", 0)
    header = st.number_input("Header Row Index", min_value=0, value=st.session_state["header"], key="header")
    st.caption("Character used to quote fields. Default is '""' (double quote). Only change if your file uses a different quote character.")
    if "quotechar" not in st.session_state:
        st.session_state["quotechar"] = autodetect_result.get("quotechar", '"')
    quotechar = st.text_input("Quote Character", value=st.session_state["quotechar"], key="quotechar")
    # Always track skiprows and na_values, default to empty string if not set
    if "skiprows" not in st.session_state:
        st.session_state["skiprows"] = ""
    skiprows = st.session_state["skiprows"]
    if 'na_values' not in locals():
        na_values = ""
    if show_advanced:
        st.markdown("Advanced options are rarely needed. Only use if your file has extra header rows or special missing value codes.")
        st.caption("Rows to skip at the start of the file (comma-separated or blank). E.g., '1,2' skips the first two rows.")
        skiprows = st.text_input("Skip Rows (optional)", value=skiprows, key="skiprows")
        st.caption("Additional strings to recognize as NA/NaN (comma-separated). E.g., 'NA,N/A,-'")
        na_values = st.text_input("NA Values (optional)", value=na_values if na_values else "NA,N/A,", key="na_values")
        st.caption("Recommended: keep checked to save a copy of the extracted data. Uncheck only for advanced workflows.")
        extract_output = st.checkbox("Write Extract Output File", value=True)

    # --- File upload and preview step ---
    st.subheader("Step 2: Upload a File to Preview")
    uploaded_file = st.file_uploader("Upload a file to preview data (optional, but recommended)")
    preview_confirmed = False
    df_preview = None
    if uploaded_file is not None:
        import tempfile
        import shutil
        try:
            # Save uploaded file to a temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp_in:
                tmp_in.write(uploaded_file.read())
                tmp_in_path = tmp_in.name
            # Save extract config to a temp yaml
            import yaml
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
            extract_config_dict = {
                "extract": {
                    "delimiter": delimiter,
                    "encoding": encoding,
                    "header": header,
                    "quotechar": quotechar,
                    "skiprows": skiprows_val,
                    "na_values": [v.strip() for v in na_values.split(",") if v.strip()] if na_values else None,
                    "output": False,
                },
                "transform": {},
                "load": {},
            }
            with tempfile.NamedTemporaryFile(delete=False, suffix='.yaml', mode='w', encoding='utf-8') as tmp_yaml:
                yaml.dump(extract_config_dict, tmp_yaml, sort_keys=False)
                tmp_yaml_path = tmp_yaml.name
            # Log and show temp yaml as text
            st.info(f"Using temp YAML config: {tmp_yaml_path}")
            with open(tmp_yaml_path, "r", encoding="utf-8") as yfile:
                st.code(yfile.read(), language="yaml")
            # Call run_extract and get DataFrame
            import sys
            sys.path.insert(0, str(Path('src').resolve()))
            from extract.extract import run_extract
            df_preview = run_extract(tmp_in_path, tmp_yaml_path, return_df=True)
            st.markdown("#### Data Preview (first 10 rows):")
            st.dataframe(df_preview.head(10))
            preview_confirmed = st.checkbox("Preview looks correct. Continue to column type selection.")
        except Exception as e:
            st.warning(f"Could not preview file: {e}")
        finally:
            # Clean up temp files
            try:
                if 'tmp_in_path' in locals() and os.path.exists(tmp_in_path):
                    os.remove(tmp_in_path)
                if 'tmp_yaml_path' in locals() and os.path.exists(tmp_yaml_path):
                    os.remove(tmp_yaml_path)
            except Exception:
                pass

    # Only show the rest of the config form if preview is confirmed or no file uploaded
    if (uploaded_file is None) or preview_confirmed:
        # Step 3: Column type selection if preview is available
        column_types = {}
        if df_preview is not None:
            st.subheader("Step 3: Specify Column Types")
            st.caption("Review and adjust the type for each column. This helps with validation and filtering in later steps.")
            type_options = ["string", "int", "float", "bool", "date"]
            pandas_type_map = {
                "object": "string",
                "int64": "int",
                "float64": "float",
                "bool": "bool",
                "datetime64[ns]": "date"
            }
            for col in df_preview.columns:
                inferred = pandas_type_map.get(str(df_preview[col].dtype), "string")
                column_types[col] = st.selectbox(f"Type for '{col}'", options=type_options, index=type_options.index(inferred) if inferred in type_options else 0)
        else:
            column_types = None

        st.subheader("Transform Settings")
        st.caption("Transform settings control how your data is changed after extraction. Leave unchecked unless you want to save the intermediate result.")
        transform_output = st.checkbox("Write Transform Output File", value=False)
        st.subheader("Load Settings")
        st.caption("Load settings control the final output. Keep checked to save the final processed file.")
        load_output = st.checkbox("Write Final Output File", value=True)
        submitted_config = st.button("Save Config")
    else:
        submitted_config = False

    if submitted_config:
        if not config_name.strip():
            st.error("Please provide a configuration name.")
        else:
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
                "columns": column_types if (uploaded_file is not None and preview_confirmed and column_types) else None,
                "transform": {
                    "output": transform_output,
                },
                "load": {
                    "output": load_output,
                },
            }
            config_path = USER_CONFIGS_DIR / f"{config_name.replace(' ', '_').lower()}.yaml"
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config_dict, f, sort_keys=False)
            st.success(f"Config '{config_name}' saved!")

if config_mode == "Use Existing Config":
    st.header("2. Run ETL Pipeline with Existing Config")
    user_configs = list(USER_CONFIGS_DIR.glob("*.yaml"))
    if not user_configs:
        st.info("No configs found. Please create a config first.")
    else:
        config_choices = {c.stem.replace('_', ' ').title(): c for c in user_configs}
        selected_config_name = st.selectbox("Select a Config to Run", list(config_choices.keys()))
        selected_config_path = config_choices[selected_config_name]
        input_path = st.text_input("Input File Path", value=".\\data\\input\\customer_master.csv")
        submitted_run = st.button("Run ETL with Selected Config")

        if submitted_run:
            if not input_path:
                st.error("Please specify an input file path.")
            elif not os.path.exists(input_path):
                st.error(f"Input file not found: {input_path}")
            else:
                st.info(f"Running ETL pipeline with config '{selected_config_name}'...")
                import subprocess
                result = subprocess.run([
                    sys.executable, os.path.join("src", "main.py"), input_path, str(selected_config_path)
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("ETL pipeline completed successfully!")
                    st.text(result.stdout)
                else:
                    st.error(f"ETL failed with exit code {result.returncode}.")
                    st.text(result.stdout)
                    st.text(result.stderr)

                # Preview output file
                config_base = os.path.splitext(os.path.basename(selected_config_path))[0]
                output_path = os.path.abspath(os.path.join("data", "load", f"{config_base}_load.csv"))
                encoding = "utf-8"
                if os.path.exists(output_path):
                    st.markdown("### Output Preview (Final Load Output):")
                    import pandas as pd
                    try:
                        df_out = pd.read_csv(output_path, encoding=encoding)
                        st.dataframe(df_out)
                    except Exception as e:
                        st.warning(f"Could not display output file: {e}")
                    with open(output_path, "rb") as f:
                        st.download_button("Download Output", f, file_name=os.path.basename(output_path))

st.markdown("---")
st.markdown("*This is a simple UI. Create a config, run ETL, and preview the result. More options coming soon.*")

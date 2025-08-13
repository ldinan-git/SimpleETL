"""
Streamlit UI for running ETL with an existing config.
This UI lets the user select a config and run the ETL pipeline.
"""
import streamlit as st
import yaml
from pathlib import Path
import os

USER_CONFIGS_DIR = Path("configs/saved")
USER_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

def main():

    st.title("SimpleETL: Run ETL with Existing Config")
    st.markdown("""
    1. Select a saved ETL config YAML.
    2. Select or enter the input file to process.
    3. Click **Run ETL** to execute the pipeline.
    """)

    # 1. List available configs
    config_files = sorted([f for f in USER_CONFIGS_DIR.glob("*.yaml")])
    if not config_files:
        st.warning("No saved configs found in configs/saved/. Please create a config first.")
        return
    config_names = [f.name for f in config_files]
    selected_config_name = st.selectbox("Select Config YAML", config_names)
    selected_config_path = USER_CONFIGS_DIR / selected_config_name

    # 2. Parse config to suggest input file (if present)
    input_file_suggestion = ""
    try:
        with open(selected_config_path, "r") as f:
            config = yaml.safe_load(f)
        extract_cfg = config.get("extract", {})
        # Try to find input file in config
        input_file_suggestion = extract_cfg.get("input_file", "")
        if not input_file_suggestion:
            # Try to guess from docs or show help
            st.info("No input_file specified in config. Please select the file to process.")
    except Exception as e:
        st.error(f"Failed to parse config: {e}")
        return

    # 3. Input file selection
    input_file = st.text_input(
        "Input File to Process",
        value=input_file_suggestion,
        help="Path to the data file to process. Must match the config's expected format."
    )

    # 4. Run ETL button
    run_clicked = st.button("Run ETL Pipeline")
    if run_clicked:
        if not input_file or not os.path.exists(input_file):
            st.error(f"Input file not found: {input_file}")
            return
        st.info("Running ETL pipeline. This may take a moment...")
        import subprocess
        import sys
        try:
            # Run main.py as a subprocess for isolation
            result = subprocess.run(
                [sys.executable, "src/main.py", input_file, str(selected_config_path)],
                capture_output=True, text=True, check=False
            )
            st.code(result.stdout, language="text")
            if result.returncode == 0:
                st.success("ETL pipeline completed successfully.")
            else:
                st.error(f"ETL failed.\n{result.stderr}")
        except Exception as e:
            st.error(f"Failed to run ETL: {e}")

    st.caption("All config YAMLs must match the standards in configs/docs. For advanced troubleshooting, see the terminal output or logs.")

if __name__ == "__main__":
    main()

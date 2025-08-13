"""
Streamlit homepage for SimpleETL UI.
Lets the user choose to create a new config or run ETL with an existing config.
Routes to the appropriate UI module.
"""

import streamlit as st
import importlib
import sys
import os
# Ensure project root is in sys.path for dynamic imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def main():
    st.title("SimpleETL: Home")
    st.markdown("""
    Welcome to SimpleETL! Please choose an action:
    """)
    action = st.radio(
        "What would you like to do?",
        ["Create a New ETL Config", "Run ETL with Existing Config"],
        index=0
    )
    if action == "Create a New ETL Config":
        st.info("Launching the config builder wizard...")
        # Dynamically import and run the create UI
        etl_create = importlib.import_module("src.ui.etl_ui_create")
        etl_create.main()
    elif action == "Run ETL with Existing Config":
        st.info("Launching the ETL runner UI...")
        etl_run = importlib.import_module("src.ui.etl_ui_run")
        etl_run.main()

if __name__ == "__main__":
    main()

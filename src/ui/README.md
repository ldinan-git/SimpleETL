# SimpleETL UI Module Structure

## Overview
This folder contains the Streamlit UI logic for the SimpleETL project, split by feature for clarity and maintainability.

- `etl_ui_create.py`: UI for creating new ETL configs (wizard flow).
- `etl_ui_run.py`: UI for running ETL with existing configs.
- `ai_autodetect.py`: All auto-detect/AI/heuristic helpers for the UI.

## Extending the UI
- Each step in the wizard should be a function for clarity.
- All config YAML output must match the standards in `configs/docs`.
- Auto-detect logic should be added to `ai_autodetect.py` for reusability.

## Example Usage
- To launch the config builder: `streamlit run src/ui/etl_ui_create.py`
- To launch the ETL runner: `streamlit run src/ui/etl_ui_run.py`

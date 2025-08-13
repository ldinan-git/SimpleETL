# Main entry point for the transform step
import yaml
import pandas as pd
from .column_ops import ColumnOps
from .row_filters import RowFilters
import os

def run_transform(
    yaml_path: str,
    df: 'pd.DataFrame | None' = None,
    extracted_df_path: 'str | None' = None,
    return_df: bool = False
) -> 'pd.DataFrame | None':
    """
    Main entry point for the transform step.
    Loads YAML config, applies column and row transformations to the extracted CSV, and writes the result to the load output location.

    DataFrame loading priority:
        1. If df is provided, use it directly.
        2. Else if extracted_df_path is provided, load from that path.
        3. Else, load from the default path: data/extract/<config_base>_extract.csv (relative to project root).

    Output file: data/transform/<config_base>_transform.csv

    Args:
        yaml_path (str): Path to the YAML config file.
        df (pd.DataFrame, optional): DataFrame to transform. If provided, no file is loaded.
        extracted_df_path (str, optional): Path to extracted CSV. Used if df is not provided.
        return_df (bool): If True, return the transformed DataFrame.
    Returns:
        pd.DataFrame or None: Transformed DataFrame if return_df is True, else None.
    """
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"[Transform] YAML config file not found: {yaml_path}")
    try:
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"[Transform] Failed to read or parse YAML config: {yaml_path}\nError: {e}")
    extract_config = config.get('extract', {})
    transform_config = config.get('transform', {})
    load_config = config.get('load', {})

    # --- DataFrame loading logic ---
    def get_step_output_path(yaml_path: str, step: str) -> str:
        """
        Returns the default output path for a given ETL step and config YAML.
        Args:
            yaml_path (str): Path to the YAML config file.
            step (str): ETL step name (e.g., 'extract', 'transform', 'load').
        Returns:
            str: Absolute path to the output file for the step.
        """

    if df is not None:
        print("[Transform] Using DataFrame passed in memory.")
    else:
        if extracted_df_path is not None:
            input_file = extracted_df_path
            print(f"[Transform] Loading extracted file from provided path: {input_file}")
        else:
            # Default extracted file path from extract step
            input_file = get_step_output_path(yaml_path, 'extract')
            print(f"[Transform] Loading extracted file from default path: {input_file}")
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"[Transform] Extracted file not found: {input_file}")
        df = pd.read_csv(input_file, dtype=str)

    # Column operations
    col_ops_spec = transform_config.get('column_ops', {})
    if col_ops_spec:
        print(f"[Transform] Applying column operations...")
        df = ColumnOps(col_ops_spec).apply(df)

    # Row filters
    row_filters_spec = transform_config.get('row_filters', {})
    if row_filters_spec:
        print(f"[Transform] Applying row filters...")
        df = RowFilters(row_filters_spec).apply(df)

    # Write to transform output location only if output: true (default False)
    if transform_config.get('output', False):
        if df is not None:
            output_file = get_step_output_path(yaml_path, 'transform')
            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                print(f"[Transform] Creating transform output directory: {output_dir}")
                os.makedirs(output_dir, exist_ok=True)
            print(f"[Transform] Writing transformed data to: {output_file}")
            df.to_csv(output_file, index=False)
        else:
            print("[Transform] No DataFrame available for transform output.")
    else:
        print("[Transform] Skipping transform output file write (output: false in config). DataFrame remains in memory.")

    print(f"[Transform] Transform step complete. Final DataFrame shape: {df.shape}")
    if return_df:
        return df

if __name__ == "__main__":
    import sys
    # Optionally allow passing extracted_df_path as a second argument
    if len(sys.argv) == 2:
        run_transform(sys.argv[1])
    elif len(sys.argv) == 3:
        run_transform(sys.argv[1], extracted_df_path=sys.argv[2])
    else:
        print("Usage: python transform.py <config.yaml> [<extracted_df_path>]")
        exit(1)

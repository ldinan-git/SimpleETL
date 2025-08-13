# Main entry point for the load step
import yaml
import pandas as pd
import os
from .csv_writer import CsvWriter

def run_load(
    yaml_path: str,
    df: 'pd.DataFrame | None' = None,
    transformed_df_path: 'str | None' = None
) -> None:
    """
    Main entry point for the load step.
    Loads YAML config, reads the transformed CSV (unless df is provided), and writes the final output using CsvWriter.

    DataFrame loading priority:
        1. If df is provided, use it directly.
        2. Else if transformed_df_path is provided, load from that path.
        3. Else, load from the default path: data/transform/<config_base>_transform.csv (relative to project root).

    Output file: data/load/<config_base>_load.csv

    Args:
        yaml_path (str): Path to the YAML config file.
        df (pd.DataFrame, optional): DataFrame to load. If provided, no file is loaded.
        transformed_df_path (str, optional): Path to transformed CSV. Used if df is not provided.
    Returns:
        None
    """
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
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
        base = os.path.splitext(os.path.basename(yaml_path))[0]
        return os.path.abspath(os.path.join('data', step, f"{base}_{step}.csv"))

    if df is not None:
        print("[Load] Using DataFrame passed in memory.")
        base_name = os.path.splitext(os.path.basename(yaml_path))[0] + '_load.csv'
    else:
        if transformed_df_path is not None:
            input_file = transformed_df_path
            print(f"[Load] Loading transformed file from provided path: {input_file}")
        else:
            # Default transformed file path from transform step
            input_file = get_step_output_path(yaml_path, 'transform')
            print(f"[Load] Loading transformed file from default path: {input_file}")
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"[Load] Transformed file not found: {input_file}")
        df = pd.read_csv(input_file, dtype=str)
        base_name = os.path.splitext(os.path.basename(yaml_path))[0] + '_load.csv'

    # Write final output using CsvWriter only if output: true (default False)
    if load_config.get('output', False):
        output_file = get_step_output_path(yaml_path, 'load')
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            print(f"[Load] Creating load output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        load_config = dict(load_config)
        load_config['output'] = output_file
        print(f"[Load] Writing final output CSV via CsvWriter to: {output_file}")
        csv_writer = CsvWriter(load_config)
        csv_writer.write(df)
        print("[Load] Load step complete.")
    else:
        print("[Load] Skipping output file write (output: false in config).")

if __name__ == "__main__":
    import sys
    # Optionally allow passing transformed_df_path as a second argument
    if len(sys.argv) == 2:
        run_load(sys.argv[1])
    elif len(sys.argv) == 3:
        run_load(sys.argv[1], transformed_df_path=sys.argv[2])
    else:
        print("Usage: python load.py <config.yaml> [<transformed_df_path>]")
        exit(1)

# Main entry point for the extract step

import yaml
import os
import pandas as pd
from .delimited_loader import ExtractDelimited
from .validation_loader import ValidationLoader


def run_extract(input_file_path: str, yaml_path: str, return_df: bool = False) -> 'pd.DataFrame | None':
    """
    Main entry point for the extract step.
    Loads YAML config, runs extract (load), writes to output, then validates output file.

    Args:
        input_file_path (str): Path to the input file to use (overrides config).
        yaml_path (str): Path to the YAML config file.
        return_df (bool): If True, returns the extracted DataFrame.
    Returns:
        pd.DataFrame or None: Extracted DataFrame if return_df is True, else None.
    """
    print(f"[Extract] Starting extract step.")
    print(f"[Extract] Config file: {yaml_path}")
    print(f"[Extract] Input file path: {input_file_path}")
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    extract_config = config.get('extract', {})
    transform_config = config.get('transform', {})

    # Validate input file path (argument only, not from config)
    if not input_file_path or not os.path.exists(input_file_path):
        print(f"[Extract][ERROR] Input file not found: {input_file_path}")
        raise FileNotFoundError(f"[Extract] Input file not found: {input_file_path}. The input file path must be passed as a parameter and must exist. Please check the file path you provided.")

    print(f"[Extract] Input file found. Proceeding to extraction.")
    # Always set output_file to default if output: true
    # Output file: data/extract/<config_base>_extract.csv
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

    if extract_config.get('output', False):
        default_output_file = get_step_output_path(yaml_path, 'extract')
        extract_config['output_file'] = default_output_file
        print(f"[Extract] Output flag is True. Extracting and writing output file to: {default_output_file}")
        extractor = ExtractDelimited(input_file_path, extract_config)
        df = extractor.load()
    else:
        print("[Extract] Output flag is False. Loading data in memory only, not writing output file.")
        extractor = ExtractDelimited(input_file_path, extract_config)
        df = extractor.load(write_output=False)

    print(f"[Extract] Extraction complete. Starting validation.")
    validator = ValidationLoader(transform_config, extract_config)
    validator.validate(df)
    print(f"[Extract] Extract and validation successful for {input_file_path}")
    if return_df:
        return df


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python extract.py <input_file_path> <config.yaml>")
        exit(1)
    run_extract(sys.argv[1], sys.argv[2])

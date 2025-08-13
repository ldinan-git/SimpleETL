# Main orchestrator for the SimpleETL pipeline
import sys
import os
import yaml

def main(input_file_path: str, yaml_path: str) -> None:
    """
    Orchestrates the SimpleETL pipeline.

    Args:
        input_file_path (str): Path to the input data file to process.
        yaml_path (str): Path to the YAML configuration file.
    Returns:
        None
    """
    # Step 1: Validate input file and config file
    if not os.path.exists(input_file_path):
        print(f"[Main] ERROR: Input file not found: {input_file_path}")
        sys.exit(1)
    if not os.path.exists(yaml_path):
        print(f"[Main] ERROR: Config YAML file not found: {yaml_path}")
        sys.exit(1)

    # Step 2: Load config and inject input_file_path
    try:
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"[Main] ERROR: Failed to read or parse YAML config: {yaml_path}\nError: {e}")
        sys.exit(1)
    extract_config = config.get('extract', {})
    transform_config = config.get('transform', {})
    load_config = config.get('load', {})
    extract_config['input_file'] = input_file_path  # For legacy compatibility if needed

    # Step 3: Run ETL steps
    from extract.extract import run_extract
    from transform.transform import run_transform
    from load.load import run_load

    print("[Main] Starting extract step...")
    df_extract = run_extract(input_file_path, yaml_path, return_df=True)

    print("[Main] Starting transform step...")
    df_transform = run_transform(yaml_path, df=df_extract, return_df=True)

    print("[Main] Starting load step...")
    run_load(yaml_path, df=df_transform)

    print("[Main] ETL pipeline complete.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_file_path> <config.yaml>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])

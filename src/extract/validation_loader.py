# Handles validation of extracted DataFrames to ensure standardization
import pandas as pd

class ValidationLoader:
    """
    Validates the DataFrame output from the extract step to ensure it matches the required specification.
    This step is source-agnostic: every file, regardless of origin, must pass the same validation rules.
    The rules are defined in the YAML config (e.g., required columns, types, etc).

    Validation steps:
        1. File extension is .csv (or as specified)
        2. Delimiter is a comma (or as specified)
        3. Column names are standardized (no leading/trailing spaces, all lowercase, etc.)
        4. Required columns are present
        5. (Optional) Types and other checks

    Example YAML config:
        extract:
          input_file: ../data/input/sales_transactions.csv
          delimiter: ','
        transform:
          columns:
            - name: customer_id
              type: int
            - name: name
              type: str
            - name: email
              type: str
    """

    def __init__(self, spec: dict, extract_config: dict) -> None:
        """
        Initialize ValidationLoader with transform spec and extract config.
        Args:
            spec (dict): Transform spec from YAML (e.g., transform['columns']).
            extract_config (dict): Extract config from YAML.
        """
        """
        spec: dict from YAML, e.g., transform['columns']
        extract_config: dict from YAML, e.g., extract section
        """
        self.columns_spec = spec.get('columns', [])
        self.input_file = extract_config.get('input_file')
        self.delimiter = extract_config.get('delimiter', ',')
        self.output_file = extract_config.get('output_file')

    def validate(self, df: 'pd.DataFrame') -> None:
        """
        Validates that the DataFrame and file match the required format and columns.
        Args:
            df (pd.DataFrame): DataFrame to validate.
        Raises:
            ValueError: If validation fails.
        """
        """
        Validates that the DataFrame and file match the required format and columns.
        Raises ValueError if validation fails.
        """
        import csv
        print(f"[ValidationLoader] Starting validation for input: {self.input_file} and output: {self.output_file}")
        # 1. File extension check
        if self.input_file and not self.input_file.lower().endswith('.csv'):
            print(f"[ValidationLoader] ERROR: Input file {self.input_file} is not a .csv file.")
            raise ValueError(f"Input file {self.input_file} is not a .csv file.")
        print(f"[ValidationLoader] Input file extension is valid.")

        # 2. Output file delimiter and quoting check
        if self.output_file:
            print(f"[ValidationLoader] Checking output file delimiter and quoting...")
            with open(self.output_file, newline='', encoding='utf-8') as f:
                sample = [next(f) for _ in range(5)]  # Read first 5 lines
            # Use csv.Sniffer to detect delimiter and quoting
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(''.join(sample))
            print(f"[ValidationLoader] Detected delimiter: '{dialect.delimiter}', quotechar: '{dialect.quotechar}'")
            if dialect.delimiter != ',':
                print(f"[ValidationLoader] ERROR: Output file {self.output_file} is not comma-delimited (detected: '{dialect.delimiter}')")
                raise ValueError(f"Output file {self.output_file} is not comma-delimited (detected: '{dialect.delimiter}')")
            if not dialect.quotechar or dialect.quotechar not in ('"', "'"):
                print(f"[ValidationLoader] ERROR: Output file {self.output_file} has inconsistent or missing quoting (detected: '{dialect.quotechar}')")
                raise ValueError(f"Output file {self.output_file} has inconsistent or missing quoting (detected: '{dialect.quotechar}')")
            # Check for consistent number of columns
            with open(self.output_file, newline='', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=',', quotechar=dialect.quotechar)
                col_counts = [len(row) for row in reader]
            if len(set(col_counts)) > 1:
                print(f"[ValidationLoader] ERROR: Output file {self.output_file} has inconsistent number of columns per row: {col_counts}")
                raise ValueError(f"Output file {self.output_file} has inconsistent number of columns per row: {col_counts}")
            print(f"[ValidationLoader] Output file delimiter, quoting, and column count are valid.")

        # 3. Standardize column names: strip spaces, lower-case
        df.columns = [col.strip().lower() for col in df.columns]
        required_cols = [col['name'].strip().lower() for col in self.columns_spec]

        # 4. Check required columns
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"[ValidationLoader] ERROR: Missing required columns: {missing}")
            raise ValueError(f"Missing required columns: {missing}")
        print(f"[ValidationLoader] All required columns are present.")

        # 5. (Optional) Add more validation logic as needed
        print(f"[ValidationLoader] Validation successful for {self.output_file or self.input_file}.")
        return True

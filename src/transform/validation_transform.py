# Validates that all transform YAML operations were correctly applied to the DataFrame/output file
import pandas as pd
import yaml
import os

class ValidationTransform:
    """
    Validates that the transformed DataFrame/output file matches the transform YAML config.
    Checks column presence, order, types, and optionally sample values.
    """
    def __init__(self, yaml_path: str, transform_output_file: str) -> None:
        """
        Initialize ValidationTransform with YAML path and transform output file.
        Args:
            yaml_path (str): Path to the YAML config file.
            transform_output_file (str): Path to the transformed output CSV.
        """
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        self.transform_config = config.get('transform', {})
        self.col_ops = self.transform_config.get('column_ops', {})
        self.row_filters = self.transform_config.get('row_filters', {})
        self.transform_output_file = transform_output_file

    def validate(self) -> None:
        """
        Validates that the transformed output matches the transform YAML config.
        Raises:
            ValueError: If validation fails.
        """
        print(f"[ValidationTransform] Validating transform output: {self.transform_output_file}")
        df = pd.read_csv(self.transform_output_file, dtype=str)
        errors = []

        # 1. Check column order
        if 'order' in self.col_ops:
            expected_order = self.col_ops['order']
            if list(df.columns) != expected_order:
                errors.append(f"Column order mismatch. Expected: {expected_order}, Found: {list(df.columns)}")

        # 2. Check required columns (from order, add, rename, etc.)
        expected_cols = set()
        if 'order' in self.col_ops:
            expected_cols.update(self.col_ops['order'])
        if 'add' in self.col_ops:
            expected_cols.update(self.col_ops['add'].keys())
        if 'rename' in self.col_ops:
            expected_cols.update(self.col_ops['rename'].values())
        if expected_cols:
            missing = [col for col in expected_cols if col not in df.columns]
            if missing:
                errors.append(f"Missing expected columns: {missing}")

        # 3. Check dropped columns
        if 'drop' in self.col_ops:
            dropped = [col for col in self.col_ops['drop'] if col in df.columns]
            if dropped:
                errors.append(f"Columns not dropped as expected: {dropped}")

        # 4. Check type casting (optional, best effort)
        if 'cast' in self.col_ops:
            for col, dtype in self.col_ops['cast'].items():
                if col in df.columns:
                    try:
                        df[col].astype(dtype)
                    except Exception:
                        errors.append(f"Column {col} could not be cast to {dtype}")

        # 5. Check fillna (optional, best effort)
        if 'fillna' in self.col_ops:
            for col, val in self.col_ops['fillna'].items():
                if col in df.columns and df[col].isnull().any():
                    errors.append(f"Column {col} still contains nulls after fillna")

        # 6. Check string methods (optional, best effort)
        if 'str' in self.col_ops:
            for col, method in self.col_ops['str'].items():
                if col in df.columns:
                    sample = df[col].dropna().astype(str).head(5)
                    if method == 'lower' and not all(s == s.lower() for s in sample):
                        errors.append(f"Column {col} not all lowercase after str.lower")
                    if method == 'upper' and not all(s == s.upper() for s in sample):
                        errors.append(f"Column {col} not all uppercase after str.upper")
                    if method == 'strip' and not all(s == s.strip() for s in sample):
                        errors.append(f"Column {col} not all stripped after str.strip")

        # 7. Report results
        if errors:
            print("[ValidationTransform] Validation failed:")
            for err in errors:
                print(f"  - {err}")
            raise ValueError("Transform validation failed. See errors above.")
        else:
            print("[ValidationTransform] Transform validation successful.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python validation_transform.py <config.yaml> <transform_output_file>")
        exit(1)
    ValidationTransform(sys.argv[1], sys.argv[2]).validate()

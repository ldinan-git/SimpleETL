"""
ai_autodetect.py

Auto-detection logic for delimiter, encoding, header row, quotechar, and column types.
All AI/heuristic/ML-based helpers for the ETL UI live here.
"""
import chardet
import csv
import pandas as pd
import re

def autodetect_file_settings(filepath):
    """
    Auto-detect delimiter, encoding, header row, and quotechar for a delimited file.
    Returns a dict with keys: delimiter, encoding, header, quotechar.
    """
    result = {"delimiter": ",", "encoding": "utf-8", "header": 0, "quotechar": '"'}
    # Guess encoding
    with open(filepath, "rb") as f:
        raw = f.read(4096)
        enc_guess = chardet.detect(raw)
        result["encoding"] = enc_guess["encoding"] or "utf-8"
    # Guess delimiter and quotechar
    with open(filepath, "r", encoding=result["encoding"], errors="replace") as f:
        sample = f.read(4096)
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)
        result["delimiter"] = dialect.delimiter
        result["quotechar"] = getattr(dialect, "quotechar", '"') or '"'
        # Guess header: if first row is all strings, likely header
        lines = sample.splitlines()
        if lines:
            first_row = next(csv.reader([lines[0]], delimiter=result["delimiter"]))
            result["header"] = 0 if all(any(c.isalpha() for c in col) for col in first_row) else 1
    return result

def autodetect_column_types(df: pd.DataFrame):
    """
    Auto-detect column types for a DataFrame. Returns a dict {col: type}.
    Types: string, int, float, bool, date
    """
    def custom_detect_type(series):
        vals = series.dropna().astype(str)
        if len(vals) == 0:
            return "string"
        if vals.apply(lambda x: re.fullmatch(r"[-+]?\d+", x) is not None).all():
            return "int"
        if vals.apply(lambda x: re.fullmatch(r"[-+]?\d+([/-]\d+)+", x) is not None).all():
            return "date"
        if vals.apply(lambda x: re.fullmatch(r"[-+]?\d*\.\d+", x) is not None or re.fullmatch(r"[-+]?\d+", x) is not None).all():
            if vals.apply(lambda x: "." in x).any():
                return "float"
            else:
                return "int"
        return "string"
    return {col: custom_detect_type(df[col]) for col in df.columns}

# Delimited Loader Configuration Guide

This document describes all supported configuration options for the `ExtractDelimited` class in your ETL pipeline. Use these options in the `extract` section of your YAML config.

## Example Usage
```yaml
extract:
  input_file: ../data/input/customer_master.csv
  output_file: ../data/extract_output/customer_master.csv
  delimiter: ','
  header: 0
  encoding: 'utf-8'
  quotechar: '"'
  skiprows: null
  na_values: ['NA', 'N/A', '']
  standardize_headers: true
```

---

## Option Descriptions & Examples

### `input_file` (str, required)
Path to the input file to extract. Must be a delimited text file (e.g., CSV).

### `output_file` (str, required)
Path to write the standardized, extracted file. Will be created if it does not exist.

### `delimiter` (str, default: ',')
Field delimiter in the input file. Most CSVs use ','.
```yaml
delimiter: ','
```

### `header` (int, list of int, or 'infer', default: 'infer')
Row(s) to use as the column names. Use 0 for the first row, or 'infer' to let pandas decide.
```yaml
header: 0
```

### `encoding` (str or null, default: null)
File encoding (e.g., 'utf-8', 'latin1'). Null lets pandas auto-detect.
```yaml
encoding: 'utf-8'
```

### `quotechar` (str, default: '"')
Character used to quote fields.
```yaml
quotechar: '"'
```

### `skiprows` (int, list of int, or null, default: null)
Rows to skip at the start of the file.
```yaml
skiprows: 1
```

### `na_values` (scalar, str, list-like, or dict, default: null)
Additional strings to recognize as NA/NaN.
```yaml
na_values: ['NA', 'N/A', '']
```

### `standardize_headers` (bool, default: false)
If true, column names will be stripped and lowercased for consistency.
```yaml
standardize_headers: true
```

---

## Notes
- All columns are loaded as strings by default for maximum compatibility.
- The output file will always be a standardized, comma-delimited CSV.
- The loader will create the output directory if it does not exist.
- Use the validation step to ensure the output file is correct and ready for downstream processing.

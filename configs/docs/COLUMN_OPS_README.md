# Column Operations Configuration Guide

This document describes all supported column operations for the `transform` step in your ETL pipeline. Use these options in the `column_ops` section of your YAML config.

## Example Usage
```yaml
transform:
  column_ops:
    rename:
      old_col: new_col
    drop: [col1, col2]
    add:
      new_col: value_or_lambda
    cast:
      col: dtype
    fillna:
      col: value
    str:
      col: lower|upper|strip
    replace:
      col:
        old: new
    order: [col1, col2, ...]
    arithmetic:
      col:
        operation: add|subtract|multiply|divide
        value: number
    date:
      col: '%Y-%m-%d'
    concat:
      new_col: [col1, col2]
    split:
      col:
        sep: '-'
        new_cols: [colA, colB]
    lambda:
      col: "lambda row: ..."
```

---

## Operation Descriptions & Examples

### `rename`
Rename columns. Key is old name, value is new name.
```yaml
rename:
  signup_date: registration_date
```

### `drop`
Drop columns by name. List of column names.
```yaml
drop: [email, temp_col]
```

### `add`
Add new columns. Value can be a constant or a lambda (as a string).
```yaml
add:
  is_north: "lambda row: row['region'] == 'North'"
  constant_col: 1
```

### `cast`
Change column data type. Key is column, value is dtype (int, float, str, etc).
```yaml
cast:
  customer_id: int
```

### `fillna`
Fill missing values. Key is column, value is fill value.
```yaml
fillna:
  status: 'unknown'
```

### `str`
Apply string methods. Key is column, value is method (lower, upper, strip).
```yaml
str:
  name: lower
```

### `replace`
Replace values in a column. Key is column, value is mapping of old:new.
```yaml
replace:
  status:
    inactive: 'INACTIVE'
```

### `order`
Reorder columns. List of column names in desired order.
```yaml
order: [customer_id, name, registration_date, status, region, is_north]
```

### `arithmetic`
Apply arithmetic to a column. Key is column, value is dict with 'operation' and 'value'.
```yaml
arithmetic:
  amount:
    operation: add
    value: 10
```

### `date`
Parse column as date with given format.
```yaml
date:
  registration_date: '%Y-%m-%d'
```

### `concat`
Concatenate columns into a new column. Key is new column, value is list of columns.
```yaml
concat:
  full_name: [first_name, last_name]
```

### `split`
Split a column into multiple columns. Key is column, value is dict with 'sep' and 'new_cols'.
```yaml
split:
  full_name:
    sep: ' '
    new_cols: [first_name, last_name]
```

### `lambda`
Apply a custom lambda to a column. Key is column, value is a string lambda.
```yaml
lambda:
  is_even: "lambda row: int(row['customer_id']) % 2 == 0"
```

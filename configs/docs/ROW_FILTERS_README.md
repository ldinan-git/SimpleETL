# Row Filters Configuration Guide

This document describes all supported row filtering operations for the `transform` step in your ETL pipeline. Use these options in the `row_filters` section of your YAML config.

## Example Usage
```yaml
transform:
  row_filters:
    equals:
      status: 'active'
    not_equals:
      region: 'West'
    in:
      region: ['North', 'South']
    contains:
      name: 'user'
    gt:
      customer_id: 1020
    lambda:
      custom_filter: "lambda row: int(row['customer_id']) % 2 == 0"
```

---

## Operation Descriptions & Examples

### `equals`
Filter rows where column equals a value.
```yaml
equals:
  status: 'active'
```

### `not_equals`
Filter rows where column does not equal a value.
```yaml
not_equals:
  region: 'West'
```

### `gt`, `lt`, `ge`, `le`
Filter rows where column is greater than, less than, greater or equal, or less or equal to a value.
```yaml
gt:
  customer_id: 1020
lt:
  customer_id: 2000
```

### `in`
Filter rows where column value is in a list.
```yaml
in:
  region: ['North', 'South']
```

### `not_in`
Filter rows where column value is not in a list.
```yaml
not_in:
  status: ['inactive', 'unknown']
```

### `isnull`
Filter rows where column is null.
```yaml
isnull:
  - email
```

### `notnull`
Filter rows where column is not null.
```yaml
notnull:
  - name
```

### `contains`
Filter rows where column contains a substring.
```yaml
contains:
  name: 'user'
```

### `startswith`, `endswith`
Filter rows where column starts or ends with a substring.
```yaml
startswith:
  name: 'A'
endswith:
  name: 'Smith'
```

### `lambda`
Apply a custom lambda function to each row. Key is a name, value is a string lambda.
```yaml
lambda:
  custom_filter: "lambda row: int(row['customer_id']) % 2 == 0"
```

---

You can combine multiple filters for complex logic. All filters are ANDed together by default. For OR/compound logic, use a custom lambda.

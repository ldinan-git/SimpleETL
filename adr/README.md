# SimpleETL Architecture & Design Rationale

## Overview
SimpleETL is a modular, YAML-driven ETL (Extract, Transform, Load) framework designed for accessibility, reproducibility, and robustness. The goal is to empower non-technical users to automate and standardize data workflows, especially for Excel/CSV-based business processes.

---

## ETL Step Responsibilities

### Extract
- **Purpose:** Ingest data from various sources (CSV, eventually JSON/XML/etc.), standardize structure, and output a clean, comma-delimited CSV.
- **Responsibilities:**
  - Load raw data using robust pandas settings.
  - Standardize headers (strip, lowercase, etc.).
  - Save output to a known location (`data/extract_output/`).
  - Validate output: must be a valid CSV, comma-delimited, consistent quoting, correct columns, and schema as defined in YAML.
- **Output Requirement:**
  - File must be a valid, comma-delimited CSV with standardized column names and all required columns present.

### Transform
- **Purpose:** Apply user-defined column and row operations to the extracted data, enabling flexible business logic without code.
- **Responsibilities:**
  - Apply column operations (rename, drop, add, cast, fillna, string ops, replace, arithmetic, date, concat, split, lambda, reorder).
  - Apply row filters (equals, not_equals, gt, lt, in, not_in, isnull, notnull, contains, startswith, endswith, lambda).
  - Save output to a known location (`data/transform_output/`).
  - (Optional) Validate output: should maintain the same schema as extract output, unless explicitly changed by user.
- **Output Requirement:**
  - File must remain a valid, comma-delimited CSV. By default, column structure should match extract output unless user changes it.

### Load
- **Purpose:** Join, append, or otherwise combine multiple transformed files and load to the final destination (e.g., reporting, database, S3, etc.).
- **Responsibilities:**
  - Join/merge files as specified in YAML.
  - Output to the final target location.
  - (Optional) Validate output: ensure final file meets business or technical requirements.
- **Output Requirement:**
  - File must be a valid, comma-delimited CSV (or other target format as specified).

---

## Validation at Each Step
- **Extract:** Always required. Ensures all downstream steps receive clean, standardized data.
- **Transform:** Recommended, especially if column structure is changed. If only filtering rows, validation is optional but can catch accidental column drops or type changes.
- **Load:** Optional, but useful for ensuring final output meets all requirements.

---

## Design Principles
- **Separation of Concerns:** Each step has a clear, limited responsibility.
- **Reproducibility:** All logic is YAML-driven and versionable.
- **Accessibility:** Designed for non-technical users, with future plans for a UI.
- **Extensibility:** Easy to add new sources, transforms, or outputs.
- **Validation:** Early and often, to catch issues before they propagate.

---

## FAQ
**Q: Should validation run after transform?**
A: Yes, especially if the transform step can change columns or types. If transform only filters rows, validation is optional but still useful for catching accidental changes or ensuring schema consistency.

**Q: What if a file is missing columns after transform?**
A: Validation will catch this and raise an error, preventing bad data from moving downstream.

**Q: Can users add custom logic?**
A: Yes, via lambdas in YAML or by extending the codebase.

---

For more details, see the documentation in the `configs/docs` directory.

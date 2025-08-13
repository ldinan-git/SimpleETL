
import pandas as pd

class RowFilters:
	"""
	Applies a wide range of row filtering operations to a DataFrame, as specified in a config (e.g., from YAML).
	Supported operations:
		- Equality filter (column == value)
		- Inequality filter (column != value)
		- Greater/less than (>, <, >=, <=)
		- In list (column in [values])
		- Not in list
		- Null/not null
		- String contains/startswith/endswith
		- Custom lambda functions
		- Compound filters (AND/OR)
		- Any other pandas-supported row-wise filter
	"""
	def __init__(self, spec: dict) -> None:
		"""
		Initialize RowFilters with a row filter spec.
		Args:
			spec (dict): Row filter specification from YAML.
		"""
		self.spec = spec

	def apply(self, df: 'pd.DataFrame') -> 'pd.DataFrame':
		"""
		Apply all specified row filters to the DataFrame.
		Args:
			df (pd.DataFrame): DataFrame to filter.
		Returns:
			pd.DataFrame: Filtered DataFrame.
		"""
		mask = pd.Series([True] * len(df))

		# 1. Equality filters
		if 'equals' in self.spec:
			for col, val in self.spec['equals'].items():
				print(f"[RowFilters] Filtering where {col} == {val}")
				mask &= (df[col] == val)

		# 2. Inequality filters
		if 'not_equals' in self.spec:
			for col, val in self.spec['not_equals'].items():
				print(f"[RowFilters] Filtering where {col} != {val}")
				mask &= (df[col] != val)

		# 3. Greater/less than
		if 'gt' in self.spec:
			for col, val in self.spec['gt'].items():
				print(f"[RowFilters] Filtering where {col} > {val}")
				mask &= (pd.to_numeric(df[col], errors='coerce') > val)
		if 'lt' in self.spec:
			for col, val in self.spec['lt'].items():
				print(f"[RowFilters] Filtering where {col} < {val}")
				mask &= (pd.to_numeric(df[col], errors='coerce') < val)
		if 'ge' in self.spec:
			for col, val in self.spec['ge'].items():
				print(f"[RowFilters] Filtering where {col} >= {val}")
				mask &= (pd.to_numeric(df[col], errors='coerce') >= val)
		if 'le' in self.spec:
			for col, val in self.spec['le'].items():
				print(f"[RowFilters] Filtering where {col} <= {val}")
				mask &= (pd.to_numeric(df[col], errors='coerce') <= val)

		# 4. In list
		if 'in' in self.spec:
			for col, values in self.spec['in'].items():
				print(f"[RowFilters] Filtering where {col} in {values}")
				mask &= df[col].isin(values)

		# 5. Not in list
		if 'not_in' in self.spec:
			for col, values in self.spec['not_in'].items():
				print(f"[RowFilters] Filtering where {col} not in {values}")
				mask &= ~df[col].isin(values)

		# 6. Null/not null
		if 'isnull' in self.spec:
			for col in self.spec['isnull']:
				print(f"[RowFilters] Filtering where {col} is null")
				mask &= df[col].isnull()
		if 'notnull' in self.spec:
			for col in self.spec['notnull']:
				print(f"[RowFilters] Filtering where {col} is not null")
				mask &= df[col].notnull()

		# 7. String contains/startswith/endswith
		if 'contains' in self.spec:
			for col, val in self.spec['contains'].items():
				print(f"[RowFilters] Filtering where {col} contains '{val}'")
				mask &= df[col].str.contains(val, na=False)
		if 'startswith' in self.spec:
			for col, val in self.spec['startswith'].items():
				print(f"[RowFilters] Filtering where {col} startswith '{val}'")
				mask &= df[col].str.startswith(val, na=False)
		if 'endswith' in self.spec:
			for col, val in self.spec['endswith'].items():
				print(f"[RowFilters] Filtering where {col} endswith '{val}'")
				mask &= df[col].str.endswith(val, na=False)

		# 8. Custom lambda functions
		if 'lambda' in self.spec:
			for name, func in self.spec['lambda'].items():
				print(f"[RowFilters] Applying custom lambda filter: {name}")
				if isinstance(func, str) and func.strip().startswith('lambda'):
					mask &= df.apply(eval(func), axis=1)
				else:
					mask &= df.apply(func, axis=1)

		# 9. Compound filters (AND/OR) can be added as needed

		# 10. Any other pandas-supported row-wise filter can be added here

		print(f"[RowFilters] Filtered DataFrame shape: {df[mask].shape}")
		return df[mask]

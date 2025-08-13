
import pandas as pd

class ColumnOps:
	"""
	Applies a wide range of column operations to a DataFrame, as specified in a config (e.g., from YAML).
	Supported operations:
		- Rename columns
		- Change column order
		- Drop columns
		- Add new columns (with default or computed values)
		- Type casting
		- Fill missing values
		- Apply string methods (lower, upper, strip, etc.)
		- Map/replace values
		- Arithmetic operations (add, subtract, multiply, divide)
		- Date parsing and formatting
		- Concatenate columns
		- Split columns
		- Reorder columns
		- Custom lambda functions
		- Any other pandas-supported column-wise operation
	"""
	def __init__(self, spec: dict) -> None:
		"""
		Initialize ColumnOps with a column operation spec.
		Args:
			spec (dict): Column operation specification from YAML.
		"""
		self.spec = spec

	def apply(self, df: 'pd.DataFrame') -> 'pd.DataFrame':
		"""
		Apply all specified column operations to the DataFrame.
		Args:
			df (pd.DataFrame): DataFrame to transform.
		Returns:
			pd.DataFrame: Transformed DataFrame.
		"""
		# 1. Always map columns first (rename, drop, cast, fillna, string ops, replace, arithmetic, date, concat, split, lambda)
		if 'rename' in self.spec:
			print(f"[ColumnOps] Renaming columns: {self.spec['rename']}")
			df = df.rename(columns=self.spec['rename'])
		if 'drop' in self.spec:
			print(f"[ColumnOps] Dropping columns: {self.spec['drop']}")
			df = df.drop(columns=self.spec['drop'], errors='ignore')
		if 'cast' in self.spec:
			for col, dtype in self.spec['cast'].items():
				print(f"[ColumnOps] Casting column {col} to {dtype}")
				df[col] = df[col].astype(dtype, errors='ignore')
		if 'fillna' in self.spec:
			print(f"[ColumnOps] Filling missing values: {self.spec['fillna']}")
			df = df.fillna(self.spec['fillna'])
		if 'str' in self.spec:
			for col, method in self.spec['str'].items():
				print(f"[ColumnOps] Applying string method '{method}' to column {col}")
				if method == 'lower':
					df[col] = df[col].str.lower()
				elif method == 'upper':
					df[col] = df[col].str.upper()
				elif method == 'strip':
					df[col] = df[col].str.strip()
		if 'replace' in self.spec:
			for col, mapping in self.spec['replace'].items():
				print(f"[ColumnOps] Replacing values in column {col}: {mapping}")
				df[col] = df[col].replace(mapping)
		if 'arithmetic' in self.spec:
			for col, op in self.spec['arithmetic'].items():
				print(f"[ColumnOps] Applying arithmetic operation to column {col}: {op}")
				if op['operation'] == 'add':
					df[col] = df[col].astype(float) + op['value']
				elif op['operation'] == 'subtract':
					df[col] = df[col].astype(float) - op['value']
				elif op['operation'] == 'multiply':
					df[col] = df[col].astype(float) * op['value']
				elif op['operation'] == 'divide':
					df[col] = df[col].astype(float) / op['value']
		if 'date' in self.spec:
			for col, fmt in self.spec['date'].items():
				print(f"[ColumnOps] Parsing dates in column {col} with format {fmt}")
				df[col] = pd.to_datetime(df[col], format=fmt, errors='coerce')
		if 'concat' in self.spec:
			for new_col, cols in self.spec['concat'].items():
				print(f"[ColumnOps] Concatenating columns {cols} into {new_col}")
				df[new_col] = df[cols].astype(str).agg(''.join, axis=1)
		if 'split' in self.spec:
			for col, params in self.spec['split'].items():
				print(f"[ColumnOps] Splitting column {col} by '{params['sep']}' into {params['new_cols']}")
				splits = df[col].str.split(params['sep'], expand=True)
				for i, new_col in enumerate(params['new_cols']):
					df[new_col] = splits[i]
		if 'lambda' in self.spec:
			for col, func in self.spec['lambda'].items():
				print(f"[ColumnOps] Applying custom lambda to column {col}")
				df[col] = df.apply(func, axis=1)

		# 2. Add new columns (after mapping)
		if 'add' in self.spec:
			for col, val in self.spec['add'].items():
				print(f"[ColumnOps] Adding column: {col} (default/computed value)")
				if callable(val):
					df[col] = df.apply(val, axis=1)
				elif isinstance(val, str) and val.strip().startswith('lambda'):
					# Evaluate lambda string safely
					df[col] = df.apply(eval(val), axis=1)
				else:
					df[col] = val

		# 3. Change column order (after all columns exist)
		if 'order' in self.spec:
			print(f"[ColumnOps] Reordering columns: {self.spec['order']}")
			df = df[self.spec['order']]

		# 4. Any other pandas-supported column-wise operation can be added here

		return df

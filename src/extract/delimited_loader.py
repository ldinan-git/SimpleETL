# Handles loading and standardizing delimited input files
import pandas as pd

class ExtractDelimited:
	"""
	Extracts data from a delimited file (default: CSV) using robust pandas settings.
	All options are set via a config dict (e.g., from YAML). If a config value is missing, a default is used.

	Config options:
		input_file (str): Path to the input file. (Required)
		output_file (str): Path to write the extracted file. (Required)
		delimiter (str): Field delimiter. Default is ','.
		header (int, list of int, or 'infer'): Row(s) to use as the column names. Default is 'infer'.
		encoding (str or None): File encoding (e.g., 'utf-8', 'latin1'). Default is None (pandas auto-detects).
		quotechar (str): Character used to quote fields. Default is '"'.
		skiprows (int, list of int, or None): Rows to skip at the start of the file. Default is None.
		na_values (scalar, str, list-like, or dict, optional): Additional strings to recognize as NA/NaN. Default is None.

	Defaults:
		- All columns loaded as strings (object dtype)
		- Delimiter is a comma (',')
		- No special quoting, encoding, or NA handling unless specified
		- Designed for business-user-friendly, Excel-adjacent files

	Example YAML config:
		extract:
		  input_file: ../data/input/sales_transactions.csv
		  output_file: ../data/extract_output/sales_transactions.csv
		  delimiter: ','
		  header: 0
		  encoding: 'utf-8'
		  quotechar: '"'
		  skiprows: null
		  na_values: ['NA', 'N/A', '']
	"""
	def __init__(self, filepath: str, config: dict) -> None:
		"""
		Initialize ExtractDelimited with file path and config.
		Args:
			filepath (str): Path to the input file.
			config (dict): Extract config dictionary.
		"""
		# Always use filepath argument, not config
		self.filepath = filepath
		self.output_file = config.get('output_file')
		self.delimiter = config.get('delimiter', ',')
		self.header = config.get('header', 'infer')
		self.encoding = config.get('encoding', None)
		self.quotechar = config.get('quotechar', '"')
		self.skiprows = config.get('skiprows', None)
		self.na_values = config.get('na_values', None)

	def load(self, write_output: bool = True) -> 'pd.DataFrame':
		"""
		Loads the delimited file into a pandas DataFrame with robust defaults, then writes it to the output_file as CSV if write_output is True.
		Args:
			write_output (bool): If True, writes the DataFrame to output_file.
		Returns:
			pd.DataFrame: DataFrame with all columns as strings.
		"""
		"""
		Loads the delimited file into a pandas DataFrame with robust defaults, then writes it to the output_file as CSV if write_output is True.
		Returns:
			pd.DataFrame: DataFrame with all columns as strings.
		"""
		print(f"[ExtractDelimited] Starting extraction from: {self.filepath}")
		print(f"[ExtractDelimited] Loading file: {self.filepath} (delimiter='{self.delimiter}')")
		df = pd.read_csv(
			self.filepath,
			delimiter=self.delimiter,
			dtype=str,  # All columns as strings by default
			header=self.header,
			encoding=self.encoding,
			quotechar=self.quotechar,
			skiprows=self.skiprows,
			na_values=self.na_values,
			engine='python',  # More robust for odd delimiters/quoting
		)
		print(f"[ExtractDelimited] Loaded DataFrame with shape: {df.shape}")
		if self.output_file and write_output:
			import os
			output_dir = os.path.dirname(self.output_file)
			if output_dir and not os.path.exists(output_dir):
				print(f"[ExtractDelimited] Creating output directory: {output_dir}")
				os.makedirs(output_dir, exist_ok=True)
			print(f"[ExtractDelimited] Writing standardized CSV to: {self.output_file}")
			df.to_csv(self.output_file, index=False)
		return df

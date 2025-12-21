from pathlib import Path
import pandas as pd

# -------- user input --------
input_path = Path(input("Enter CSV file or folder path: ").strip().strip('"'))

# -------- config --------
DATETIME_COL = "DateTime"
CUTOFF_STR = "2025.01.01 00:00:00"
DATETIME_FMT = "%Y.%m.%d %H:%M:%S"

# -------- validation --------
if not input_path.exists():
    raise FileNotFoundError(f"Path does not exist: {input_path}")

# Determine input files
if input_path.is_file():
    csv_files = [input_path]
    base_dir = input_path.parent
elif input_path.is_dir():
    csv_files = sorted(input_path.glob("*.csv"))
    base_dir = input_path
else:
    raise ValueError("Input must be a CSV file or a folder")

if not csv_files:
    raise FileNotFoundError("No CSV files found.")

# Output folder
output_dir = base_dir / "cleaneddata"
output_dir.mkdir(exist_ok=True)

cutoff_dt = pd.to_datetime(CUTOFF_STR, format=DATETIME_FMT)

# -------- processing --------
for file in csv_files:
    df = pd.read_csv(
        file,
        sep=None,              # auto-detect delimiter (tabs / commas)
        engine="python"
    )

    if DATETIME_COL not in df.columns:
        raise KeyError(f"{file.name}: missing '{DATETIME_COL}' column")

    # Parse datetime safely
    df[DATETIME_COL] = pd.to_datetime(
        df[DATETIME_COL],
        format=DATETIME_FMT,
        errors="coerce"
    )

    # Drop malformed rows
    df = df.dropna(subset=[DATETIME_COL])

    # Filter for 2025+
    df = df[df[DATETIME_COL] >= cutoff_dt]

    # Write output
    out_file = output_dir / file.name
    df.to_csv(out_file, index=False)

    print(f"{file.name}: {len(df):,} rows saved")

print(f"\nCleaned files written to:\n{output_dir.resolve()}")

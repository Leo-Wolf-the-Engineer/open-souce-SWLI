import os
import pandas as pd
import glob

def extract_distance_data():
    """
    Extracts the column "  Distance1 (µm)" from all CSV files in the folder
    and saves them in a file called data.csv.
    """
    # Find all CSV files in the current directory, except data.csv
    csv_files = [f for f in glob.glob("*.csv") if f != "data.csv"]

    if not csv_files:
        print("No CSV files found.")
        return

    print(f"{len(csv_files)} CSV files found.")

    # Initialize result DataFrame
    result_df = pd.DataFrame()

    # Read existing data.csv, if available
    if os.path.exists("data.csv"):
        try:
            result_df = pd.read_csv("data.csv", sep=',', decimal='.', encoding="windows-1252")
            print(f"Existing data.csv loaded with {len(result_df.columns)} columns.")
        except Exception as e:
            print(f"Error loading existing data.csv: {e}")
            result_df = pd.DataFrame()

    # Iterate over all CSV files and extract the distance column
    for file in csv_files:
        try:
            print(f"Processing {file}...")
            # Read file
            df = pd.read_csv(file, sep=',', decimal='.', encoding="windows-1252")

            # Check if the target column exists
            if " Distance1 (µm)" in df.columns:
                # If the filename already exists as a column, skip it
                if file not in result_df.columns:
                    # Add column to the result with filename as header
                    result_df[file] = df[" Distance1 (µm)"].reset_index(drop=True)
                    print(f"  Successfully extracted {len(df)} values.")
                else:
                    print(f"  Column '{file}' already exists in data.csv. Skipping.")
            else:
                print(f"  Column '  Distance1 (µm)' not found in {file}.")
        except Exception as e:
            print(f"  Error processing {file}: {e}")

    # Save the result
    if not result_df.empty:
        result_df.to_csv("data.csv", sep=',', decimal='.', index=False)
        print(f"Data saved in data.csv. Total of {len(result_df.columns)} columns.")
    else:
        print("No data extracted.")

if __name__ == "__main__":
    extract_distance_data()
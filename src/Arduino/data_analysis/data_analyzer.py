import pandas as pd
import numpy as np
import time
import os
import argparse

def analyze_measurement_data(csv_file, std_dev_threshold, window_size_ms, wait_time_ms, averaging_duration_ms):
    df = pd.read_csv(csv_file)
    df['time_ms'] = pd.to_numeric(df['time_ms'], errors='coerce')
    df['measurement'] = pd.to_numeric(df['measurement'], errors='coerce')
    df = df.dropna()

    stagnant_windows = []
    if df.empty:
        return stagnant_windows
    window_size_samples = int(window_size_ms / (df['time_ms'].diff().median())) if len(df['time_ms']) > 1 else 10 # Estimate samples per window, default to 10 if time_ms has only one value
    if window_size_samples < 1:
        window_size_samples = 1

    for i in range(len(df) - window_size_samples + 1):
        window = df['measurement'].iloc[i:i + window_size_samples]
        if window.std() < std_dev_threshold:
            start_time = df['time_ms'].iloc[i]
            end_time = df['time_ms'].iloc[i + window_size_samples - 1]
            stagnant_windows.append({'start_time': start_time, 'end_time': end_time})

    averaged_windows = []
    for window in stagnant_windows:
        wait_time_sec = wait_time_ms / 1000.0
        avg_duration_sec = averaging_duration_ms / 1000.0
        
        start_index = df[df['time_ms'] >= window['end_time']].index.min()
        if pd.isna(start_index):
            continue # No data after stagnant window end time

        wait_end_time = window['end_time'] + wait_time_ms
        avg_start_time = wait_end_time
        avg_end_time = avg_start_time + averaging_duration_ms

        avg_start_index = df[df['time_ms'] >= avg_start_time].index.min()
        avg_end_index = df[df['time_ms'] <= avg_end_time].index.max()

        if pd.isna(avg_start_index) or pd.isna(avg_end_index):
            continue

        measurement_window = df['measurement'].iloc[avg_start_index:avg_end_index+1]
        if not measurement_window.empty:
            average_measurement = measurement_window.mean()
        else:
            average_measurement = np.nan

        averaged_windows.append({
            'start_time': window['start_time'],
            'end_time': window['end_time'],
            'average_measurement': average_measurement
        })

    return averaged_windows

def main():
    parser = argparse.ArgumentParser(description="Analyze time-series measurement data for stagnant windows.")
    parser.add_argument("csv_file", help="Path to the CSV file containing measurement data.")
    parser.add_argument("--std_dev_threshold", type=float, default=0.1, help="Standard deviation threshold for negligible movement (default: 0.1).")
    parser.add_argument("--window_size_ms", type=int, default=1000, help="Sliding window size in milliseconds (default: 1000ms).")
    parser.add_argument("--wait_time_ms", type=int, default=50, help="Wait time after stagnant window in milliseconds (default: 50ms).")
    parser.add_argument("--averaging_duration_ms", type=int, default=200, help="Averaging duration after wait time in milliseconds (default: 200ms).")

    args = parser.parse_args()

    try:
        stagnant_windows_avg = analyze_measurement_data(
            args.csv_file,
            args.std_dev_threshold,
            args.window_size_ms,
            args.wait_time_ms,
            args.averaging_duration_ms
        )

        if stagnant_windows_avg:
            print("Detected stagnant windows with average measurements:")
            for window in stagnant_windows_avg:
                print(f"  Start Time: {window['start_time']}ms, End Time: {window['end_time']}ms, Average Measurement: {window['average_measurement']:.4f}")
        else:
            print("No stagnant windows detected.")

    except FileNotFoundError:
        print(f"Error: CSV file not found at '{args.csv_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
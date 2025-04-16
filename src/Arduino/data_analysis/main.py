import pandas as pd
import plotly.express as px
from data_analyzer import analyze_measurement_data

# Configuration parameters
std_dev_threshold = 2
window_size_ms = 10
wait_time_ms = 300
averaging_duration_ms = 300

def main():
    """
    Main function to load data, analyze measurements and create plots.
    """
    try:
        # Load data from data.csv
        df = pd.read_csv("data.csv", sep=',', decimal='.', encoding="windows-1252")
        print(f"Data successfully loaded. Available columns: {df.columns.tolist()}")

        # Select first column for plotting
        first_column = df.columns[0]

        # Create a proper copy of the data to work with
        analysis_df = pd.DataFrame()
        analysis_df['measurement'] = df[first_column].astype(float)

        # Analyze measurement data
        averaged_windows = analyze_measurement_data(analysis_df,
                                                    std_dev_threshold,
                                                    window_size_ms,
                                                    wait_time_ms,
                                                    averaging_duration_ms)

        print(f"Found {len(averaged_windows)} stagnant windows.")

        # Create plot with Plotly
        fig = px.line(analysis_df, y='measurement', title="Measurement Values")
        fig.update_layout(
            xaxis_title="Index",
            yaxis_title="Value",
            template="plotly_white"
        )

        # Add highlighted areas for stagnation windows
        for window in averaged_windows:
            fig.add_vrect(
                x0=window['start_time'],
                x1=window['end_time'],
                fillcolor="red",
                opacity=0.2,
                line_width=0,
                annotation_text="Stagnation",
                annotation_position="top left"
            )

        # Display the plot
        fig.show()

        print(f"Plot for column '{first_column}' has been created.")
    except Exception as e:
        print(f"Error loading or displaying data: {e}")

if __name__ == "__main__":
    main()
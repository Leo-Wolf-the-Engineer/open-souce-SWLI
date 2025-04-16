import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from extraction import extract_and_plot_window_averages
from linearity import plot_linearity_comparison

def plot_selected_windows(df, column_name, t_offset, t_window_size, t_movement, n_movements, sampling_rate=520.8333333):
    """
    Plots a single column with multiple highlighted windows for each movement.
    """
    # Create time values for this specific column
    time_values = np.arange(len(df[column_name])) / sampling_rate

    fig = go.Figure()

    # Plot the main data
    fig.add_trace(go.Scatter(
        x=time_values,
        y=df[column_name],
        mode='lines',
        name=column_name
    ))

    # Calculate total cycle time (window + movement)
    cycle_time = t_window_size + t_movement

    # Add shaded regions for each movement window
    for i in range(n_movements):
        start_time = t_offset + i * cycle_time
        end_time = start_time + t_window_size

        # Highlight the window
        fig.add_shape(
            type="rect",
            x0=start_time,
            x1=end_time,
            y0=df[column_name].min(),
            y1=df[column_name].max(),
            fillcolor="rgba(0, 255, 0, 0.2)",  # Transparent green
            line=dict(width=0),
            layer="below"
        )

    # Update layout
    fig.update_layout(
        title=f"Selected Windows for {column_name}",
        xaxis_title="Time (s)",
        yaxis_title="Measurement",
        showlegend=True,
        height=600,
        width=1000
    )

    # Show the plot
    fig.show()

def plot_all_windows(df, columns, t_offsets, t_window_sizes, t_movements, n_movements_list, sampling_rate=520.8333333):
    """
    Plots all columns with their highlighted windows in a grid.
    """
    # Calculate grid dimensions
    n_cols = min(3, len(columns))
    n_rows = (len(columns) + n_cols - 1) // n_cols

    fig = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=columns)

    for i, (column, offset, window_size, movement, n_movements) in enumerate(
            zip(columns, t_offsets, t_window_sizes, t_movements, n_movements_list)):
        if column not in df.columns:
            continue

        # Create time values for this specific column
        time_values = np.arange(len(df[column])) / sampling_rate

        # Calculate grid position
        row = i // n_cols + 1
        col = i % n_cols + 1

        # Plot the main data
        fig.add_trace(
            go.Scatter(
                x=time_values,
                y=df[column],
                mode='lines',
                name=column
            ),
            row=row, col=col
        )

        # Calculate total cycle time (window + movement)
        cycle_time = window_size + movement

        # Add shaded regions for each movement window
        for j in range(n_movements):
            start_time = offset + j * cycle_time
            end_time = start_time + window_size

            # Add shape to the corresponding subplot
            fig.add_shape(
                type="rect",
                x0=start_time,
                x1=end_time,
                y0=df[column].min(),
                y1=df[column].max(),
                fillcolor="rgba(0, 255, 0, 0.2)",
                line=dict(width=0),
                row=row, col=col
            )

    fig.update_layout(height=450*n_rows, width=1400, title_text="Selected Windows Visualization")
    fig.show()

def main():
    """
    Main function to load data, analyze measurements and create plots.
    The data is chopped up to extract standstill data
    """
    try:
        # Load data from data.csv
        df = pd.read_csv("data.csv", sep=',', decimal='.', encoding="windows-1252")
        print(f"Data successfully loaded. Available columns: {df.columns.tolist()}")
    except FileNotFoundError:
        print("Error: data.csv file not found.")
        return

    # Define column names, offsets, window sizes, move times
    columns = [
        #'0.45mm_10steps_500ms_1.csv',
        '0.45mm_10steps_500ms_2.csv',
        '0.45mm_40steps_300ms_1.csv',
        #'0.45mm_40steps_300ms_2.csv',
        '0.45mm_80steps_300ms.csv',
        '0.45mm_480steps_300ms.csv',
        'single_step_40_300ms_1.csv',
        #'single_step_40_300ms_2.csv',
        #'triple_step_40_300ms_1.csv',
        #'triple_step_40_300ms_2.csv',
        'triple_step_40_300ms_3.csv'
    ]

    pitch = 0.5
    steps_per_rotation = 200
    microstepping = 64
    steps_per_um = steps_per_rotation * microstepping / pitch / 1000
    nm_per_step = 1 / steps_per_um * 1000
    print (f"nm_per_step: {nm_per_step}")

    distance = 0.45
    # Convert distance to steps
    distance_steps = int(distance * steps_per_um)*1000

    sampling_rate = 520.8333333


    t_offsets = [2.12, 2.53, 0.92, 0.08, 1.94, 0.78]
    t_window_sizes = [0.45, 0.2475, 0.239, 0.24, 0.1775, 0.2185]
    t_movement = [0.285, 0.111, 0.09, 0.065, 0.123, 0.082]
    n_movements = [11, 41, 55, 60, 40, 40]
    n_steps = [distance_steps/10, -distance_steps/40, -distance_steps/80, -distance_steps/480, -1, 3]
    print(f"amount of steps: {n_steps}")
    nm_per_movement = [n_steps * nm_per_step for n_steps in n_steps]
    print(f"nm_per_movement: {nm_per_movement}")

    # Plot all columns with their windows
    plot_all_windows(df, columns, t_offsets, t_window_sizes, t_movement, n_movements)

    # Extract and plot window averages using time on the x-axis
    window_averages = extract_and_plot_window_averages(
        df, columns, t_offsets, t_window_sizes, t_movement, n_movements,
        nm_per_movement, x_axis_type="time"
    )

    # Plot each measurement with linearity line
    linearity_figures = plot_linearity_comparison(window_averages, nm_per_movement, columns)

if __name__ == "__main__":
    main()
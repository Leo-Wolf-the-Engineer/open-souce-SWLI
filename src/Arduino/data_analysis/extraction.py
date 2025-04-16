import numpy as np
import pandas as pd
import plotly.graph_objects as go

def extract_and_plot_window_averages(df, columns, t_offsets, t_window_sizes, t_movements,
                                    n_movements_list, nm_per_movement_list=None,
                                    sampling_rate=520.8333333, x_axis_type="time"):
    """
    Extracts the average values from each defined window and plots them.

    Parameters:
        df (pd.DataFrame): The data frame containing measurement columns
        columns (list): List of column names to process
        t_offsets (list): List of initial time offsets for each column
        t_window_sizes (list): List of window sizes for each column
        t_movements (list): List of movement times for each column
        n_movements_list (list): List of number of movements for each column
        nm_per_movement_list (list, optional): List of nm per movement for each column
        sampling_rate (float): Sampling rate in Hz
        x_axis_type (str): "time", "distance", or "index" for x-axis display

    Returns:
        dict: Dictionary containing average values for each column
    """
    # Dictionary to store results
    results = {}

    # Create figure
    fig = go.Figure()

    for i, (column, offset, window_size, movement, n_movements) in enumerate(
            zip(columns, t_offsets, t_window_sizes, t_movements, n_movements_list)):
        if column not in df.columns:
            continue

        # Calculate time values for this column
        time_values = np.arange(len(df[column])) / sampling_rate

        # List to store averages and window times
        averages = []
        window_times = []

        # Calculate total cycle time
        cycle_time = window_size + movement

        for j in range(n_movements):
            # Calculate window boundaries
            start_time = offset + j * cycle_time
            end_time = start_time + window_size
            window_center = start_time + window_size / 2
            window_times.append(window_center)

            # Get indices of data points inside this window
            window_indices = np.where((time_values >= start_time) & (time_values < end_time))[0]

            # Extract values in this window
            if len(window_indices) > 0:
                window_values = df[column].iloc[window_indices]
                average = window_values.mean()
                averages.append(average)
            else:
                averages.append(np.nan)

        # remove average
        averages = averages - np.mean(averages)

        # Store results
        results[column] = averages

        # Determine x-axis values based on selected type
        if x_axis_type == "time":
            x_values = window_times
            x_axis_title = "Time (s)"
        elif x_axis_type == "distance" and nm_per_movement_list is not None:
            x_values = [j * nm_per_movement_list[i] for j in range(len(averages))]
            x_axis_title = "Distance (nm)"
        else:
            x_values = list(range(1, len(averages) + 1))
            x_axis_title = "Window Index"

        # Add trace for this column
        fig.add_trace(go.Scatter(
            x=x_values,
            y=averages,
            mode='lines+markers',
            name=column
        ))

    # Update layout
    fig.update_layout(
        title="Average Values for Each Window",
        xaxis_title=x_axis_title,
        yaxis_title="Average Value",
        showlegend=True,
        height=600,
        width=1000
    )

    fig.show()

    return results
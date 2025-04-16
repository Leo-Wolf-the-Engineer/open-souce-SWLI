import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_linearity_comparison(results, nm_per_movement_list, columns):
    """
    Creates plots for each measurement with an ideal linearity line in a single window.

    Parameters:
        results (dict): Dictionary containing average values for each column
        nm_per_movement_list (list): List of nm per movement for each column
        columns (list): List of column names to process

    Returns:
        go.Figure: The figure object containing all subplots
    """
    # Calculate grid dimensions
    n_cols = min(2, len(columns))
    n_rows = (len(columns) + n_cols - 1) // n_cols

    # Create subplot titles - use shortened column names
    subplot_titles = [col.split('_')[0] + '...' for col in columns if col in results]

    # Create figure with subplots
    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=subplot_titles,
        vertical_spacing=0.12
    )

    for i, column in enumerate(columns):
        if column not in results:
            continue

        averages = results[column]

        # Calculate subplot position
        row = (i // n_cols) + 1
        col = (i % n_cols) + 1

        # Create x-axis values in µm
        x_values = [j * nm_per_movement_list[i]/1000 for j in range(len(averages))]

        #subtract slope from y values
        averages = averages - x_values
        averages = averages - np.mean(averages)

        # Add measurement data
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=averages,
                mode='markers',
                name=f'{column} (Data)',
                marker=dict(size=6),
                showlegend=True
            ),
            row=row, col=col
        )

        # Calculate linear fit if we have enough points
        if len(x_values) > 1:
            # Filter out any NaN values
            valid_indices = ~np.isnan(averages)
            valid_x = np.array(x_values)[valid_indices]
            valid_y = np.array(averages)[valid_indices]

            if len(valid_x) > 1:
                # Calculate linear regression
                slope, intercept = np.polyfit(valid_x, valid_y, 1)

                # Generate line points
                line_x = [min(x_values), max(x_values)]
                line_y = [slope * x + intercept for x in line_x]

                # Add ideal linearity line
                fig.add_trace(
                    go.Scatter(
                        x=line_x,
                        y=line_y,
                        mode='lines',
                        name=f'{column} (Fit: {slope:.4f})',
                        line=dict(color='red', width=2, dash='dash')
                    ),
                    row=row, col=col
                )

        # Update axes labels
        fig.update_xaxes(title_text="Distance (µm)", row=row, col=col)
        fig.update_yaxes(title_text="Average Value", row=row, col=col)

    # Update layout
    fig.update_layout(
        title="Linearity Analysis for All Measurements",
        height=280*n_rows,
        width=1450,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )

    # Additional title formatting
    #for i in fig['layout']['annotations']:
     #   i['font'] = dict(size=10)  # Smaller font size for titles
     #   i['text'] = '<b>' + i['text'] + '</b>'  # Make titles bold

    fig.show()
    return fig
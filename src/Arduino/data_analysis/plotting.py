import numpy as np


def debug_plot(df, title="Debug Plot"):
    """
    Debug plotting function that creates a figure with two subplots:
    - Top subplot: position vs time
    - Bottom subplot: velocity vs time

    Args:
        df: DataFrame with 'time', 'position', 'velocity' columns
        title: Title for the figure
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Create figure with two subplots
    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=('Position', 'Velocity'))

    # Add position trace on top subplot
    fig.add_trace(
        go.Scatter(x=df["time"], y=df["position"], mode='lines', name='Position'),
        row=1, col=1
    )

    # Add velocity trace on bottom subplot
    fig.add_trace(
        go.Scatter(x=df["time"], y=df["velocity"], mode='lines', name='Velocity', line=dict(color='red')),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        title=title,
        height=800,
        width=1000,
        showlegend=True,
    )

    # Add grid to both subplots
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')

    # Update axis labels
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="Position", row=1, col=1)
    fig.update_yaxes(title_text="Velocity", row=2, col=1)

    # Show the plot
    fig.show()


def debug_plot_with_peaks(df_processed, peaks_df, stillstands_df=None, title="Debug Plot with Peaks"):
    """
    Debug-Plotting-Funktion, die ein Diagramm mit drei Unterplots erstellt und
    die erkannten Peaks markiert:
    - Oberer Unterplot: Position über Zeit mit markierten Peaks
    - Mittlerer Unterplot: Geschwindigkeit über Zeit mit markierten Peaks
    - Unterer Unterplot: Absolute Geschwindigkeit mit Schwellenwerten für Peak-Detektion

    Args:
        df_processed: DataFrame mit 'time', 'position', 'velocity' Spalten
        peaks_df: DataFrame mit 'time', 'position', 'velocity' Spalten der erkannten Peaks
        stillstands_df: DataFrame mit Stillstandsinformationen
        title: Titel für das Diagramm
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Diagramm mit drei Unterplots erstellen
    fig = make_subplots(rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=('Position', 'Velocity', 'Absolute Velocity & Thresholds'))

    # Position Daten zum oberen Unterplot hinzufügen
    fig.add_trace(
        go.Scatter(x=df_processed["time"], y=df_processed["position"],
                   mode='lines', name='Position'),
        row=1, col=1
    )

    # Peaks auf dem Positions-Plot markieren
    fig.add_trace(
        go.Scatter(x=peaks_df["time"], y=peaks_df["position"],
                   mode='markers', name='Position Peaks',
                   marker=dict(color='red', size=10, symbol='circle')),
        row=1, col=1
    )

    # Geschwindigkeit Daten zum mittleren Unterplot hinzufügen
    fig.add_trace(
        go.Scatter(x=df_processed["time"], y=df_processed["velocity"],
                   mode='lines', name='Velocity', line=dict(color='green')),
        row=2, col=1
    )

    # Peaks auf dem Geschwindigkeits-Plot markieren
    fig.add_trace(
        go.Scatter(x=peaks_df["time"], y=peaks_df["velocity"],
                   mode='markers', name='Velocity Peaks',
                   marker=dict(color='red', size=10, symbol='circle')),
        row=2, col=1
    )

    # --- Neuer dritter Unterplot: Absolute Geschwindigkeit mit Schwellenwerten ---
    # Absolute Geschwindigkeit berechnen
    abs_velocity = np.abs(df_processed["velocity"])

    # Zugriff auf SignalProcessor für Schwellenwerte
    # Falls diese Funktion außerhalb des Kontexts eines Tests aufgerufen wird,
    # verwenden wir Standardwerte
    try:
        # Schwellenwerte aus dem SignalProcessor extrahieren
        from signal_processor import SignalProcessor
        processor = SignalProcessor()
        v_th = processor.v_th
        min_peak_height = v_th * 2
        min_peak_prominence = v_th * 3
    except:
        # Fallback-Werte
        v_th = abs_velocity.max() * 0.1
        min_peak_height = v_th * 2
        min_peak_prominence = v_th * 3

    abs_velocity = (-np.abs(np.abs(df_processed["velocity"].tolist()) - (v_th * 8))).flatten()

    # Absolute Geschwindigkeit zum unteren Unterplot hinzufügen
    fig.add_trace(
        go.Scatter(x=df_processed["time"], y=abs_velocity,
                   mode='lines', name='|Velocity|', line=dict(color='purple')),
        row=3, col=1
    )

    # Peaks auf dem abs_velocity-Plot markieren
    if not peaks_df.empty:
        abs_peak_velocity = np.abs(peaks_df["velocity"])
        fig.add_trace(
            go.Scatter(x=peaks_df["time"], y=abs_peak_velocity,
                       mode='markers', name='Abs Velocity Peaks',
                       marker=dict(color='red', size=10, symbol='circle')),
            row=3, col=1
        )

    # Schwellenwert-Linien hinzufügen
    fig.add_trace(
        go.Scatter(x=[df_processed["time"].min(), df_processed["time"].max()],
                   y=[min_peak_height, min_peak_height],
                   mode='lines', name='Min Peak Height',
                   line=dict(color='orange', dash='dash')),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(x=[df_processed["time"].min(), df_processed["time"].max()],
                   y=[min_peak_prominence, min_peak_prominence],
                   mode='lines', name='Min Peak Prominence',
                   line=dict(color='red', dash='dot')),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(x=[df_processed["time"].min(), df_processed["time"].max()],
                   y=[v_th, v_th],
                   mode='lines', name='Velocity Threshold',
                   line=dict(color='green', dash='dash')),
        row=3, col=1
    )

    # Stillstands-Zeitpunkte markieren, wenn stillstands_df vorhanden ist
    if stillstands_df is not None and not stillstands_df.empty:
        # CalibrationStartTime und CalibrationStopTime als vertikale Linien darstellen
        for i, row in stillstands_df.iterrows():
            # Start-Zeit als vertikale Linie in allen Plots
            for row_idx in range(1, 4):  # Für jeden der drei Unterplots
                # Kalibrier-Startzeit
                fig.add_vline(
                    x=row["still_time_start"],
                    line=dict(color="blue", width=1, dash="dash"),
                    row=row_idx, col=1
                )
                # Kalibrier-Endzeit
                fig.add_vline(
                    x=row["still_time_end"],
                    line=dict(color="red", width=1, dash="dash"),
                    row=row_idx, col=1
                )

            # Labels für den ersten Stillstand hinzufügen (nur einmal, um Legende nicht zu überfüllen)
            if i == 0:
                # Dummy-Traces für die Legende
                fig.add_trace(
                    go.Scatter(x=[None], y=[None], mode='lines',
                               name='Calibration Start Time',
                               line=dict(color="blue", width=1, dash="dash")),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=[None], y=[None], mode='lines',
                               name='Calibration End Time',
                               line=dict(color="red", width=1, dash="dash")),
                    row=1, col=1
                )

    # Layout aktualisieren
    fig.update_layout(
        title=title,
        height=1000,  # Höhe erhöht wegen des zusätzlichen Plots
        width=1000,
        showlegend=True,
    )

    # Gitter zu allen Unterplots hinzufügen
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')

    # Achsenbeschriftungen aktualisieren
    fig.update_xaxes(title_text="Time", row=3, col=1)
    fig.update_yaxes(title_text="Position", row=1, col=1)
    fig.update_yaxes(title_text="Velocity", row=2, col=1)
    fig.update_yaxes(title_text="Absolute Velocity", row=3, col=1)

    # Diagramm anzeigen
    fig.show()

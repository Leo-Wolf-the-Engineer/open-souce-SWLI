import pandas as pd
from signal_processor import SignalProcessor
from plotting import debug_plot_with_peaks

# Configuration parameters
#std_dev_threshold = 2
#window_size_ms = 10
#wait_time_ms = 300
#averaging_duration_ms = 300

def main():
    """
    Main function to load data, analyze measurements and create plots.
    """
    try:
        # Load data from data.csv
        df = pd.read_csv("data.csv", sep=',', decimal='.', encoding="windows-1252")
        print(f"Data successfully loaded. Available columns: {df.columns.tolist()}")

        # Select column for plotting
        # 1 '0.45mm_10steps_500ms_1.csv'
        # 2 '0.45mm_10steps_500ms_2.csv'
        # 3 '0.45mm_40steps_300ms_1.csv'
        # 4 '0.45mm_40steps_300ms_2.csv'
        # 5 '0.45mm_480steps_300ms.csv'
        # 6 '0.45mm_80steps_300ms.csv'
        # 7 'single_step_40_300ms_1.csv'
        # 8 'single_step_40_300ms_2.csv'
        # 9 'triple_step_40_300ms_1.csv'
        # 10 'triple_step_40_300ms_2.csv'
        # 11 'triple_step_40_300ms_3.csv'
        analysis_df = pd.DataFrame()
        analysis_df['measurement'] = df[df.columns[5]].astype(float)

        # Process the measurement data
        processor = SignalProcessor(15, 0.05, 0.05)
        df_processed, peaks_df, stillstands_df = processor.process_signal(analysis_df['measurement'].tolist())

        # Debugging: Plot processed data with peaks and stillstand markers
        debug_plot_with_peaks(df_processed=df_processed,
                                   peaks_df=peaks_df,
                                   stillstands_df=stillstands_df,
                                   title="Processed Data with Peaks and Stillstands")


        print(f"Plot for column '{first_column}' has been created.")
    except Exception as e:
        print(f"Error loading or displaying data: {e}")

if __name__ == "__main__":
    main()
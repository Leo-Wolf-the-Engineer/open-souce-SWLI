import pandas as pd
import numpy as np
import time
import logging
from typing import List, Dict, Tuple, Any
from plotting import debug_plot

from scipy.ndimage import median_filter
from scipy.signal import decimate, find_peaks

# Updated import path
#from src.utils.config_reader import ConfigReader

logger = logging.getLogger(__name__)


class SignalProcessor:
    """Processes raw time-series data to extract key features like stillstand periods."""

    def __init__(self, v_th, T_start, T_stop):


        # Parameters from DataPreprocessor - Let errors propagate
        self.downsample_factor = int(1) # Let ValueError occur if not int
            
        self.sampling_rate = 520.83333333 # Assuming 520.83333333 samples per second
             
        # Add type check before comparison
        is_numeric_sampling_rate = isinstance(self.sampling_rate, (int, float))
        self.time_interval = 1 / self.sampling_rate if is_numeric_sampling_rate and self.sampling_rate > 0 else 0

        self.measurement_is_rotational = False # Default to linear

        # calculate v_th based on calibration window peak_to_peak*0.777 and sampling_rate
        self.v_th = v_th
        self.T_start = T_start
        self.T_stop = T_stop
        print(f"debugging: v_th: {self.v_th}, T_start: {self.T_start}, T_stop: {self.T_stop}, dt: {self.time_interval}")
        
        self.dt = 0 # Will be calculated during processing

    def process_signal(self, raw_data: List[float]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Main method to process raw signal data.

        Args:
            raw_data: List of floats representing the raw time series data.

        Returns:
            Tuple containing:
            - Processed timeseries DataFrame (with time, position, velocity).
            - Peaks DataFrame.
            - Stillstands DataFrame.
        """
        if not raw_data:
            logger.error("Received empty raw_data list.")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # --- Step 1: Convert to DataFrame and Initial Preprocessing ---
        try:
            # Handle raw_data as a list of float values
            if isinstance(raw_data, list):
                if all(isinstance(x, (int, float)) for x in raw_data):
                    # Simple list of numbers - create DataFrame with position column
                    df = pd.DataFrame({'position': raw_data})
                else:
                    # List of dictionaries or other structures
                    df = pd.DataFrame(raw_data)
            else:
                # Already a DataFrame or similar structure
                df = pd.DataFrame(raw_data)

            # Ensure 'position_raw' exists, potentially copying from 'position'
            if 'position_raw' not in df.columns and 'position' in df.columns:
                df['position_raw'] = df['position'].copy()
            elif 'position_raw' not in df.columns:
                raise KeyError("Raw data must contain at least a 'position' or 'position_raw' column.")
            # Ensure 'position' column exists for processing if only 'position_raw' is present
            if 'position' not in df.columns:
                df['position'] = df['position_raw'].copy()

            logger.info(f"Initial DataFrame shape: {df.shape}")

        except Exception as e:
            logger.error(f"Failed to convert raw_data to DataFrame or initial checks failed: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # --- Step 2: Preprocessing (from DataPreprocessor) --- 
        df_processed, self.dt = self._preprocess_dataframe(df)
        if df_processed.empty:
             logger.error("Preprocessing returned an empty DataFrame.")
             return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        logger.info(f"DataFrame shape after preprocessing: {df_processed.shape}")

        # --- Step 3: Peak and Stillstand Detection (from PeakDetector) ---
        peaks_df, stillstands_df = self._find_peaks_and_stillstands(df_processed)
        logger.info(f"Found {len(peaks_df)} peaks and {len(stillstands_df)} stillstands.")

        return df_processed, peaks_df, stillstands_df

    # --- Methods adapted from DataPreprocessor --- 

    def _preprocess_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """Applies preprocessing steps like downsampling, unwrapping, time calculation, velocity."""
        if len(df) <= 7: # Need enough points for filtering/diff
            logger.warning("DataFrame too short for full preprocessing.")
            # Basic time and velocity if possible
            if 'time' not in df.columns:
                 df['time'] = np.arange(len(df)) * self.time_interval
            if 'velocity' not in df.columns:
                 df['velocity'] = 0.0
            return df, self.time_interval 

        df = df.copy()
        effective_downsample_factor = self.downsample_factor

        # Downsample data if needed
        if effective_downsample_factor > 1:
            df = self._downsample_data(df, effective_downsample_factor)
            logger.debug(f"DataFrame shape after downsampling: {df.shape}")

        # Remove data errors/jumps (simple diff check)
        # Consider more robust outlier detection if needed
        diff_threshold = 5
        unwrap_threshold = 355 # For rotational wrap-around
        position_diff = df["position_raw"].diff().abs()
        valid_indices = (position_diff <= diff_threshold) | (position_diff >= unwrap_threshold) | position_diff.isna()
        df = df[valid_indices].reset_index(drop=True)
        logger.debug(f"DataFrame shape after jump removal: {df.shape}")

        # Process position based on measurement type
        if self.measurement_is_rotational:
            self._process_rotational_data(df)

        # Add/update time column
        dt_effective = self.time_interval * effective_downsample_factor
        df["time"] = np.arange(len(df)) * dt_effective
        # Ensure essential columns exist
        df = df[["time", "position_raw", "position"]]
        
        # Calculate time difference (should be consistent after preprocessing)
        calculated_dt = df["time"].diff().fillna(dt_effective).mean()

        # Calculate and filter velocity
        if len(df) > 1:
            df = self._calculate_velocity(df, calculated_dt)
            logger.debug(f"DataFrame shape after velocity calculation: {df.shape}")
            # calculate rms Velocity and apply to v_th
            rms_velocity = np.sqrt(np.mean(df['velocity']**2))
            self.v_th = rms_velocity * 0.2
            print(f"debugging: v_th: {self.v_th}, T_start: {self.T_start}, T_stop: {self.T_stop}, dt: {self.dt}")
        else:
             df['velocity'] = 0.0 # Assign zero velocity if only one point remains

        if df.empty:
             logger.warning("Preprocessing resulted in an empty DataFrame.")

        return df, calculated_dt

    def _downsample_data(self, df, downsample_factor):
        start_time = time.perf_counter()
        try:
            # Extract position data for decimation
            data = df["position"].to_numpy()
            # Apply scipy's decimate function
            data_decimated = decimate(data, downsample_factor, ftype="fir", zero_phase=True)

            # Downsample the dataframe indices
            indices = np.arange(len(df))
            indices_decimated = decimate(indices, downsample_factor, ftype='fir', zero_phase=True).astype(int)
            indices_decimated = np.clip(indices_decimated, 0, len(df) - 1) # Ensure indices are valid
            
            df_downsampled = df.iloc[indices_decimated].reset_index(drop=True)

            # Ensure lengths match
            min_len = min(len(data_decimated), len(df_downsampled))
            df_final = df_downsampled.iloc[:min_len].copy()
            df_final["position"] = data_decimated[:min_len]
            
            logger.info(f"Downsampling time: {time.perf_counter() - start_time:.4f} seconds. Shape before: {df.shape}, after: {df_final.shape}")
            return df_final
        except Exception as e:
            logger.error(f"Error during downsampling: {e}. Returning original DataFrame.")
            return df

    def _process_rotational_data(self, df):
        """Handles phase unwrapping for rotational data."""
        # Initial shift if starting > 180
        if not df.empty and df["position_raw"].iloc[0] > 180:
            df["position_raw"] = df["position_raw"] - 360
        # Perform unwrapping
        df["position"] = np.unwrap(df["position_raw"].to_numpy(), period=360)
        logger.debug("Performed rotational data unwrapping.")

    def _calculate_velocity(self, df, dt):
        """Calculates velocity using gradient and applies median filter."""
        if len(df) < 2 or dt == 0:
            df["velocity"] = 0.0
            return df
            
        t = df["time"].to_numpy()
        x = df["position"].to_numpy()
        
        # Use numpy.gradient for potentially more accurate velocity calculation
        v = np.gradient(x, dt)

        # Apply median filter to smooth velocity
        filter_size = 5 # Should be odd
        if len(v) >= filter_size:
            filtered_v = median_filter(v, size=filter_size, mode='nearest') # Use mode='nearest' or 'reflect' for edges
        else:
            filtered_v = v # Not enough data points for filter
            
        df["velocity"] = filtered_v

        self._log_high_velocities(df)
        return df
        
    def _log_high_velocities(self, df):
        """Logs warnings if velocity exceeds typical thresholds."""
        if df.empty or 'velocity' not in df.columns:
            return
            
        threshold = 180 if self.measurement_is_rotational else 3000
        unit = "deg/s" if self.measurement_is_rotational else "mm/s"
        max_vel = df["velocity"].abs().max()

        if max_vel > threshold:
            logger.warning(f"Maximum velocity ({max_vel:.2f} {unit}) exceeds threshold ({threshold} {unit}).")
            # Optional: Add more detailed logging for specific high-velocity points
            high_velocity_indices = df.index[df["velocity"].abs() > threshold]
            logger.debug(f"High velocity occurred at times: {df.loc[high_velocity_indices, 'time'].tolist()}")

    # --- Methods adapted from PeakDetector --- 

    def _find_peaks_and_stillstands(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Find peaks in velocity and extract stillstand regions.
        
        Args:
            df: Processed DataFrame with time, position, velocity.

        Returns:
            Tuple containing:
            - Peaks DataFrame.
            - Stillstands DataFrame.
        """
        if df.empty or 'velocity' not in df.columns or self.dt <= 0:
            logger.warning("Cannot find peaks/stillstands: DataFrame is empty, missing velocity, or dt is invalid.")
            return pd.DataFrame(), pd.DataFrame()

        # Find peaks in velocity data
        peaks = self._find_velocity_peaks(df)
        logger.debug(f"Found {len(peaks)} raw velocity peaks.")

        # Clean peaks (remove outliers, edge cases)
        peaks = self._clean_peaks(df, peaks)
        logger.debug(f"Found {len(peaks)} cleaned peaks.")

        # Extract stillstand regions
        stillstands_list = self._extract_stillstands(df, peaks)

        # Create result dataframes
        peaks_df = self._create_peaks_dataframe(df, peaks)
        stillstands_df = pd.DataFrame(stillstands_list) if stillstands_list else pd.DataFrame()

        # Optional: Normalize position based on a reference stillstand (was part of original PeakDetector)
        # df_normalized = self._normalize_position(df, stillstands_list)
        # return df_normalized, peaks_df, stillstands_df 

        return peaks_df, stillstands_df

    def _find_velocity_peaks(self, df: pd.DataFrame) -> np.ndarray:
        """Find peaks in the absolute velocity signal to identify movement start/stop."""
        v = df["velocity"].to_numpy()
        abs_v = (-np.abs(np.abs(v) - (self.v_th * 8))).flatten()
        
        # Parameters for find_peaks need careful tuning
        min_peak_height = self.v_th * 2 # Peak must be significantly above noise threshold
        min_peak_distance = int(self.T_stop / self.dt * 0.1) # Min distance between peaks (related to stop time)
        # Use prominence to avoid minor fluctuations being detected as peaks
        min_peak_prominence = np.max(np.abs(v))*0.2

        if min_peak_distance < 1: min_peak_distance = 1 # Ensure distance is at least 1 sample

        # Find peaks on the absolute velocity signal
        peaks, properties = find_peaks(
            abs_v,
            height=-1 * min_peak_height,
            distance=min_peak_distance,
            prominence=min_peak_prominence,
            # wlen can also be useful (window length for prominence calculation)
            # wlen=int(self.T_stop * 2 / self.dt) 
        )
        # logger.debug(f"find_peaks properties: {properties}")
        return peaks

    def _clean_peaks(self, df: pd.DataFrame, peaks: np.ndarray) -> np.ndarray:
        """Remove outlier peaks based on position and edge conditions."""
        if len(peaks) <= 1:
            return peaks

        # Example cleaning logic (adapt based on specific needs):
        # Remove first peak if it occurs very early and position hasn't changed much (noise)
        if len(peaks) > 0 and df["position"].iloc[peaks[0]] < 1:
            peaks = np.delete(peaks, [0])

        if len(peaks) > 1:
            # Remove the first peak if there's a significant position difference
            # between the first and second peak (indicates movement between them)
            if abs(df["position"].iloc[peaks[1]] - df["position"].iloc[peaks[0]]) > 0.1:
                peaks = np.delete(peaks, [0])

            # Remove the last peak if there's a significant position difference
            # between the last and second-to-last peak (indicates movement between them)
            if len(peaks) >= 2 and abs(df["position"].iloc[peaks[-1]] - df["position"].iloc[peaks[-2]]) > 0.1:
                peaks = np.delete(peaks, -1)
        
        # Remove last peak if it occurs very late?
        # ... add other cleaning rules as identified ...
        
        # Ensure peaks represent significant start/stop events, not just fluctuations during movement
        # (Could involve checking velocity sign changes around peaks, etc.)
        
        return peaks

    def _extract_stillstands(self, df: pd.DataFrame, peaks: np.ndarray) -> List[Dict]:
        """Extracts stillstand regions between pairs of velocity peaks."""
        stillstands = []
        if len(peaks) < 2:
            logger.warning("Not enough peaks to determine stillstand periods.")
            return stillstands

        # Initialize repetition counter and overtravel counter
        repetition = 1
        overtravel_count = 0
        ref_position = None
        
        # Iterate through pairs of peaks (assuming peaks mark start/end of movement)
        for i in range(0, len(peaks) - 1, 2):
            # Indices marking the *end* of movement (peak_start) and *start* of next movement (peak_end)
            idx_move_end = peaks[i]
            idx_move_start_next = peaks[i+1]

            # Calculate stillstand window indices based on T_start and T_stop
            start_idx = int(idx_move_end + self.T_stop / self.dt)
            end_idx = int(idx_move_start_next - self.T_start / self.dt)

            # Validate indices
            if start_idx >= end_idx or start_idx < 0 or end_idx >= len(df):
                logger.debug(f"Skipping invalid stillstand window: peak {i} ({idx_move_end}) to {i+1} ({idx_move_start_next}) -> indices [{start_idx}:{end_idx}] (len={len(df)}) ")
                continue
            
            # Extract data for the stillstand period
            stillstand_data = df.iloc[start_idx:end_idx]
            if stillstand_data.empty:
                logger.debug(f"Stillstand window empty for indices [{start_idx}:{end_idx}]")
                continue

            # Calculate metrics for the stillstand period
            avg_position = np.mean(stillstand_data["position"])
            std_dev_pos = np.std(stillstand_data["position"])
            avg_velocity = np.mean(stillstand_data["velocity"])
            duration = stillstand_data["time"].iloc[-1] - stillstand_data["time"].iloc[0]

            # Determine direction based on velocity at peaks
            vel_at_peak1 = df['velocity'].iloc[idx_move_end]
            vel_at_peak2 = df['velocity'].iloc[idx_move_start_next]
            
            direction = 0
            if vel_at_peak1 > 0 and vel_at_peak2 > 0:
                direction = 1
            elif vel_at_peak1 < 0 and vel_at_peak2 < 0:
                direction = -1
            elif (vel_at_peak1 * vel_at_peak2) < 0:
                direction = 0  # Overtravel

            # Update overtravel counter and repetition
            is_overtravel = direction == 0
            if is_overtravel:
                overtravel_count += 1
                # After 3 overtravels, increment repetition counter
                if overtravel_count >= 3:
                    repetition += 1
                    overtravel_count = 0
                    logger.debug(f"New repetition: {repetition}")

            # For second stillstand (i=1), set reference position
            if i == 1:
                ref_position = np.median(stillstand_data["position"])
                reference_pos_bool = True
            else:
                reference_pos_bool = False

            # Create stillstand dictionary with combined information
            stillstand_info = {
                'still_start_idx': start_idx,
                'still_end_idx': end_idx,
                'still_time_start': df["time"].iloc[start_idx],
                'still_time_end': df["time"].iloc[end_idx],
                'still_duration': duration,
                'still_time_duration': duration,  # For compatibility with old code
                'avg_position': avg_position,
                'std_dev_pos': std_dev_pos,
                'avg_velocity': avg_velocity,

                # Information about the movement phase
                'analysis_start_idx': idx_move_end,
                'analysis_end_idx': idx_move_start_next,
                'analysis_start_pos': df["position"].iloc[idx_move_end],
                'analysis_end_pos': df["position"].iloc[idx_move_start_next],
                'analysis_start_vel': df["velocity"].iloc[idx_move_end],
                'analysis_end_vel': df["velocity"].iloc[idx_move_start_next],
                'analysis_start_time': df["time"].iloc[idx_move_end],
                'analysis_end_time': df["time"].iloc[idx_move_start_next],
                'analysis_duration': df["time"].iloc[idx_move_start_next] - df["time"].iloc[idx_move_end],

                # Direction and repetition information
                'preceding_move_start_idx': idx_move_end,
                'preceding_move_end_idx': idx_move_start_next,
                'preceding_direction': direction,
                'direction': direction,
                'repetition': repetition,
                'overtravel_pos_bool': is_overtravel,
                'reference_pos_bool': reference_pos_bool
            }

            stillstands.append(stillstand_info)

            # Add to reference stillstands if position is close to reference
            if i > 0 and ref_position is not None and abs(avg_position - ref_position) < 0.1:
                logger.debug(f"Stillstand at {df['time'].iloc[start_idx]} seconds used for calculation")
                stillstand_info['reference_pos_bool'] = True

        return stillstands
        
    def _create_peaks_dataframe(self, df: pd.DataFrame, peaks: np.ndarray) -> pd.DataFrame:
        """Creates a DataFrame summarizing detected peak information."""
        if len(peaks) == 0:
            return pd.DataFrame(columns=['index', 'time', 'position', 'velocity'])
        
        peak_times = df['time'].iloc[peaks].values
        peak_positions = df['position'].iloc[peaks].values
        peak_velocities = df['velocity'].iloc[peaks].values
        
        return pd.DataFrame({
            'index': peaks,
            'time': peak_times,
            'position': peak_positions,
            'velocity': peak_velocities
        })

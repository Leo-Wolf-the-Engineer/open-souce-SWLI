import unittest
import pandas as pd
import os
from src.Arduino.data_analyzer import analyze_measurement_data

class TestDataAnalyzer(unittest.TestCase):

    def test_linear_ramp(self):
        # Create synthetic linear ramp data with stagnant windows
        data = {'time_ms': [], 'measurement': []}
        current_time = 0
        measurement = 0
        for i in range(10): # 10 stagnant windows
            # Stagnant window
            for _ in range(100): # 200ms stagnant window
                data['time_ms'].append(current_time)
                data['measurement'].append(measurement)
                current_time += 1
            # Ramp up
            for _ in range(50): # 50ms ramp
                measurement += 0.1
                data['time_ms'].append(current_time)
                data['measurement'].append(measurement)
                current_time += 1

        test_df = pd.DataFrame(data)
        test_csv_file = 'test_linear_ramp.csv'
        test_df.to_csv(test_csv_file, index=False)

        std_dev_threshold = 0.01
        window_size_ms = 100
        wait_time_ms = 10
        averaging_duration_ms = 50

        stagnant_windows_avg = analyze_measurement_data(test_csv_file, std_dev_threshold, window_size_ms, wait_time_ms, averaging_duration_ms)

        os.remove(test_csv_file) # Clean up test CSV file

        self.assertIsNotNone(stagnant_windows_avg)
        self.assertTrue(len(stagnant_windows_avg) >= 10) # Expect at least 10 stagnant windows

        for i, window in enumerate(stagnant_windows_avg):
            self.assertAlmostEqual(window['start_time'], i * 150) # Check start time
            self.assertAlmostEqual(window['end_time'], i * 150 + 99) # Check end time
            self.assertAlmostEqual(window['average_measurement'], i * 0.1, places=1) # Check average measurement

    def test_single_step(self):
        # Placeholder for single step test
        pass

if __name__ == '__main__':
    unittest.main()
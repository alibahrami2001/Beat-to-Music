"""
Pulse Sensor Module for Beat to Music Project
Handles analog pulse sensor reading, filtering, and beat detection

Wiring:
- Pulse Sensor VCC → Pico 3.3V (Pin 36)
- Pulse Sensor GND → Pico GND (Pin 38)  
- Pulse Sensor Signal → Pico GP26 (Pin 31) - ADC0
"""

from machine import Pin, ADC
import utime

class PulseSensor:
    def __init__(self, adc_pin=26, threshold_factor=0.6, min_beat_interval=300):
        """
        Initialize pulse sensor
        
        Args:
            adc_pin: GPIO pin for ADC (default GP26)
            threshold_factor: Multiplier for dynamic threshold (0.0-1.0)
            min_beat_interval: Minimum ms between beats (prevents false triggers)
        """
        self.adc = ADC(Pin(adc_pin))
        self.threshold_factor = threshold_factor
        self.min_beat_interval = min_beat_interval
        
        # Filter variables
        self.filter_size = 10
        self.readings = [0] * self.filter_size
        self.reading_index = 0
        self.filtered_value = 0
        
        # Beat detection variables
        self.baseline = 32768  # Middle of 16-bit ADC range
        self.threshold = 35000
        self.last_beat_time = 0
        self.beat_detected = False
        self.peak_value = 0
        self.valley_value = 65535
        
        # BPM calculation
        self.beat_intervals = []
        self.max_intervals = 5  # Average over last 5 beats
        self.current_bpm = 0
        
        # Calibration
        self.calibration_samples = 100
        self.calibrated = False
        
    def calibrate(self):
        """Calibrate sensor by reading baseline values"""
        print("Calibrating pulse sensor... Keep finger steady!")
        
        min_val = 65535
        max_val = 0
        
        for i in range(self.calibration_samples):
            raw = self.adc.read_u16()
            min_val = min(min_val, raw)
            max_val = max(max_val, raw)
            utime.sleep_ms(10)
            
        self.baseline = (min_val + max_val) // 2
        self.threshold = self.baseline + int((max_val - min_val) * self.threshold_factor)
        self.valley_value = min_val
        self.peak_value = max_val
        
        self.calibrated = True
        print(f"Calibration complete! Baseline: {self.baseline}, Threshold: {self.threshold}")
        
    def read_filtered(self):
        """Read ADC with moving average filter"""
        # Get raw reading
        raw_reading = self.adc.read_u16()
        
        # Update circular buffer
        self.readings[self.reading_index] = raw_reading
        self.reading_index = (self.reading_index + 1) % self.filter_size
        
        # Calculate moving average
        self.filtered_value = sum(self.readings) // self.filter_size
        
        return raw_reading, self.filtered_value
        
    def detect_beat(self):
        """
        Detect heartbeat using filtered signal with dynamic threshold
        Returns: (beat_detected, raw_value, filtered_value, bpm)
        """
        raw_val, filtered_val = self.read_filtered()
        current_time = utime.ticks_ms()
        
        # Update peak and valley for dynamic threshold
        if filtered_val > self.peak_value:
            self.peak_value = filtered_val
        if filtered_val < self.valley_value:
            self.valley_value = filtered_val
            
        # Dynamic threshold adjustment
        signal_range = self.peak_value - self.valley_value
        if signal_range > 1000:  # Only adjust if we have significant signal
            self.threshold = self.valley_value + int(signal_range * self.threshold_factor)
        
        beat_detected = False
        
        # Beat detection: rising edge crossing threshold
        if (filtered_val > self.threshold and 
            not self.beat_detected and 
            utime.ticks_diff(current_time, self.last_beat_time) > self.min_beat_interval):
            
            beat_detected = True
            self.beat_detected = True
            
            # Calculate BPM
            if self.last_beat_time > 0:
                interval = utime.ticks_diff(current_time, self.last_beat_time)
                self.beat_intervals.append(interval)
                
                # Keep only recent intervals
                if len(self.beat_intervals) > self.max_intervals:
                    self.beat_intervals.pop(0)
                    
                # Calculate average BPM
                if len(self.beat_intervals) >= 2:
                    avg_interval = sum(self.beat_intervals) / len(self.beat_intervals)
                    self.current_bpm = int(60000 / avg_interval)  # Convert ms to BPM
                    
            self.last_beat_time = current_time
            
        # Reset beat flag when signal falls below threshold
        elif filtered_val < self.threshold * 0.9:  # Hysteresis to prevent bouncing
            self.beat_detected = False
            
        return beat_detected, raw_val, filtered_val, self.current_bpm
        
    def get_signal_strength(self):
        """Get signal quality indicator (0-100)"""
        signal_range = self.peak_value - self.valley_value
        # Normalize to 0-100 based on expected pulse signal range
        strength = min(100, max(0, (signal_range - 500) // 100))
        return strength
"""
Beat to Music - Main Application
Real-time heart rate monitor with musical feedback and OLED visualization

Hardware Setup:
1. Pulse Sensor:
   - VCC → Pico 3.3V (Pin 36)
   - GND → Pico GND (Pin 38)
   - Signal → Pico GP26 (Pin 31)

2. OLED Display (SSD1306 128x64):
   - VCC → Pico 3.3V (Pin 36)
   - GND → Pico GND (Pin 38)
   - SDA → Pico GP0 (Pin 1)
   - SCL → Pico GP1 (Pin 2)

3. Buzzer/Speaker:
   - Positive → Pico GP15 (Pin 20)
   - Negative → Pico GND (Pin 23)

Installation:
1. Copy all .py files to your Raspberry Pi Pico
2. Install MicroPython on the Pico if not already done
3. Run this main.py file
4. Place finger on pulse sensor and wait for calibration

Author: Ali Bahrami
Project: Beat to Music Heart Rate Monitor
"""

import utime
import gc
from pulse_sensor import PulseSensor
from music_player import MusicPlayer
from display import HeartDisplay

class BeatToMusicApp:
    def __init__(self):
        """Initialize the Beat to Music application"""
        print("Starting Beat to Music application...")
        
        # Initialize hardware modules
        try:
            self.display = HeartDisplay(sda_pin=0, scl_pin=1)
            print("✓ Display initialized")
            
            self.pulse_sensor = PulseSensor(adc_pin=26, threshold_factor=0.6)
            print("✓ Pulse sensor initialized")
            
            self.music_player = MusicPlayer(buzzer_pin=15)
            print("✓ Music player initialized")
            
        except Exception as e:
            print(f"Hardware initialization error: {e}")
            if hasattr(self, 'display'):
                self.display.show_error("Init failed!")
            return
            
        # Application state
        self.running = False
        self.last_beat_time = 0
        self.beat_count = 0
        self.app_start_time = utime.ticks_ms()
        
        # Performance monitoring
        self.loop_count = 0
        self.last_performance_check = utime.ticks_ms()
        
        print("Application initialized successfully!")
        
    def startup_sequence(self):
        """Run startup sequence with splash screen and calibration"""
        print("Starting startup sequence...")
        
        # Show splash screen
        self.display.show_startup_screen()
        self.music_player.play_startup_sound()
        utime.sleep_ms(2000)
        
        # Calibration sequence
        print("Starting calibration...")
        calibration_start = utime.ticks_ms()
        calibration_duration = 3000  # 3 seconds
        
        while utime.ticks_diff(utime.ticks_ms(), calibration_start) < calibration_duration:
            elapsed = utime.ticks_diff(utime.ticks_ms(), calibration_start)
            progress = (elapsed * 100) // calibration_duration
            
            self.display.show_calibration_screen(progress)
            
            if progress == 25 or progress == 50 or progress == 75:
                self.music_player.play_calibration_sound()
                
            utime.sleep_ms(50)
            
        # Perform sensor calibration
        self.pulse_sensor.calibrate()
        
        print("Startup sequence complete!")
        utime.sleep_ms(1000)
        
    def run_main_loop(self):
        """Main application loop"""
        print("Starting main loop...")
        self.running = True
        
        while self.running:
            try:
                loop_start = utime.ticks_ms()
                
                # Read pulse sensor
                beat_detected, raw_value, filtered_value, bpm = self.pulse_sensor.detect_beat()
                
                # Handle beat detection
                if beat_detected:
                    self.handle_beat_detected(bpm)
                    
                # Update music mode based on BPM
                self.music_player.set_mode_by_bpm(bpm)
                
                # Update display
                signal_strength = self.pulse_sensor.get_signal_strength()
                self.display.update_display(bpm, signal_strength, beat_detected, raw_value)
                
                # Performance monitoring
                self.monitor_performance()
                
                # Small delay for stability (adjust based on performance needs)
                loop_time = utime.ticks_diff(utime.ticks_ms(), loop_start)
                if loop_time < 20:  # Target ~50Hz update rate
                    utime.sleep_ms(20 - loop_time)
                    
                # Garbage collection periodically
                if self.loop_count % 100 == 0:
                    gc.collect()
                    
                self.loop_count += 1
                
            except KeyboardInterrupt:
                print("\nShutting down...")
                self.shutdown()
                break
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                self.display.show_error("Runtime error!")
                utime.sleep_ms(2000)
                
    def handle_beat_detected(self, bpm):
        """Handle detected heartbeat"""
        current_time = utime.ticks_ms()
        self.beat_count += 1
        
        print(f"♥ Beat #{self.beat_count} detected! BPM: {bpm}")
        
        # Play beat sound
        self.music_player.play_beat_sound(bpm)
        
        # Optional: Play melody note on every 4th beat
        if self.beat_count % 4 == 0:
            self.music_player.play_melody_note(bpm)
            
        self.last_beat_time = current_time
        
    def monitor_performance(self):
        """Monitor application performance"""
        current_time = utime.ticks_ms()
        
        # Check performance every 5 seconds
        if utime.ticks_diff(current_time, self.last_performance_check) > 5000:
            uptime = utime.ticks_diff(current_time, self.app_start_time) // 1000
            loops_per_sec = self.loop_count * 1000 // max(1, utime.ticks_diff(current_time, self.app_start_time))
            
            print(f"Performance: {loops_per_sec} loops/sec, Uptime: {uptime}s, Beats: {self.beat_count}")
            
            # Reset counters
            self.last_performance_check = current_time
            
            # Memory info
            print(f"Free memory: {gc.mem_free()} bytes")
            
    def shutdown(self):
        """Graceful shutdown"""
        print("Shutting down Beat to Music...")
        self.running = False
        
        # Turn off buzzer
        self.music_player.silence()
        
        # Clear display
        self.display.display.fill(0)
        self.display.display.text("Goodbye!", 35, 28, 1)
        self.display.display.show()
        
        print("Shutdown complete.")
        
def main():
    """Main entry point"""
    print("=" * 50)
    print("Beat to Music - Heart Rate Monitor")
    print("MicroPython on Raspberry Pi Pico")
    print("=" * 50)
    
    # Create and run application
    app = BeatToMusicApp()
    
    try:
        # Run startup sequence
        app.startup_sequence()
        
        # Run main loop
        app.run_main_loop()
        
    except Exception as e:
        print(f"Application error: {e}")
        if hasattr(app, 'display'):
            app.display.show_error("App crashed!")
        
    finally:
        if hasattr(app, 'shutdown'):
            app.shutdown()

if __name__ == "__main__":
    main()
"""
Music Player Module for Beat to Music Project
Generates melodies and tones based on heart rate

Wiring:
- Buzzer/Speaker + → Pico GP15 (Pin 20) - PWM capable pin
- Buzzer/Speaker - → Pico GND (Pin 23)
"""

from machine import Pin, PWM
import utime

class MusicPlayer:
    def __init__(self, buzzer_pin=15):
        """
        Initialize music player with PWM buzzer
        
        Args:
            buzzer_pin: GPIO pin for buzzer (must support PWM)
        """
        self.buzzer_pin = buzzer_pin
        self.buzzer = PWM(Pin(buzzer_pin))
        self.buzzer.duty_u16(0)  # Start silent
        
        # Musical notes (frequencies in Hz)
        self.notes = {
            'C4': 262, 'D4': 294, 'E4': 330, 'F4': 349, 'G4': 392, 'A4': 440, 'B4': 494,
            'C5': 523, 'D5': 587, 'E5': 659, 'F5': 698, 'G5': 784, 'A5': 880, 'B5': 988,
            'C6': 1047, 'D6': 1175, 'E6': 1319
        }
        
        # Melody patterns
        self.calm_melody = ['C4', 'E4', 'G4', 'C5']
        self.normal_melody = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
        self.fast_melody = ['C5', 'E5', 'G5', 'C6', 'G5', 'E5']
        
        self.current_melody = self.normal_melody
        self.melody_index = 0
        
        # Sound parameters
        self.beat_tone_duration = 150  # ms
        self.melody_note_duration = 200  # ms
        self.last_sound_time = 0
        
    def set_mode_by_bpm(self, bpm):
        """Set musical mode based on BPM"""
        if bpm < 60:
            self.current_melody = self.calm_melody
            self.beat_tone_duration = 200
        elif bpm > 100:
            self.current_melody = self.fast_melody
            self.beat_tone_duration = 100
        else:
            self.current_melody = self.normal_melody
            self.beat_tone_duration = 150
            
    def play_beat_sound(self, bpm=70):
        """Play sound for detected heartbeat"""
        # Calculate base frequency from BPM (map 50-120 BPM to 200-800 Hz)
        base_freq = max(200, min(800, int(200 + (bpm - 50) * 8)))
        
        # Play a quick chirp
        self.play_tone(base_freq, 50)
        utime.sleep_ms(20)
        self.play_tone(int(base_freq * 1.2), 30)
        
    def play_melody_note(self, bpm=70):
        """Play next note in current melody"""
        if len(self.current_melody) == 0:
            return
            
        note = self.current_melody[self.melody_index]
        freq = self.notes[note]
        
        # Modify frequency slightly based on BPM
        freq_modifier = 1.0 + (bpm - 70) / 200.0  # Subtle pitch change
        freq = int(freq * freq_modifier)
        
        self.play_tone(freq, self.melody_note_duration)
        
        self.melody_index = (self.melody_index + 1) % len(self.current_melody)
        
    def play_tone(self, frequency, duration_ms):
        """Play a single tone"""
        if frequency > 0:
            self.buzzer.freq(frequency)
            self.buzzer.duty_u16(32767)  # 50% duty cycle
            utime.sleep_ms(duration_ms)
        
        self.buzzer.duty_u16(0)  # Turn off
        
    def play_startup_sound(self):
        """Play startup melody"""
        startup_notes = ['C4', 'E4', 'G4', 'C5', 'G4', 'C5']
        for note in startup_notes:
            self.play_tone(self.notes[note], 150)
            utime.sleep_ms(50)
            
    def play_calibration_sound(self):
        """Play sound during calibration"""
        for i in range(3):
            self.play_tone(440, 100)  # A4
            utime.sleep_ms(100)
            
    def silence(self):
        """Turn off buzzer"""
        self.buzzer.duty_u16(0)
        
    def play_ambient_rhythm(self, bpm):
        """Play ambient rhythm based on current BPM (optional background)"""
        current_time = utime.ticks_ms()
        
        # Calculate interval based on BPM
        beat_interval = 60000 // max(bpm, 1)  # ms per beat
        
        if utime.ticks_diff(current_time, self.last_sound_time) > beat_interval:
            # Play very soft background tone
            base_freq = 150 + (bpm - 60) * 2
            self.buzzer.freq(base_freq)
            self.buzzer.duty_u16(8192)  # Very low volume (12.5%)
            utime.sleep_ms(20)
            self.buzzer.duty_u16(0)
            
            self.last_sound_time = current_time
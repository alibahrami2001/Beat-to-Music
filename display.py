"""
OLED Display Module for Beat to Music Project
Handles SSD1306 128x64 OLED display with waveform and BPM visualization

Wiring:
- OLED VCC → Pico 3.3V (Pin 36)
- OLED GND → Pico GND (Pin 38)
- OLED SDA → Pico GP0 (Pin 1) - I2C SDA
- OLED SCL → Pico GP1 (Pin 2) - I2C SCL
"""

from machine import Pin, I2C
import framebuf
import utime

# SSD1306 OLED Driver (simplified)
class SSD1306_I2C:
    def __init__(self, width, height, i2c, addr=0x3C):
        self.i2c = i2c
        self.addr = addr
        self.width = width
        self.height = height
        
        self.buffer = bytearray(self.width * self.height // 8)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        
        # Initialize display
        self.init_display()
        
    def init_display(self):
        """Initialize OLED display with proper commands"""
        for cmd in [
            0xAE,  # Display off
            0x20, 0x00,  # Set Memory Addressing Mode
            0xB0,  # Set Page Start Address
            0xC8,  # Set COM Output Scan Direction
            0x00,  # Set low column address
            0x10,  # Set high column address
            0x40,  # Set start line address
            0x81, 0x3F,  # Set contrast control register
            0xA1,  # Set segment re-map
            0xA6,  # Set normal display
            0xA8, 0x3F,  # Set multiplex ratio
            0xA4,  # Output RAM to Display
            0xD3, 0x00,  # Set display offset
            0xD5, 0xF0,  # Set display clock divide ratio
            0xD9, 0x22,  # Set pre-charge period
            0xDA, 0x12,  # Set com pins hardware configuration
            0xDB, 0x20,  # Set vcomh
            0x8D, 0x14,  # Set DC-DC enable
            0xAF  # Display on
        ]:
            self.write_cmd(cmd)
            
    def write_cmd(self, cmd):
        """Write command to display"""
        self.i2c.writeto(self.addr, bytes([0x80, cmd]))
        
    def write_data(self, buf):
        """Write data to display"""
        self.i2c.writeto(self.addr, b'\x40' + buf)
        
    def show(self):
        """Update display with buffer contents"""
        self.write_data(self.buffer)
        
    def fill(self, col):
        """Fill entire display"""
        self.framebuf.fill(col)
        
    def pixel(self, x, y, col):
        """Set pixel"""
        self.framebuf.pixel(x, y, col)
        
    def text(self, string, x, y, col=1):
        """Draw text"""
        self.framebuf.text(string, x, y, col)
        
    def line(self, x1, y1, x2, y2, col):
        """Draw line"""
        self.framebuf.line(x1, y1, x2, y2, col)
        
    def rect(self, x, y, w, h, col):
        """Draw rectangle"""
        self.framebuf.rect(x, y, w, h, col)
        
    def fill_rect(self, x, y, w, h, col):
        """Draw filled rectangle"""
        self.framebuf.fill_rect(x, y, w, h, col)

class HeartDisplay:
    def __init__(self, sda_pin=0, scl_pin=1, freq=400000):
        """
        Initialize heart rate display
        
        Args:
            sda_pin: I2C SDA pin (default GP0)
            scl_pin: I2C SCL pin (default GP1)
            freq: I2C frequency
        """
        # Initialize I2C
        self.i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=freq)
        
        # Initialize display
        self.display = SSD1306_I2C(128, 64, self.i2c)
        
        # Waveform buffer
        self.waveform_width = 128
        self.waveform_height = 32
        self.waveform_y_offset = 32
        self.waveform_buffer = [32] * self.waveform_width  # Center line
        self.waveform_index = 0
        
        # Heart animation
        self.heart_beat_time = 0
        self.heart_scale = 0
        
        # Display update timing
        self.last_update_time = 0
        self.update_interval = 50  # 20 FPS
        
        print("OLED Display initialized!")
        
    def show_startup_screen(self):
        """Display startup screen"""
        self.display.fill(0)
        self.display.text("Beat to Music", 15, 10, 1)
        self.display.text("Heart Monitor", 15, 25, 1)
        self.display.text("Initializing...", 10, 45, 1)
        self.display.show()
        
    def show_calibration_screen(self, progress=0):
        """Display calibration screen"""
        self.display.fill(0)
        self.display.text("Calibrating", 20, 10, 1)
        self.display.text("Keep finger", 15, 25, 1)
        self.display.text("steady...", 25, 35, 1)
        
        # Progress bar
        bar_width = int((progress / 100) * 100)
        self.display.rect(14, 50, 100, 8, 1)
        self.display.fill_rect(15, 51, bar_width, 6, 1)
        
        self.display.show()
        
    def add_waveform_point(self, value):
        """Add point to scrolling waveform"""
        # Normalize value to fit waveform area (0-32 pixels)
        normalized = max(0, min(31, int(value / 2048)))  # Assuming 16-bit ADC
        
        self.waveform_buffer[self.waveform_index] = normalized
        self.waveform_index = (self.waveform_index + 1) % self.waveform_width
        
    def draw_waveform(self):
        """Draw scrolling waveform"""
        # Clear waveform area
        self.display.fill_rect(0, self.waveform_y_offset, 128, self.waveform_height, 0)
        
        # Draw waveform
        for i in range(self.waveform_width - 1):
            x1 = i
            y1 = self.waveform_y_offset + (31 - self.waveform_buffer[i])
            x2 = i + 1
            y2 = self.waveform_y_offset + (31 - self.waveform_buffer[(i + 1) % self.waveform_width])
            
            self.display.line(x1, y1, x2, y2, 1)
            
        # Draw center reference line
        self.display.line(0, self.waveform_y_offset + 16, 127, self.waveform_y_offset + 16, 1)
        
    def draw_heart_icon(self, beat_detected=False):
        """Draw animated heart icon"""
        current_time = utime.ticks_ms()
        
        if beat_detected:
            self.heart_beat_time = current_time
            self.heart_scale = 3
        else:
            # Fade heart scale
            time_since_beat = utime.ticks_diff(current_time, self.heart_beat_time)
            if time_since_beat < 200:
                self.heart_scale = 3 - (time_since_beat * 3 // 200)
            else:
                self.heart_scale = 0
                
        # Draw simple heart (two circles and triangle)
        heart_x, heart_y = 105, 8
        size = 1 + self.heart_scale
        
        if size > 1:
            # Heart shape approximation
            self.display.fill_rect(heart_x - size, heart_y, size * 2, size, 1)
            self.display.fill_rect(heart_x - size//2, heart_y - size//2, size, size//2, 1)
            self.display.fill_rect(heart_x, heart_y - size//2, size, size//2, 1)
            
    def update_display(self, bpm, signal_strength, beat_detected, raw_value):
        """Update full display"""
        current_time = utime.ticks_ms()
        
        # Limit update rate for performance
        if utime.ticks_diff(current_time, self.last_update_time) < self.update_interval:
            return
            
        self.display.fill(0)
        
        # Add waveform point
        self.add_waveform_point(raw_value)
        
        # Draw waveform
        self.draw_waveform()
        
        # Display BPM
        bpm_text = f"BPM: {bpm:3d}" if bpm > 0 else "BPM: ---"
        self.display.text(bpm_text, 5, 5, 1)
        
        # Display signal strength
        signal_text = f"Sig: {signal_strength}%"
        self.display.text(signal_text, 5, 15, 1)
        
        # Draw heart icon
        self.draw_heart_icon(beat_detected)
        
        # Status indicators
        if signal_strength < 30:
            self.display.text("Check sensor!", 5, 55, 1)
        elif bpm > 100:
            self.display.text("Fast!", 80, 5, 1)
        elif bpm < 60 and bpm > 0:
            self.display.text("Calm", 80, 5, 1)
            
        self.display.show()
        self.last_update_time = current_time
        
    def show_error(self, message):
        """Display error message"""
        self.display.fill(0)
        self.display.text("ERROR:", 30, 20, 1)
        self.display.text(message, 10, 35, 1)
        self.display.show()
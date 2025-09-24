# Beat to Music - Heart Rate Monitor

A real-time heart rate monitor for Raspberry Pi Pico that converts your heartbeat into music with live OLED visualization.

## Features

- **Real-time pulse detection** with advanced filtering and beat detection
- **Musical feedback** - each heartbeat triggers tones and melodies  
- **Live OLED visualization** - scrolling waveform, BPM display, animated heart
- **Adaptive music modes** - different melodies for calm, normal, and fast heart rates
- **Signal quality monitoring** - displays sensor connection status
- **Professional code structure** - modular design with separate components

## Hardware Requirements

### Components Needed:
- Raspberry Pi Pico (regular or W)
- Pulse sensor with analog output
- SSD1306 OLED display (128x64, I2C)
- Passive buzzer or small speaker
- Breadboard and jumper wires

### Wiring Connections:

#### Pulse Sensor:
```
Pulse Sensor VCC → Pico 3.3V (Pin 36)
Pulse Sensor GND → Pico GND (Pin 38)  
Pulse Sensor Signal → Pico GP26 (Pin 31) [ADC0]
```

#### OLED Display:
```
OLED VCC → Pico 3.3V (Pin 36)
OLED GND → Pico GND (Pin 38)
OLED SDA → Pico GP0 (Pin 1) [I2C SDA]
OLED SCL → Pico GP1 (Pin 2) [I2C SCL]
```

#### Buzzer/Speaker:
```
Buzzer Positive → Pico GP15 (Pin 20) [PWM]
Buzzer Negative → Pico GND (Pin 23)
```

#### Raspberry Pi Pico Pinout:
![Raspberry Pi Pico Pinout](https://www.raspberrypi.com/documentation/microcontrollers/images/pico-pinout.svg)

## Installation

1. **Install MicroPython** on your Raspberry Pi Pico if not already done
2. **Copy all Python files** to your Pico:
   - `main.py`
   - `pulse_sensor.py`  
   - `music_player.py`
   - `display.py`
3. **Connect hardware** according to wiring diagram above
4. **Run the application** by executing `main.py`

### Using Thonny IDE:
1. Connect Pico to computer via USB
2. Open Thonny and select MicroPython (Raspberry Pi Pico) interpreter
3. Copy each `.py` file to the Pico using "Save As" and selecting "Raspberry Pi Pico"
4. Run `main.py`

### Using Command Line:
```bash
# Copy files using rshell or ampy
rshell -p /dev/ttyACM0 cp *.py /pyboard/
# Then run main.py on the Pico
```

## Usage

1. **Power on** the Pico with all connections made
2. **Place finger** gently on the pulse sensor
3. **Wait for calibration** (3-second countdown with audio feedback)
4. **Monitor your heart rate** on the OLED display
5. **Listen to musical feedback** that adapts to your heart rate

### Real Project Photos

![Beat to Music Running - Photo 1](https://github.com/alibahrami2001/Beat-to-Music/blob/main/img/image1-min.jpg)
![Beat to Music Running - Photo 2](https://github.com/alibahrami2001/Beat-to-Music/blob/main/img/image2-min.jpg)

### Display Information:
- **Top left**: Current BPM and signal strength percentage
- **Middle**: Real-time scrolling waveform of your pulse
- **Top right**: Animated heart icon that pulses with each beat
- **Bottom**: Status messages (signal quality warnings, heart rate zones)

### Musical Modes:
- **BPM < 60**: Calm, slow melody with longer notes
- **BPM 60-100**: Normal mode with balanced rhythm  
- **BPM > 100**: Fast, energetic melody with shorter notes

## Code Structure

### `pulse_sensor.py`
- ADC reading with moving average filter
- Dynamic threshold beat detection
- Real-time BPM calculation
- Signal quality assessment
- Automatic calibration

### `music_player.py`
- PWM-based tone generation
- Multiple melody patterns for different heart rate zones
- Beat-synchronized sound effects
- Musical note frequency definitions

### `display.py`
- SSD1306 OLED driver implementation
- Real-time waveform visualization
- BPM and status display
- Animated heart icon
- Startup and calibration screens

### `main.py`
- Application coordination and main loop
- Hardware initialization
- Performance monitoring
- Error handling and graceful shutdown

## Technical Details

### Performance Optimizations:
- **50Hz main loop** for responsive real-time operation
- **Circular buffer** for waveform data
- **Periodic garbage collection** to prevent memory issues
- **Limited display updates** to maintain performance

### Signal Processing:
- **10-point moving average** filter for noise reduction
- **Dynamic threshold** adjustment based on signal amplitude  
- **Hysteresis** in beat detection to prevent false triggers
- **Minimum beat interval** protection (300ms)

### BPM Calculation:
- **Running average** of last 5 inter-beat intervals
- **Real-time updates** with each detected beat
- **Range validation** for physiologically reasonable values

## Troubleshooting

### "Check sensor!" message:
- Ensure pulse sensor connections are secure
- Clean sensor surface and your finger
- Press finger more firmly (but not too hard)
- Try different finger or sensor positioning

### No display output:
- Verify I2C connections (SDA/SCL)
- Check OLED power connections
- Ensure correct I2C address (0x3C)

### No sound output:
- Check buzzer connections
- Verify PWM pin (GP15) is connected correctly
- Test with different buzzer/speaker

### Erratic readings:
- Ensure stable power supply
- Keep sensor and wires away from interference
- Wait for full calibration before use
- Stay still during measurements

## Customization

### Adjusting Sensitivity:
```python
# In pulse_sensor.py, modify:
threshold_factor=0.6  # Lower = more sensitive (0.4-0.8)
min_beat_interval=300  # Minimum ms between beats
```

### Changing Musical Modes:
```python
# In music_player.py, modify melody arrays:
self.calm_melody = ['C4', 'E4', 'G4', 'C5']  # Add your notes
self.fast_melody = ['C5', 'E5', 'G5', 'C6']  # Higher energy
```

### Display Customization:
```python
# In display.py, adjust:
self.update_interval = 50  # Display refresh rate (ms)
self.waveform_height = 32  # Waveform area size
```

## License

This project is open source. Feel free to modify and distribute according to your needs.

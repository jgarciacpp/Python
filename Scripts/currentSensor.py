import spidev
import time
from collections import deque



# --- SPI Setup ---
spi = spidev.SpiDev()
spi.open(0, 0) # Bus 0, CE0
spi.max_speed_hz = 1350000 # Safest Answer for 3.3V System (1.35MHz)
spi.mode = 0 # Mode 0 is being used, Required


# --- Read one channel ---
def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0]) # [Start Bit, Configuration Bit, Dont Care]
    value = ((adc[1] & 3) << 8) + adc[2] # [Have first 2 Bits masked by 3, and shifted 8 to left. Then 8 Bits are added at the end]
    return value # [The final raw digital value]


# --- Target sample rate ---
sample_rate = 2000 # 2 kHz
sample_period = 1.0 / sample_rate

print("Sampling at ~2 kHz. Press Ctrl+C to stop.")

next_time = time.perf_counter()

voltage_buffer = deque(maxlen=100) # [Buffer that holds 100 items]
current_buffer = deque(maxlen=100) # [Buffer for current sensor]

try:
    counter = 0 # [Counter for while loop]
    while True:
        counter += 1
        raw_value_v = read_adc(0)
        voltage = (raw_value_v / 1023.0) * 3.3
        voltage_buffer.append(voltage)
        avg_voltage = sum(voltage_buffer) / len(voltage_buffer)

        raw_value_c = read_adc(1)
        current = (raw_value_c / 1023.0) * 3.3
        current_buffer.append(current)
        avg_current = sum(current_buffer) / len(current_buffer)
    
        # Maintain stable timing
        next_time += sample_period
        sleep_time = next_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)
    
        if counter % 20 == 0:
            print(f"Raw Avg Voltage Conditioning: {avg_voltage:.4f}V | Raw Avg Current Conditioning: {avg_current:.4f}V")


except KeyboardInterrupt:
    spi.close()
    print("Program Stopped.")
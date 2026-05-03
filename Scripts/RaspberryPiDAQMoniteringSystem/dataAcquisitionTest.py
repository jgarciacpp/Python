import time
import spidev
import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

# ==============================
# CONFIGURATION
# ==============================
FS = 2000
LINE_FREQ = 60
CYCLES = 5
NUM_SAMPLES = int(CYCLES * (FS / LINE_FREQ))

FILENAME = "power_samples.csv" 

V_REF = 3.3
ADC_MAX = 1024

# Hardware SPI Setup
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000 # Using safe 1.35MHz speed
spi.mode = 0

def read_adc(channel):
    # Proven ADC read function
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    value = ((adc[1] & 3) << 8) + adc[2]
    return value

# ==============================
# INITIALIZE CSV FILE
# ==============================
with open(FILENAME, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Voltage_Raw", "Current_Raw"])

print(f"Logging started. Saving to {FILENAME}...")
print("Press Ctrl+C to stop.")

# ==============================
# MAIN LOGGING LOOP
# ==============================
t_batch = np.zeros(NUM_SAMPLES)
v_batch = np.zeros(NUM_SAMPLES)
i_batch = np.zeros(NUM_SAMPLES)
sample_interval = 1.0 / FS

try:
    while True:
        next_sample_time = time.perf_counter()

        for k in range(NUM_SAMPLES):
            t_batch[k] = time.time()
            v_batch[k] = read_adc(0)
            i_batch[k] = read_adc(1)

            next_sample_time += sample_interval
            while time.perf_counter() < next_sample_time:
                pass

        with open(FILENAME, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(zip(t_batch, v_batch, i_batch))
        
        print(f"Batch complete. Added {NUM_SAMPLES} samples to {FILENAME}.")

except KeyboardInterrupt:
    spi.close() # Good practice to close SPI on exit
    print("\nLogging stopped.")
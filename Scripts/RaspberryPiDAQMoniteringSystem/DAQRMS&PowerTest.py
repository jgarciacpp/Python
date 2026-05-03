import time
import spidev
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

V_REF = 3.3
ADC_MAX = 1024

# UPDATE THESE: Circuit gains from Design Module 2
VOLTAGE_SCALE = 1.0 
CURRENT_SCALE = 1.0 

# ==============================
# HARDWARE SETUP
# ==============================
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000 # Using safe 1.35MHz speed
spi.mode = 0

def read_adc(channel):
    # Proven ADC read function
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    value = ((adc[1] & 3) << 8) + adc[2]
    return value
    
# Pre-allocate arrays
t_batch = np.zeros(NUM_SAMPLES)
v_batch = np.zeros(NUM_SAMPLES)
i_batch = np.zeros(NUM_SAMPLES)
sample_interval = 1.0 / FS

# ==============================
# MAIN PROCEDURAL LOOP
# ==============================
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

        # 3) CALCULATE RMS, POWER, AND POWER FACTOR
        v_volts = (v_batch / ADC_MAX) * V_REF
        i_volts = (i_batch / ADC_MAX) * V_REF

        v_clean = (v_volts - np.mean(v_volts)) * VOLTAGE_SCALE
        i_clean = (i_volts - np.mean(i_volts)) * CURRENT_SCALE

        Vrms = np.sqrt(np.mean(v_clean**2))
        Irms = np.sqrt(np.mean(i_clean**2))
        P = np.mean(v_clean * i_clean)
        S = Vrms * Irms
        PF = P / S if S != 0 else 0.0
        
        print(f"Vrms: {Vrms:.2f} V | Irms: {Irms:.2f} A | P: {P:.2f} W | S: {S:.2f} VA | PF: {PF:.2f}")
        
except KeyboardInterrupt:
    spi.close() # Good practice to close SPI on exit
    print("\nLogging stopped.")
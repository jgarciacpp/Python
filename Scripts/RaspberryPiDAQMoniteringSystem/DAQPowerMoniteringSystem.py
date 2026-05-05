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
CYCLES = 100 
NUM_SAMPLES = int(CYCLES * (FS / LINE_FREQ)) 

TREND_POINTS = 300

V_REF = 3.3
ADC_MAX = 1024

# UPDATE THESE
VOLTAGE_SCALE = 1.415 
CURRENT_SCALE = 15.0

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

# ==============================
# PLOTTING SETUP
# ==============================
plt.ion()

Vrms_trend = deque(maxlen=TREND_POINTS)
Irms_trend = deque(maxlen=TREND_POINTS)
P_trend    = deque(maxlen=TREND_POINTS)
PF_trend   = deque(maxlen=TREND_POINTS)

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Real-Time Power Trends", fontsize=16, fontweight='bold')

ax_v_RMS = axes[0, 0]
ax_i_RMS = axes[0, 1]
ax_pf    = axes[1, 0]
ax_p     = axes[1, 1]

ax_v_RMS.set_title("Voltage (RMS)")
ax_i_RMS.set_title("Current (RMS)")
ax_pf.set_title("Power Factor")
ax_p.set_title("Real Power")

line_v,  = ax_v_RMS.plot([], [], color='blue')
line_i,  = ax_i_RMS.plot([], [], color='orange')
line_pf, = ax_pf.plot([], [], color='green')
line_p,  = ax_p.plot([], [], color='red')

for ax in axes.flat:
    ax.set_xlim(0, TREND_POINTS)

ax_pf.set_ylim(-1.05, 1.05)
plt.tight_layout()

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

        Vrms_trend.append(Vrms)
        Irms_trend.append(Irms)
        P_trend.append(P)
        PF_trend.append(PF)

        x_data = range(len(Vrms_trend))
        line_v.set_data(x_data, Vrms_trend)
        line_i.set_data(x_data, Irms_trend)
        line_pf.set_data(x_data, PF_trend)
        line_p.set_data(x_data, P_trend)

        ax_v_RMS.set_title(f"Voltage (RMS): {Vrms:.2f} V")
        ax_i_RMS.set_title(f"Current (RMS): {Irms:.2f} A")
        ax_pf.set_title(f"Power Factor: {PF:.2f}")
        ax_p.set_title(f"Real Power: {P:.2f} W")

        ax_v_RMS.relim()
        ax_v_RMS.autoscale_view(scalex=False, scaley=True)
        ax_i_RMS.relim()
        ax_i_RMS.autoscale_view(scalex=False, scaley=True)
        ax_p.relim()
        ax_p.autoscale_view(scalex=False, scaley=True)

        fig.canvas.flush_events()
        plt.pause(0.001) 

except KeyboardInterrupt:
    spi.close() # Good practice to close SPI on exit
    plt.ioff()
    plt.show()
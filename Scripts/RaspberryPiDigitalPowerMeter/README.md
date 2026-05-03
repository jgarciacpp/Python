# Single-Phase Digital Power Meter & Data Acquisition System

## Overview
This project implements a custom data acquisition (DAQ) system using a Raspberry Pi to measure, condition, and analyze single-phase AC power. It acts as the digital bridge between high-voltage/high-current physical systems and software-based power calculation algorithms. 

The system reads concurrent voltage and current waveforms at a stable 2 kHz sample rate, allowing for the real-time calculation of Real Power (P), Reactive Power (Q), Apparent Power (S), and Power Factor (PF).

## Hardware Architecture
This project is heavily focused on hardware-in-the-loop integration. The physical setup consists of two main stages:

### 1. Analog Signal Conditioning
High-voltage AC signals cannot be fed directly into standard microcontrollers. Custom analog circuitry was designed using **LM324 Operational Amplifiers** to safely interface the raw power signals with the 3.3V digital logic of the ADC.
* **Scaling:** Attenuates the incoming AC voltage and current sensor outputs to fit within a 3.0V peak-to-peak window.
* **DC Level Shifting:** Injects a precise 1.65V DC offset to ensure the AC waveform swings safely between 0.15V and 3.15V, preventing negative voltages from destroying the digital chips.

### 2. Digital Conversion (ADC)
An **MCP3008 10-bit Analog-to-Digital Converter** is used to digitize the conditioned analog signals. 
* **Protocol:** Communicates with the Raspberry Pi via the Hardware SPI Bus (Serial Peripheral Interface).
* **Speed:** SPI clock configured for high-speed transfer (1.35 MHz) to ensure negligible delay between reading the voltage and current channels.

## Pinout & Wiring Configuration

### SPI Digital Interface (Raspberry Pi <-> MCP3008)
| Signal | RPi Pin | RPi GPIO | MCP3008 Pin |
| :--- | :--- | :--- | :--- |
| **3.3V Power** | Pin 1 or 17 | 3V3 | Pin 15 (VREF) & Pin 16 (VDD) |
| **Ground** | Pin 6 or 14 | GND | Pin 9 (DGND) & Pin 14 (AGND) |
| **SCLK** | Pin 23 | GPIO 11 | Pin 13 (CLK) |
| **MISO** | Pin 21 | GPIO 9 | Pin 12 (DOUT) |
| **MOSI** | Pin 19 | GPIO 10 | Pin 11 (DIN) |
| **CE0** | Pin 24 | GPIO 8 | Pin 10 (CS/SHDN) |

### Analog Inputs (Sensors <-> MCP3008)
| Signal Source | MCP3008 Channel |
| :--- | :--- |
| Voltage Conditioning Circuit Output | **CH0** (Pin 1) |
| Current Conditioning Circuit Output | **CH1** (Pin 2) |

## Software Requirements & Setup
The logic is written in Python 3 and relies on the `spidev` library for hardware-level SPI communication.

### 1. Enable SPI on the Raspberry Pi
Before running the code, the hardware SPI interface must be enabled in the Linux kernel:
```bash
sudo raspi-config
# Navigate to: Interface Options -> SPI -> Enable -> Yes
sudo reboot
```

### 2. Dependencies
Ensure the SPI library for Python is installed
```bash
pip3 install spidev
```

### 3. Running the DAQ
Execute the main script to begin sampling at ~2kHz. The terminal will output raw, conditioned voltage values (0V-3.3V) for both the voltage and current waveforms.
```bash
python3 DigitalPowerMeter.py
```

## Key Engineering Takeaways
* **Concurrent Sampling:** Developed a looping architecture utilizing time.perf_counter() to maintain a rigid 2 kHz sampling frequency without drifting, essential for accurate AC phase-angle calculations.
* **Hardware Troubleshooting:** Mitigated issues with op-amp saturation, ground loops, and signal clipping during breadboard prototyping.
* **Bit-level Data Manipulation:** Manually reconstructed 10-bit ADC values from raw byte arrays using bitwise masking and shifting in Python.

from gpiozero import MCP3008
from time import sleep

# This connects to Channel 0 of the MCP3008
# It assumes you are using CE0 (GPIO 8) for Chip Select
sensor = MCP3008(channel=0)

print("Reading current sensor... Press Ctrl+C to stop.")

try:
    while True:
        # .value returns a float between 0.0 and 1.0
        # representing the percentage of VREF
        raw_value = sensor.value
        
        # To get the actual voltage:
        voltage = raw_value * 3.3
        
        print(f"Raw: {raw_value:.4f} | Voltage: {voltage:.2f}V")
        sleep(0.5)

except KeyboardInterrupt:
    print("\nProgram stopped.")
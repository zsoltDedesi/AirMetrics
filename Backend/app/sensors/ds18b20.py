# DS18B20 Temperature Sensor Reader

import os, glob, time

device_folder = glob.glob('/sys/bus/w1/devices/28-*')[0]
device_file = device_folder + '/w1_slave'

def read_temp() -> float | None:
    with open(device_file, 'r') as f:
        lines = f.readlines()
            
    if not lines[0].strip().endswith('YES'):
        return None
    
    temp_line = lines[1].split('t=')[1]
    temp_c = float(temp_line) / 1000.0
    return temp_c


if __name__ == "__main__":
    while True:
        print(f"{time.strftime("%H:%M:%S", time.localtime())} Temperature: {read_temp():.2f} °C")
        time.sleep(5)
    # ls /sys/bus/w1/devices/ -> 28-00000xxxxxxx (device folder)
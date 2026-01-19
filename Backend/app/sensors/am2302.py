# AM2302 / DHT22 Temperature and Humidity Sensor Reader

import time
import board
import adafruit_dht

dht = adafruit_dht.DHT22(board.D6, use_pulseio=False)

if __name__ == "__main__":

    while True:
        try:
            t = dht.temperature - 1.5
            h = dht.humidity
            print(f"{time.strftime("%H:%M:%S", time.localtime())} Hőmérséklet: {t:.1f} °C, Páratartalom: {h:.1f}%")
        
        except RuntimeError as e:
            
            
            time.sleep(1)        
            continue

        time.sleep(5)

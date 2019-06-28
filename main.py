import Adafruit_DHT
import time
import datetime
import traceback
from gpiozero import LightSensor, Buzzer

ldr = LightSensor(17)

sensor = Adafruit_DHT.DHT22
pin = 4
file = open("sensor_readings.txt", "a+")
try:
    while(True):
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        file.write(str(datetime.datetime.now()) + "\t" + str(temperature) + "\t" + str(humidity) + "\n")
        file.flush()
        time.sleep(60)
except:
    traceback.print_exc()
    file.close()
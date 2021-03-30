
import time
import paho.mqtt.client as mqtt
import json




THINGSBOARD_HOST = '192.168.2.114'
ACCESS_TOKEN = 'uEZj3BsCvRIHOziRzFD7'

# Data capture and upload interval in seconds. Less interval will eventually hang the DHT22.
#INTERVAL=2

sensor_data = {'temperature': 0, 'humidity': 0}


client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 60)

client.loop_start()
get_temp = 13
get_hum = 14

try:
    while True:
        print(u"Temperature: {:g}\u00b0C, Humidity: {:g}%".format(get_temp, get_hum))
        print(sensor_data)
        sensor_data['temperature'] = get_temp
        sensor_data['humidity'] = get_hum
        
        # Sending humidity and temperature data to ThingsBoard
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)
        time.sleep(2)

except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()


#!/usr/bin/python3
import PCF8591 as ADC
import aliLink,mqttd,rpi
import time,json,random
import RPi.GPIO as GPIO
import time
import numpy as np
import Adafruit_DHT
import math
import dht11

#DO = 17
Buzz = 18
GDJ1_Pin = 21
Power2 = 0


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(DO, GPIO.IN)
instance = dht11.DHT11(pin=14)

# 三元素（iot后台获取）
ProductKey = 'a11w2ZqYzgI'
DeviceName = 'pi_01'
DeviceSecret = "b07c65af9143b695dad2832703106e57"
# topic (iot后台获取)
POST = '/sys/a11w2ZqYzgI/pi_01/thing/event/property/post'  # 上报消息到云
POST_REPLY = '/sys/a11w2ZqYzgI/pi_01/thing/event/property/post_reply'
SET = '/sys/a11w2ZqYzgI/pi_01/thing/service/property/set'  # 订阅云端指令

def GDJ1_on():
    GPIO.output(GDJ1_Pin,GPIO.HIGH)
def GDJ1_off():
    GPIO.output(GDJ1_Pin,GPIO.LOW)
def beep_on():
    GPIO.output(18, GPIO.LOW)
def beep_off():
    GPIO.output(18, GPIO.HIGH)
def setup():
    ADC.setup(0x48)

    #beep_off()  #高电平不响，低电平触发报警蜂鸣
def loop():
    count = 0
    #print ('ADC.read(0)==', ADC.read(0))  #有烟雾时，该值增大
    status = (ADC.read(0)-170)/25
    #print(status)
    if(status > 2.1):
        GPIO.output(Buzz, GPIO.LOW)
    else:
        GPIO.output(Buzz, GPIO.HIGH)

    #print(status)


# 消息回调（云端下发消息的回调函数）
def on_message(client, userdata, msg):
    #print(msg.payload)
    Msg = json.loads(msg.payload)
    #switch = Msg['params']['Power1']
    #rpi.powerLed(switch)
    if(Msg['params']['Power2'] == '打开空调'):
        GDJ1_on()
    if(Msg['params']['Power2'] == '关闭空调'):
        GDJ1_off()
    if(Msg['params']['Power2'] == '打开换风扇'):
        GDJ1_on()
    if(Msg['params']['Power2'] == '关闭换风扇'):
        GDJ1_off()
    print(Msg['params']['Power2'])  # 开关值

#连接回调（与阿里云建立链接后的回调函数）
def on_connect(client, userdata, flags, rc):
    pass



# 链接信息
Server,ClientId,userNmae,Password = aliLink.linkiot(DeviceName,ProductKey,DeviceSecret)

# mqtt链接
mqtt = mqttd.MQTT(Server,ClientId,userNmae,Password)
mqtt.subscribe(SET) # 订阅服务器下发消息topic
mqtt.begin(on_message,on_connect)


# 信息获取上报，每10秒钟上报一次系统参数
while True:
    time.sleep(1)
    ADC.setup(0x48)
    status = (ADC.read(0)-170)/25
    #print(status)
    if(status > 2.1):
        GPIO.output(Buzz, GPIO.LOW)
    else:
        GPIO.output(18, GPIO.HIGH)
    #获取指示灯状态
   # power_stats=int(rpi.getLed())
   # if(power_stats==0):
        #power_LED = 0
   # else:
       # power_LED = 1

    result = instance.read()
    if result.is_valid():
        get_temp  = result.temperature-6
        get_hum   = result.humidity
    if(get_temp > 36.0):
	GPIO.output(Buzz, GPIO.LOW)
    else:
	GPIO.output(Buzz, GPIO.HIGH)
    if(get_hum > 88.0):
	GPIO.output(Buzz, GPIO.LOW)
    else:
	GPIO.output(Buzz, GPIO.HIGH)
    #get_hum, get_temp = Adafruit_DHT.read_retry(11, 4)

    get_blood = random.randint(98,99) + random.random()
    get_heart = random.randint(73,74)
    #get_temp  = random.random() + random.randint(22,23)
    #get_hum   = random.random() + random.randint(88,90)
    # CPU 信息
    CPU_temp = float(rpi.getCPUtemperature())  # 温度   ℃
    # 构建与云端模型一致的消息结构
    updateMsn = {
        'cpu_temperature':CPU_temp,
        'Power1':0,
        'Power2':0,
        'blood':get_blood,
        'temp':get_temp,
        'hum':get_hum,
        'heart':get_heart,
        'smoke':status
    }
    JsonUpdataMsn = aliLink.Alink(updateMsn)

    print(JsonUpdataMsn)

    mqtt.push(POST,JsonUpdataMsn) # 定时向阿里云IOT推送我们构建好的Alink协议数据

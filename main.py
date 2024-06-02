from machine import Pin
import network
import time
from umqtt.simple import MQTTClient
import json
import utime
import machine
import sys

mqtt_client=None

wifi_ssid="undefined"
wifi_password="password"
wlan=network.WLAN(network.STA_IF)

broker_host="216.239.36.53"
broker_port=2000

client_id="device1"
subscribe_topic="device1"


max_broker_reconnect_count=5
broker_reconnect_count=0


drip_motor_state=False
fog_motor_state=False
cooler_motor_state=False
valve_state=False

push_button_last_time=0

drip_motor_pin=Pin(0,Pin.OUT,value=1)
fog_motor_pin=Pin(1,Pin.OUT,value=1)
cooler_motor_pin=Pin(2,Pin.OUT,value=1)
valve_pin=Pin(3,Pin.OUT,value=1)

drip_motor_button_pin=Pin(4,Pin.IN,pull=Pin.PULL_UP)
fog_motor_button_pin=Pin(5,Pin.IN,pull=Pin.PULL_UP)
cooler_motor_button_pin=Pin(6,Pin.IN,pull=Pin.PULL_UP)
valve_button_pin=Pin(7,Pin.IN,pull=Pin.PULL_UP)

drip_motor_led_pin=Pin(8,Pin.OUT,value=0)
fog_motor_led_pin=Pin(9,Pin.OUT,value=0)
cooler_motor_led_pin=Pin(10,Pin.OUT,value=0)
valve_led_pin=Pin(12,Pin.OUT,value=0)

def blink_lights(delay):
    drip_motor_led_pin.value(1)
    fog_motor_led_pin.value(1)
    cooler_motor_led_pin.value(1)
    valve_led_pin.value(1)
    time.sleep(delay)
    drip_motor_led_pin.value(0)
    fog_motor_led_pin.value(0)
    cooler_motor_led_pin.value(0)
    valve_led_pin.value(0)
    time.sleep(delay)
    

def handle_broker_disconnect():
    drip_motor_pin.value(0)
    fog_motor_pin.value(0)
    cooler_motor_pin.value(0)
    valve_pin.value(0)
    

def wifi_connect(ssid,password):
        
       wlan.disconnect()
       wlan.active(True)
       
       if not wlan.isconnected():
           print("connecting to wifi")
           wlan.connect(ssid,password)
           
           while not wlan.isconnected():
               blink_lights(0.25)
               
           print("connected to  wifi")
            
           blink_lights(5)
           
           
def connect_to_broker():
    global broker_reconnect_count
    
    lights_blink_count=0
    
    mqtt_client=MQTTClient(client_id=client_id,server=broker_host,port=broker_port)
    mqtt_client.set_callback(handle_message)
    
    while lights_blink_count < 6:
        blink_lights(0.5)
        lights_blink_count+=1
    
    mqtt_client.connect()
    mqtt_client.subscribe(subscribe_topic)
    print("connected to MQTT broker")
    broker_reconnect_count=0

    blink_lights(5)
    return mqtt_client

    
    
def handle_node(state,pin,led_pin):
    if state:
        pin.value(0)
        led_pin.value(1)
    else:
        pin.value(1)
        led_pin.value(0)
    
def handle_message(topic,message):
    global drip_motor_state,fog_motor_state,cooler_motor_state,valve_state
    data=json.loads(message)
    user_id=data["userId"]
    node_name=data["nodeName"]
    state=data["state"]
    if node_name == "drip-motor":
        drip_motor_state = state
        handle_node(drip_motor_state,drip_motor_pin,drip_motor_led_pin)
        broker_data=json.dumps({"user_id":user_id,"node_name":node_name,"state":drip_motor_state})
        mqtt_client.publish("broker",broker_data)
    
    elif node_name == "fog-motor":
        fog_motor_state = state
        handle_node(fog_motor_state,fog_motor_pin,fog_motor_led_pin)
        broker_data=json.dumps({"user_id":user_id,"node_name":node_name,"state":fog_motor_state})
        mqtt_client.publish("broker",broker_data)
        
    elif node_name == "cooler-motor":
        cooler_motor_state = state
        handle_node(cooler_motor_state,cooler_motor_pin,cooler_motor_led_pin)
        broker_data=json.dumps({"user_id":user_id,"node_name":node_name,"state":cooler_motor_state})
        mqtt_client.publish("broker",broker_data)
        
    else:
        valve_state = state
        handle_node(valve_state,valve_pin,valve_led_pin)
        broker_data=json.dumps({"user_id":user_id,"node_name":node_name,"state":valve_state})
        mqtt_client.publish("broker",broker_data)
        
        
def handle_push_button(name):
    global drip_motor_state,fog_motor_state,cooler_motor_state,valve_state
    global push_button_last_time
    
    push_button_new_time=utime.ticks_ms()
    
    if (push_button_new_time - push_button_last_time) > 300:
        if name == "drip-motor":
            drip_motor_state = not drip_motor_state
            handle_node(drip_motor_state,drip_motor_pin,drip_motor_led_pin)
        
            broker_data=json.dumps({"node_name":name,"state":drip_motor_state})
            mqtt_client.publish("broker",broker_data)
        
        elif name == "fog-motor":
            fog_motor_state = not fog_motor_state
            handle_node(fog_motor_state,fog_motor_pin,fog_motor_led_pin)
        
            broker_data=json.dumps({"node_name":name,"state":fog_motor_state})
            mqtt_client.publish("broker",broker_data)
        
        elif name == "cooler-motor":
            cooler_motor_state = not cooler_motor_state
            handle_node(cooler_motor_state,cooler_motor_pin,cooler_motor_led_pin)
        
            broker_data=json.dumps({"node_name":name,"state":cooler_motor_state})
            mqtt_client.publish("broker",broker_data)
        
        else:
            valve_state = not valve_state
            handle_node(valve_state,valve_pin,valve_led_pin)
        
            broker_data=json.dumps({"node_name":name,"state":valve_state})
            mqtt_client.publish("broker",broker_data)
            
        push_button_last_time=push_button_new_time
        
            
        


    
    
def main():
    global mqtt_client,broker_reconnect_count
    wifi_connect(wifi_ssid,wifi_password)
    
    try:
        drip_motor_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("drip-motor"))
        fog_motor_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("fog-motor"))
        cooler_motor_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("cooler-motor"))
        valve_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("valve"))
    except Exception as e:
        print("failed to add event listeners")
    
    try:
        mqtt_client=connect_to_broker()
        
        while True:
            mqtt_client.check_msg()
    except Exception as e:
        broker_reconnect_count+=1
        time.sleep(1)
        if broker_reconnect_count > max_broker_reconnect_count:
            handle_broker_disconnect()
        else:
            main()
    
    
if __name__ == "__main__":
    main()

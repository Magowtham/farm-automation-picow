from machine import Pin
from umqtt.simple import MQTTClient
import _thread
import network
import time
import utime
import socket
import ujson


main_max_retry=10
push_button_last_time=0

#wifi 
wifi_ssid="undefined"
wifi_password="password"
wifi_connecting_mode=False

#server
server="192.168.209.85"
client_id="device1"
topic="anmaya_iot1.0"
server_connecting_mode=False
server_connected=False


drip_motor_state=False
fog_motor_state=False
cooler_motor_state=False
valve_state=False

drip_motor_pin=Pin(0,Pin.OUT,value=1)
fog_motor_pin=Pin(1,Pin.OUT,value=1)
cooler_motor_pin=Pin(2,Pin.OUT,value=1)
valve_pin=Pin(3,Pin.OUT,value=1)

drip_motor_button_pin=Pin(14,Pin.IN,pull=Pin.PULL_UP)
fog_motor_button_pin=Pin(15,Pin.IN,pull=Pin.PULL_UP)
cooler_motor_button_pin=Pin(16,Pin.IN,pull=Pin.PULL_UP)
valve_button_pin=Pin(17,Pin.IN,pull=Pin.PULL_UP)

drip_motor_led_pin=Pin(18,Pin.OUT,value=0)
fog_motor_led_pin=Pin(19,Pin.OUT,value=0)
cooler_motor_led_pin=Pin(20,Pin.OUT,value=0)
valve_led_pin=Pin(21,Pin.OUT,value=0)


def handle_node(state,pin,led_pin):
    if state:
        pin.value(0)
        led_pin.value(1)
    else:
        pin.value(1)
        led_pin.value(0)
        


def handle_push_button(name):
    global drip_motor_state,fog_motor_state,cooler_motor_state,valve_state
    global push_button_last_time
    
    push_button_new_time=utime.ticks_ms()
    
    if (push_button_new_time - push_button_last_time) > 300:
        print(name)
        try:
            
            if name == "drip-motor":
                drip_motor_state = not drip_motor_state
                handle_node(drip_motor_state,drip_motor_pin,drip_motor_led_pin)
        
            elif name == "fog-motor":
                fog_motor_state = not fog_motor_state
                handle_node(fog_motor_state,fog_motor_pin,fog_motor_led_pin)
      
            elif name == "cooler-motor":
                cooler_motor_state = not cooler_motor_state
                handle_node(cooler_motor_state,cooler_motor_pin,cooler_motor_led_pin)
        
            else:
                valve_state = not valve_state
                handle_node(valve_state,valve_pin,valve_led_pin)
        
        except Exception as e:
            print(e)

        push_button_last_time=push_button_new_time
        

        
def handle_server_message(topic,message):
    global drip_motor_state,fog_motor_state,cooler_motor_state,valve_state
    try:
        data=ujson.dumps(message)
        node_name=data["nodeName"]
        node_state=data["state"]
        
        if node_name == "drip-motor":
            drip_motor_state=node_state
            handle_node(drip_motor_state,drip_motor_pin,drip_motor_led_pin)
        elif node_name == "fog-motor":
            fog_motor_state=node_state
            handle_node(fog_motor_state,fog_motor_pin,fog_motor_led_pin)
        elif node_name == "cooler-motor":
            cooler_motor_state=node_state
            handle_node(cooler_motor_state,cooler_motor_pin,cooler_motor_led_pin)
        else:
            valve_state=node_state
            handle_node(valve_state,valve_pin,valve_led_pin)
    except Exception as e:
        print(e)
        
    
        
        
def wifi_connection_indicater(connecting_delay,connected_delay):
    drip_motor_button_pin.irq(handler=None)
    fog_motor_button_pin.irq(handler=None)
    cooler_motor_button_pin.irq(handler=None)
    valve_button_pin.irq(handler=None)

    while wifi_connecting_mode:
        drip_motor_led_pin.value(1)
        fog_motor_led_pin.value(1)
        cooler_motor_led_pin.value(1)
        valve_led_pin.value(1)
    
        time.sleep(connecting_delay)
    
        drip_motor_led_pin.value(0)
        fog_motor_led_pin.value(0)
        cooler_motor_led_pin.value(0)
        valve_led_pin.value(0)
    
        time.sleep(connecting_delay)
    
    wlan=network.WLAN(network.STA_IF)
    
    if wlan.isconnected():
        drip_motor_led_pin.value(1)
        fog_motor_led_pin.value(1)
        cooler_motor_led_pin.value(1)
        valve_led_pin.value(1)
    
        time.sleep(connected_delay)
    
        drip_motor_led_pin.value(0)
        fog_motor_led_pin.value(0)
        cooler_motor_led_pin.value(0)
        valve_led_pin.value(0)
        
    drip_motor_button_pin.irq(handler=lambda pin:handle_push_button("drip-motor"))
    fog_motor_button_pin.irq(handler=lambda pin:handle_push_button("fog-motor"))
    cooler_motor_button_pin.irq(handler=lambda pin:handle_push_button("cooler-motor"))
    valve_button_pin.irq(handler=lambda pin:handle_push_button("valve"))
    
def server_connection_indicater(connecting_delay,connected_delay):
    drip_motor_button_pin.irq(handler=None)
    fog_motor_button_pin.irq(handler=None)
    cooler_motor_button_pin.irq(handler=None)
    valve_button_pin.irq(handler=None)

    while server_connecting_mode:
        drip_motor_led_pin.value(1)
        fog_motor_led_pin.value(1)
        cooler_motor_led_pin.value(1)
        valve_led_pin.value(1)
    
        time.sleep(connecting_delay)
    
        drip_motor_led_pin.value(0)
        fog_motor_led_pin.value(0)
        cooler_motor_led_pin.value(0)
        valve_led_pin.value(0)
    
        time.sleep(connecting_delay)
    
    wlan=network.WLAN(network.STA_IF)
    
    if server_connected:
        drip_motor_led_pin.value(1)
        fog_motor_led_pin.value(1)
        cooler_motor_led_pin.value(1)
        valve_led_pin.value(1)
    
        time.sleep(connected_delay)
    
        drip_motor_led_pin.value(0)
        fog_motor_led_pin.value(0)
        cooler_motor_led_pin.value(0)
        valve_led_pin.value(0)
        
    drip_motor_button_pin.irq(handler=lambda pin:handle_push_button("drip-motor"))
    fog_motor_button_pin.irq(handler=lambda pin:handle_push_button("fog-motor"))
    cooler_motor_button_pin.irq(handler=lambda pin:handle_push_button("cooler-motor"))
    valve_button_pin.irq(handler=lambda pin:handle_push_button("valve"))
    
    
def main_error_indicater():
    print("main error occurred!!")
    print("please check your wifi provider and server.")
    drip_motor_led_pin.value(1)
    fog_motor_led_pin.value(1)
    cooler_motor_led_pin.value(1)
    valve_led_pin.value(1)


def connect_to_wifi():
    global wifi_connecting_mode
    wifi_connecting_mode=True
    max_wifi_retry=10
    
    _thread.start_new_thread(wifi_connection_indicater,(0.1,3))
    
    while max_wifi_retry > 0:
        wlan=network.WLAN(network.STA_IF)
        wlan.disconnect()
        if not wlan.active():
            wlan.active(True)
        print("searching for ssid "+str(wifi_ssid)+"...")
        scanned_ssid=wlan.scan()
        
        for x in scanned_ssid:
            if wifi_ssid in str(x):
                wlan.connect(wifi_ssid,wifi_password)
                print("trying to connect "+str(wifi_ssid))
                time.sleep(10)
                break
            else:
                pass
        if wlan.isconnected():
            print("connected")
            wifi_connecting_mode=False
            time.sleep(6)
            return
        else:
            print("failed to connect "+str(wifi_ssid))
            max_wifi_retry-=1
            
        time.sleep(1)
    
    if not wlan.isconnected():
        wifi_connecting_mode=False
        print("maximum retry reached...")
        print("failed to connect "+str(wifi_ssid))
        raise Exception("failed to connect wifi")
        
        
def connect_to_server():
    global server_connecting_mode,server_connected
    server_connecting_mode=True
    server_connected=False
    client=MQTTClient(client_id,server,2000)
    client.set_callback(handle_server_message)
    _thread.start_new_thread(server_connection_indicater,(0.5,3))
    try:
        client.connect()
        print("connected to MQTT Broker")
        client.subscribe(topic)
        server_connecting_mode=False
        server_connected=True
        return client
    except Exception as e:
        server_connecting_mode=False
        server_connected=False
        raise Exception("failed to connect server")
        

drip_motor_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("drip-motor"))
fog_motor_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("fog-motor"))
cooler_motor_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("cooler-motor"))
valve_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("valve"))

def main():
    global main_max_retry
    wlan=network.WLAN(network.STA_IF)
    while main_max_retry > 0:
        try:
            connect_to_wifi()
            #client=connect_to_server()
            #main_max_retry=10
            while True:
                #client.wait_msg()
                pass
        except Exception as e:
            print("server connection failed")
            
            time.sleep(2)
            main_max_retry-=1
            
    main_error_indicater()
        
main()
        


        
              








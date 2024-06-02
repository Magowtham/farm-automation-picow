from machine import Pin
import _thread
import network
import time
import utime
import socket

wifi_ssid="undefined"
wifi_password="password"
wlan=network.WLAN(network.STA_IF)

wifi_connecting_mode=False
server_connected=False
client_socket=socket.socket(socket.AF_INET)

push_button_last_time=0

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
        
        
def indicate_wifi_connecting():
    print("connecting to wifi..")
    drip_motor_led_pin.value(1)
    fog_motor_led_pin.value(1)
    cooler_motor_led_pin.value(1)
    valve_led_pin.value(1)
    
    time.sleep(0.1)
    
    drip_motor_led_pin.value(0)
    fog_motor_led_pin.value(0)
    cooler_motor_led_pin.value(0)
    valve_led_pin.value(0)
    
    time.sleep(0.1)

    
def indicate_wifi_connection():
    global wifi_connecting_mode
    
    print("connected to wifi")
    drip_motor_led_pin.value(1)
    fog_motor_led_pin.value(1)
    cooler_motor_led_pin.value(1)
    valve_led_pin.value(1)
    
    time.sleep(3)
    
    drip_motor_led_pin.value(0)
    fog_motor_led_pin.value(0)
    cooler_motor_led_pin.value(0)
    valve_led_pin.value(0)
    
    wifi_connecting_mode=False
    

def indicate_server_connecting():
    print("connecting to server..")
    while not server_connected and not wifi_connecting_mode:
        drip_motor_led_pin.value(1)
        fog_motor_led_pin.value(1)
        cooler_motor_led_pin.value(1)
        valve_led_pin.value(1)
    
        time.sleep(0.5)
    
        drip_motor_led_pin.value(0)
        fog_motor_led_pin.value(0)
        cooler_motor_led_pin.value(0)
        valve_led_pin.value(0)
    
        time.sleep(0.5)
    print("finished job")

def indicate_server_connection():
    print("connected to server")
    drip_motor_led_pin.value(1)
    fog_motor_led_pin.value(1)
    cooler_motor_led_pin.value(1)
    valve_led_pin.value(1)
    
    time.sleep(3)
    
    drip_motor_led_pin.value(0)
    fog_motor_led_pin.value(0)
    cooler_motor_led_pin.value(0)
    valve_led_pin.value(0)
        
    
    
    
def wifi_connect(ssid,password):
    global wifi_connecting_mode
    wifi_connecting_mode=True
    wlan.disconnect()
    wlan.active(False)
    time.sleep(2)
    wlan.active(True)
    
    wlan.connect(ssid,password)
    
    while not wlan.isconnected():
        indicate_wifi_connecting()
    
    indicate_wifi_connection()
    
    
    #_thread.start_new_thread(indicate_server_connecting,())
    
def resolve_domain(domain):
    addr_info = socket.getaddrinfo(domain, 8080)
    return addr_info[0][-1][0]
    
def tcp_connect():
    global server_connected,client_socket
    server_ip=resolve_domain("farm-automation-server-whidgluwra-el.a.run.app")
    print("server_ip :",server_ip)
    while not server_connected:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("farm-automation-server-whidgluwra-el.a.run.app",8080))
            server_connected=True
            time.sleep(0.5)
            indicate_server_connection()
            
        except OSError as e:
            if not wlan.isconnected():
                wifi_connect(wifi_ssid,wifi_password)
            else:
                print(e)
                time.sleep(3)
           





wifi_connect(wifi_ssid,wifi_password)

drip_motor_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("drip-motor"))
fog_motor_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("fog-motor"))
cooler_motor_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("cooler-motor"))
valve_button_pin.irq(trigger=Pin.IRQ_RISING,handler=lambda pin:handle_push_button("valve"))

#tcp_connect()




while True:
    #data = client_socket.recv(1024)
    #print('Received from server:', data)
    pass










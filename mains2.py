# demo.py
# Kevin McAleer
# test the nRF24L01 modules to send and receive data
# Watch this video for more information about that library https://www.youtube.com/watch?v=aP8rSN-1eT0
# ####### S1 controller
from nrf24l01 import NRF24L01
from machine import SPI, Pin
from time import sleep
import struct

csn = Pin(14, mode=Pin.OUT, value=1) # Chip Select Not
ce = Pin(17, mode=Pin.OUT, value=0)  # Chip Enable
led = Pin(25, Pin.OUT)               # Onboard LED
payload_size = 32

relay1 = Pin(21,Pin.OUT, value=1)
relay2 = Pin(20, Pin.OUT, value=1)

# Define the channel or 'pipes' the radios use.
# switch round the pipes depending if this is a sender or receiver pico


#role = "receive"

send_pipe =    b"\xd2\xf0\xf0\xf0\xf0"
receive_pipe = b"\x87\xf0\xf0\xf0\xf0"

def setup():
    print("Initialising the nRF24L0+ Module")
    nrf = NRF24L01(SPI(0), csn, ce, payload_size=payload_size)
    nrf.open_tx_pipe(send_pipe)
    nrf.open_rx_pipe(1, receive_pipe)
    nrf.start_listening()
    return nrf

def flash_led(times:int=None):
    ''' Flashed the built in LED the number of times defined in the times parameter '''
    for _ in range(times):
        led.value(1)
        sleep(0.01)
        led.value(0)
        sleep(0.01)


# main code loop
flash_led(30)
nrf = setup()
nrf.start_listening()

flash_led(1)

while True:

    # Check for Messages
    if nrf.any():
        package = nrf.recv()          
        message = struct.unpack("s",package)
        msg = message[0].decode()
        
        
        flash_led(1)
        print(msg)
        # Check for the new line characte
        if msg == "0":
            relay1.value(1)
            relay2.value(1)
        if msg == "7":  #22 for pull right
            relay2.value(1) 
            relay1.value(0)
            sleep(1)
            relay1.value(1)
        if msg == "8":  #33 for pull left
            relay1.value(1)
            relay2.value(0)
            sleep(1)
            relay2.value(1)
        if msg == "d":
            relay1.value(1)
            relay2.value(1)
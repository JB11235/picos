#MAIN CONTROLLER ............................................................................
  
from nrf24l01 import NRF24L01
from machine import SPI, Pin
from time import sleep, gmtime
import struct
import _thread

csn = Pin(14, mode=Pin.OUT, value=1) # Chip Select Not
ce = Pin(17, mode=Pin.OUT, value=0)  # Chip Enable
led = Pin(25, Pin.OUT)               # Onboard LED
payload_size = 32

#Pin(15, Pin.OUT, Pin.PULL_UP) #switch send signal
n1o = Pin(12, Pin.IN, Pin.PULL_DOWN)
n1i = Pin(13, Pin.IN, Pin.PULL_DOWN)
n2o = Pin(18, Pin.IN, Pin.PULL_DOWN)
n2i = Pin(19, Pin.IN, Pin.PULL_DOWN)

s1o = Pin(10, Pin.IN, Pin.PULL_DOWN)
s1i = Pin(11, Pin.IN, Pin.PULL_DOWN)
s2o = Pin(20, Pin.IN, Pin.PULL_DOWN)
s2i = Pin(21, Pin.IN, Pin.PULL_DOWN)
            #[N1,N2,S1,S2]

move_code = ["1","2","3","4","5","6","7","8"]
stop_code = ["a","b","c","d"]

main_send =  b"\xd2\xf0\xf0\xf0\xf0"
rec_n1 =  b"\xe1\xf0\xf0\xf0\xf0"
rec_n2 =  b"\x96\xf0\xf0\xf0\xf0"
rec_s2 =  b"\x87\xf0\xf0\xf0\xf0"
rec_s1 =  b"\x78\xf0\xf0\xf0\xf0"

def setup(send_var1, rec_var1, rec_var2, rec_var3, rec_var4):
    print("Initialising the nRF24L0+ Module")
    nrf = NRF24L01(SPI(0), csn, ce, payload_size=payload_size)
    #nrf.open_tx_pipe(send_pipe)
    nrf.open_tx_pipe(send_var1)
    #nrf.open_tx_pipe(send_var2)    
    nrf.open_rx_pipe(1, rec_var1)
    nrf.open_rx_pipe(2, rec_var2)
    nrf.open_rx_pipe(3, rec_var3)
    nrf.open_rx_pipe(4, rec_var4)    
    nrf.start_listening()
    return nrf

def flash_led(times:int=None):
    ''' Flashed the built in LED the number of times defined in the times parameter '''
    for _ in range(times):
        led.value(1)
        sleep(0.01)
        led.value(0)
        sleep(0.01)

def send(nrf, msg):
    global runnning_signal
    print("sending message.", msg)
    nrf.stop_listening()
    
    
    for n in range(len(msg)):
        try:
            encoded_string = msg[n].encode()
            byte_array = bytearray(encoded_string)
            buf = struct.pack("s", byte_array)
            nrf.send(buf)
            print("message ",msg[n]," sent")
            flash_led(1)
        except OSError:
            print(role,"Sorry message not sent")
    nrf.start_listening()
    
def send_signal(nrf, parr, carr):   
    for x in range(len(carr)):
        if parr[x] == 0 and carr[x] == 1:
            print("move = ", move_code[x])
            send(nrf, move_code[x])
        if parr[x] == 1 and carr[x] == 0:
            s = stop_code[int(x/2)]
            print("stop = ", s)
            send(nrf, s)
            sleep(0.01)
            send(nrf, s)
            sleep(0.01)
            send(nrf, s)

            
    
def get_buttons(nrf):
    prev_input = [0,0,0,0,0,0,0,0]
    print("start listening for switches")
    global running_signal
    while True:
           
        #take a reading
        input = [n1o.value(), n1i.value(), n2o.value(), n2i.value(), s1o.value(), s1i.value(), s2o.value(), s2i.value()]
        
        #if the last reading was low and this one high, print
        if (prev_input != input):
            print(input)
            running_signal = True
            send_signal(nrf, prev_input, input)
          #update previous input
        prev_input = input
          #slight pause to debounce
        sleep(0.3)
        

nrf = setup(main_send, rec_n1, rec_s1, rec_n1, rec_n2)
nrf.start_listening()
get_buttons(nrf)


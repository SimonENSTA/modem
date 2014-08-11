'''
Autor : Simon
Date  : 08.08.2014
Title : t-fsk4-hamming.py
Resume: Modulate & send the message with hamming corrector code (after a bip)

Run   : python t-fsk4-hamming.py (ID.dest) (message) 
Ex    : python t-fsk4-hamming.py 2 azerty
'''

# import matplotlib.pyplot as plt
import scipy.signal
import numpy as np
import pyaudio
import struct
import time
import sys

import bits_convert_v2
import header_hamming
import hamming


########################################################################

def generate_sin(time_base, f):
	return np.sin(2*np.pi*f*time_base)


def fsk4_modulation(data, s0,s1,s2,s3):
	FSK=[]
	if len(data)%2 == 1:
		data = data + [0]
	for i in range(len(data)/2):
		if data[2*i:2*i+2]==[0,0]:
			FSK=np.concatenate((FSK,s3))
		elif data[2*i:2*i+2]==[1,1]:
			FSK=np.concatenate((FSK,s2))
		elif data[2*i:2*i+2]==[0,1]:
			FSK=np.concatenate((FSK,s1))
		else :
			FSK=np.concatenate((FSK,s0))
	return FSK

########################################################################

# Define stream config
RATE = 44100
CHANNELS = 1
FORMAT = pyaudio.paInt16 

# Define Frequency
fe = 44100
f0=2000 	#10
f1=4000 	#01
f2=6000 	#11
f3=8000 	#00
dt =1.0/fe
duration = 0.01
time_base=np.arange(0, duration, dt)

# Time
start_mod = time.time()

# Built reference sinus
s0 = generate_sin(time_base, f0)
s1 = generate_sin(time_base, f1)
s2 = generate_sin(time_base, f2)
s3 = generate_sin(time_base, f3)

# Built bip
fbip = 10000
tbip = np.arange(0, 0.1, dt)
bip = generate_sin(tbip, fbip)
bip_str = ''
for k in bip:
	bip_str = bip_str + struct.pack('h',int(k*(32767)))

# Config SRC & DST
if len(sys.argv) < 2:
	print("No dest id. (int) \n")
	sys.exit(-1)
id_dest = int(sys.argv[1])
id_source = 1

# Message to transmit
if len(sys.argv) < 3:
	print("No message to transmit (str) \n")
	magic_word = ''
else:
	magic_word = sys.argv[2]

my_data = bits_convert_v2.tobits(magic_word)

# Built header
my_header = header_hamming.toheader(id_source,id_dest,len(my_data)/8)

# Add Hamming code
my_data_ham = hamming.loop_encode_h(my_data)
my_data_h = my_header + my_data_ham

# Add protection
my_data_c = my_data_h + [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1]

# FSK modulation
my_fsk = fsk4_modulation(my_data_c, s0,s1,s2,s3)

# To string
output_str = ''
for k in my_fsk:
	output_str = output_str + struct.pack('h',int(k*(32767)))

# Time
end_mod = time.time()

# Instantiate PyAudio
p = pyaudio.PyAudio()

# Open stream
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
stream.start_stream()
print "Stream Start"

# Read bip
data = bip_str
# Play stream 
stream.write(data)
time.sleep(0.3)
# Read data
data = output_str
# Play stream 
stream.write(data)

# Stop stream
stream.stop_stream()
stream.close()

# Close PyAudio
p.terminate()
print "Stream End"

# Print info
print 'Time for modulation   (s):',end_mod - start_mod
print 'Time for transmission (s):',dt*len(my_fsk)
# print 'Time for transmission (s):',(len(my_data) + 20 +1)*n*duration
print 'Number of bit transmit   :',len(my_fsk)/len(time_base)

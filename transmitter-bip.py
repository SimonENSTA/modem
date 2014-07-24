'''
Autor : Simon
Date  : 21.07.2014
Title : transmitter-bip.py
Resume: Modulate & send the message (after a bip)
'''

# import matplotlib.pyplot as plt
import scipy.signal
import numpy as np
import pyaudio
import struct
import time
import sys

import bits_convert_v2
import header_v3


########################################################################

def channel_coding(data, n):
	data_protec=[]
	for i in range(len(data)):
		if data[i]==1:
			for i in range(n):
				data_protec.append(1)
		else:
			for i in range(n):
				data_protec.append(0)
	return data_protec


def generate_sin(time_base, f):
	return np.sin(2*np.pi*f*time_base)


def fsk_modulation(data, s1, s0):
	FSK=[]
	for i in range(len(data)):
		if data[i]==1:
			FSK=np.concatenate((FSK,s1))
		else:
			FSK=np.concatenate((FSK,s0))
	return FSK

########################################################################

# Define stream config
RATE = 44100
CHANNELS = 1
FORMAT = pyaudio.paInt16 

# Define Frequency
fe = 44100
f0=2000
f1=4000
dt =1.0/fe
duration = 0.008
time_base=np.arange(0, duration, dt)

# Time
start_mod = time.time()

# Built reference sinus
s0 = generate_sin(time_base, f0)
s1 = generate_sin(time_base, f1)

# Built bip
fbip = 8000
tbip = np.arange(0, 0.1, dt)
bip = generate_sin(tbip, fbip)
bip_str = ''
for k in bip:
	bip_str = bip_str + struct.pack('h',int(k*(32767)))

# Message to transmit
if len(sys.argv) < 3:
	print("Give a word to transmit & the dest id. (int) \n")
	sys.exit(-1)
magic_word = sys.argv[1]

my_data = bits_convert_v2.tobits(magic_word)

# Config SRC & DST
id_dest = int(sys.argv[2])
id_source = 1

# Built header
my_header = header_v3.toheader(id_source,id_dest,len(my_data)/8)

my_data_h = my_header + my_data

# Add protection
my_data_c = my_data_h + [0,0,0] 
n = 3
my_data_c = channel_coding(my_data_c,n)

# FSK modulation
my_fsk = fsk_modulation(my_data_c, s1, s0)

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

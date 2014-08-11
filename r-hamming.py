'''
Autor : Simon
Date  : 08.08.2014
Title : r-hamming.py
Resume: Decode a acoustic message in real time with hamming corrector code (require a bip)
'''

import matplotlib.pyplot as plt
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

def decode_fsk(signal, nb_echantillon):
	rest = len(signal) % nb_echantillon
	zero = np.zeros((nb_echantillon - rest))
	signal = np.concatenate((signal,zero))
	nb_trame = len(signal)/nb_echantillon
	signal_matrix = signal.reshape(nb_trame,nb_echantillon)
	message_rcv=[]
	for i in range(nb_trame):
		tmp=signal_matrix[i]
		if np.mean(tmp)>0.2:
			message_rcv.append(0)
		else:
			message_rcv.append(1)
	return message_rcv


def find_message(data_array, id_dest, b, a, duration):
	# Filter
	data_filt = scipy.signal.filtfilt(b, a, data_array)
	# Absolute value
	my_signal_abs = abs(data_filt)
	my_signal_abs = my_signal_abs / max(my_signal_abs)
	# Detect first bit
	for k in range(len(my_signal_abs)):
		if my_signal_abs[k] > 0.2:
			my_signal_k = my_signal_abs[k:]
			break
	my_message_rcv = decode_fsk(my_signal_k, int(44100*duration))
	# Extract the header
	sync,src,dst,len_data,shift = header_hamming.fromheader(my_message_rcv, id_dest)
	if sync == None:
		my_str = None
	elif dst != id_dest:
		my_str = None
	else:
		# Isole the message
		decode_hamming = hamming.loop_decode_h(my_message_rcv[29+shift:])
		data_to_decode = decode_hamming[:len_data*8]
		# Message decode
		my_str=bits_convert_v2.frombits(data_to_decode)
	print 'Name of source            :',src
	print 'Name of dest              :',dst
	print 'Size of data              :',len_data
	print 'The magic word is         :',my_str
	return 1

########################################################################

# Define stream config
WIDTH = 2
CHANNELS = 1
RATE = 44100
FORMAT = pyaudio.paInt16
CHUNK = 1024
RECORD_SECONDS = 2.5

# Define Frequency
fe = 44100
f0=2000
f1=4000
dt =1.0/fe
duration = 0.01
time_base=np.arange(0, duration, dt)

# Config DST
id_dest = 2
micro_input = ''
start = time.time()

# Filter f0 - 2kHz
N = 3
x = f0/(fe/2.0)
Wn=(round(x-0.01,2), round(x+0.01,2))
b_f0, a_f0 = scipy.signal.butter(N, Wn, 'bandpass')

# Filter Bip - 8kHz
x = 8000/(fe/2.0)
Wn=(round(x-0.01,2), round(x+0.01,2))
b_bip, a_bip = scipy.signal.butter(N, Wn, 'bandpass')

# Instantiate PyAudio
p = pyaudio.PyAudio()

# Open stream
print "Stream Start"
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Record micro
while (time.time()-start) < 10:
	for i in range(5):
		data = stream.read(CHUNK)
		micro_input = micro_input + data
	# filter 8kHz
	frames = len(micro_input)/2 
	data_array = np.array(struct.unpack("%dh" % (frames), micro_input))
	data_array = data_array / max(abs(data_array))
	data_filt = scipy.signal.filtfilt(b_bip, a_bip, data_array)
	micro_input=''
	if max(data_filt) > 0.25:
		print max(data_filt)
		for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
			data = stream.read(CHUNK)
			micro_input = micro_input + data
		# Convert micro(str) to array
		frames = len(micro_input)/2 
		data_array = np.array(struct.unpack("%dh" % (frames), micro_input))
		a = find_message(data_array, id_dest, b_f0, a_f0, duration)
		micro_input=''


# Stop stream
stream.stop_stream()
stream.close()

# Close PyAudio
p.terminate()
print "Stream End"

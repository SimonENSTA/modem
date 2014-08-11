'''
Autor : Simon
Date  : 08.08.2014
Title : r-fsk4-hamming.py
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

def decode_fsk(signal, nb_echantillon, x):
	rest = len(signal) % nb_echantillon
	zero = np.zeros((nb_echantillon - rest))
	signal = np.concatenate((signal,zero))
	nb_trame = len(signal)/nb_echantillon
	signal_matrix = signal.reshape(nb_trame,nb_echantillon)
	message_rcv=[]
	for i in range(nb_trame):
		tmp=signal_matrix[i]
		if np.mean(tmp)>0.2:
			message_rcv.append(x)
		else:
			message_rcv.append(0)
	return message_rcv

def add_list(l1, l2, l3):
	l=[]
	len_l = min(len(l1),len(l2),len(l3))
	for i in range(len_l):
		l.append(l1[i]+l2[i]+l3[i])
	return l

def fsk4_to_bin(data):
	to_return = []
	for i in range(len(data)):
		if data[i]==1:
			to_return = to_return + [0,1]
		elif data[i] == 2:
			to_return = to_return + [1,1]
		elif data[i] == 3:
			to_return = to_return + [0,0]
		else :
			to_return = to_return + [1,0]
	return to_return


def find_message(data_array, id_dest, b1, a1, b2, a2, b3, a3, duration):
	# Filter
	data_f1 = scipy.signal.filtfilt(b1, a1, data_array)
	data_f2 = scipy.signal.filtfilt(b2, a2, data_array)
	data_f3 = scipy.signal.filtfilt(b3, a3, data_array)
	# Absolute value
	data_f1_abs = abs(data_f1)
	data_f2_abs = abs(data_f2)
	data_f3_abs = abs(data_f3)
	data_f1_abs = data_f1_abs / max(data_f1_abs)
	data_f2_abs = data_f2_abs / max(data_f2_abs)
	data_f3_abs = data_f3_abs / max(data_f3_abs)
	# Detect first bit
	for k in range(len(data_f1_abs)):
		if data_f3_abs[k] > 0.2:
			data_f1_abs = data_f1_abs[k:]
			data_f2_abs = data_f2_abs[k:]
			data_f3_abs = data_f3_abs[k:]
			break
	# Decode fsk
	message_f1 = decode_fsk(data_f1_abs, int(44100*duration), 1)
	message_f2 = decode_fsk(data_f2_abs, int(44100*duration), 2)
	message_f3 = decode_fsk(data_f3_abs, int(44100*duration), 3)
	# fsk4 to bin
	message_fsk4 = add_list(message_f1,message_f2,message_f3)
	message_bin = fsk4_to_bin(message_fsk4)
	# Extract the header
	sync,src,dst,len_data,shift = header_hamming.fromheader(message_bin, id_dest)
	if sync == None:
		my_str = None
	elif dst != id_dest:
		my_str = None
	else:
		# Isole the message
		decode_hamming = hamming.loop_decode_h(message_bin[29+shift:])
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
RECORD_SECONDS = 1.5

# Define Frequency
fe = 44100
f0=2000 	#10
f1=4000 	#01
f2=6000 	#11
f3=8000 	#00
dt =1.0/fe
duration = 0.01
time_base=np.arange(0, duration, dt)

# Config DST
id_dest = 2
micro_input = ''
start = time.time()

# Filter f1 - 4kHz
N = 3
x = f1/(fe/2.0)
Wn=(round(x-0.01,2), round(x+0.01,2))
b_f1, a_f1 = scipy.signal.butter(N, Wn, 'bandpass')

# Filter f2 - 6kHz
N = 3
x = f2/(fe/2.0)
Wn=(round(x-0.01,2), round(x+0.01,2))
b_f2, a_f2 = scipy.signal.butter(N, Wn, 'bandpass')

# Filter f3 - 8kHz
N = 3
x = f3/(fe/2.0)
Wn=(round(x-0.01,2), round(x+0.01,2))
b_f3, a_f3 = scipy.signal.butter(N, Wn, 'bandpass')

# Filter Bip - 10kHz
x = 10000/(fe/2.0)
Wn=(round(x-0.01,2), round(x+0.01,2))
b_bip, a_bip = scipy.signal.butter(N, Wn, 'bandpass')

# Instantiate PyAudio
p = pyaudio.PyAudio()

# Open stream
print "Stream Start - FSK4"
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
		a = find_message(data_array, id_dest, b_f1, a_f1, b_f2, a_f2, b_f3, a_f3, duration)
		micro_input=''


# Stop stream
stream.stop_stream()
stream.close()

# Close PyAudio
p.terminate()
print "Stream End"

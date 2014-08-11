'''
Autor : Simon
Date  : 05.08.2014
Title : hamming.py
Resume: Hamming Code (7,4)
'''

########################################################################

''' Encode '''
# Input  = [d0, d1, d2, d3]
# Output = [d0, d1, d2, c0, d3, c1, c2]
#
# c0 = d0 + d1 + d2
# c1 = d0 + d1 + d3
# c2 = d0 + d2 + d3

''' Decode '''
# Input  = [b0, b1, b2, b3, b4, b5, b6]
# Output = [b0, b1, b2, b4]
#
# v0 = b0 + b1 + b2 + b3
# v1 = b0 + b1 + b4 + b5
# v2 = b0 + b2 + b4 + b6
#
# Error on bx : x = 7 - bin(v0.v1.v2)

########################################################################

def parite_3(b0,b1,b2):
	x = (b0+b1+b2)%2
	return x

def parite_4(b0,b1,b2,b3):
	x = (b0+b1+b2+b3)%2
	return x

def encode_h(data):
	c0 = parite_3(data[0],data[1],data[2])
	c1 = parite_3(data[0],data[1],data[3])
	c2 = parite_3(data[0],data[2],data[3])
	return data[0:3]+[c0]+[data[-1]]+[c1]+[c2]
	
def loop_encode_h(data):
	in_data = data
	to_return = []
	while len(in_data) >= 4:
		to_encode = in_data[0:4]
		to_return = to_return + encode_h(to_encode)
		in_data = in_data[4:]
	return to_return

def decode_h(data):
	v0 = parite_4(data[0],data[1],data[2],data[3])
	v1 = parite_4(data[0],data[1],data[4],data[5])
	v2 = parite_4(data[0],data[2],data[4],data[6])
	err = 7-(v0*4+v1*2+v2)
	if err != 7:
		data[err] = (data[err]+1)%2
	to_return = data[0:3]+[data[4]]
	return to_return
	
def loop_decode_h(data):
	in_data = data
	to_return = []
	while len(in_data) >= 7:
		to_decode = in_data[0:7]
		to_return = to_return + decode_h(to_decode)
		in_data = in_data[7:]
	return to_return

########################################################################

if __name__ == "__main__":
	print parite_4(1,0,0,0)
	print parite_3(1,1,1)
	
	data=[1,0,1,0,1,0,1,0,0,0,0,0]
	print loop_encode_h(data)
	
	x=[1,1,1,0,0,1,0]
	print decode_h(x)
	
	x=loop_encode_h(data)
	print loop_decode_h(x)
	
	

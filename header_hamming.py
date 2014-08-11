'''
Autor : Simon
Date  : 08.08.2014
Title : header_hamming.py
Resume: Create the header for acoustic channel with hamming corrector code
		Decode the header and check for control data
'''
import bits_convert_v2 as b
import hamming

########################################################################

# sync = 51				- 8 bits
# id. src = ?			- 4 bits
# id. dst = ?			- 4 bits
# len_data = ? in bytes - 4 bits

# len_header = 8 + 7 + 7 + 7


def toheader(source, dest, l_data):
    sync = b.dec_to_bin(51,8)							# sync
    src = b.dec_to_bin(source,4)
    dst = b.dec_to_bin(dest,4)
    len_data= b.dec_to_bin(l_data,4)
    #Hamming protection
    src_ham = hamming.loop_encode_h(src)
    dst_ham = hamming.loop_encode_h(dst)
    len_ham = hamming.loop_encode_h(len_data)
    header = sync + src_ham + dst_ham + len_ham
    return header


def fromheader(data, desti):
	# i is the shift
	i=0
	if len(data) > 19:
		# Decode sync
		sync = b.bin_to_dec(data[i:i+8])
		while sync != 51:											# sync
			i=i+1
			sync = b.bin_to_dec(data[i:i+8])
			if len(data[i:])<20:
				return None, None, None, None, None
		dst_ham = hamming.loop_decode_h(data[i+15:i+22])
		dst = b.bin_to_dec(dst_ham)
		if dst == desti:
			src_ham = hamming.loop_decode_h(data[i+8:i+15])
			src = b.bin_to_dec(src_ham)
			len_ham = hamming.loop_decode_h(data[i+22:i+29])
			len_data = b.bin_to_dec(len_ham)
			return sync, src, dst, len_data, i
		else :
			dst_ham = hamming.loop_decode_h(data[i+16:i+23])
			dst = b.bin_to_dec(dst_ham)
			if dst == desti:
				i=i+1
				src_ham = hamming.loop_decode_h(data[i+8:i+15])
				src = b.bin_to_dec(src_ham)
				len_ham = hamming.loop_decode_h(data[i+22:i+29])
				len_data = b.bin_to_dec(len_ham)
				return sync, src, dst, len_data, i
			else:
				return sync, None, 'You are not dest', None, None
	else:
		return None, None, None, None, None
		


########################################################################

if __name__ == '__main__':
	print toheader(1,2,1)
	print toheader(15,0,2)
	print fromheader([0,0,0], 3)
	a = toheader(0,2,1)
	print a
	print fromheader(a, 0)
	print fromheader(a, 2)
	a = [0,0,0] + a + [0,0,0]
	print fromheader(a, 2)

	


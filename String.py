import argparse,socket
import struct
from random import randint
from uuid import getnode as get_mac

def getMacInBytes():
    mac = str(hex(get_mac()))
    mac = mac[2:]
    while len(mac) < 12 :
        mac = '0' + mac
    macb = b''
    for i in range(0, 12, 2) :
        m = int(mac[i:i + 2], 16)
        macb += struct.pack('!B', m)
    return macb


if __name__ == '__main__':
	input_bytes = b'\xff\xfe4\x001\x003\x00 \x00i\x00s\x00 \x00i\x00n\x00.\x00'
	input = input_bytes.decode('utf-16')
	print(repr(input))
	transactionID = b''
	transactionID += struct.pack('!B', t) 
	macb = getMacInBytes()

	print(repr(packet.decode('ascii')))
import argparse,socket
import struct
from random import randint
from uuid import getnode as get_mac
BUFSIZE = 65535

BOOTREQUEST = b'\x01'
BOOTREPLY = b'\x02'
# DHCP message type code
DHCP_DISCOVER = b'\x35\x01\x01' 
DHCP_OFFER = b'\x35\x01\x02' 
DHCP_REQUEST = b'\x35\x01\x03' 
DHCP_ACK = b'\x35\x01\x05' 
DHCP_TYPE = DHCP_DISCOVER



DHCP_END_OPT = b'255'
IP = b'\x00\x00\x00\x00'
Server_IP = b'192.168.5.1'
MAGIC = b'\x63\x82\x53\x63'
transactionID = b''


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

class DHCPMAKE:
    def __init__(self):
        self.transactionID = b''
        for i in range(4):
            t = randint(0, 255)
            self.transactionID += struct.pack('!B', t) 

    def buildPacket(self,DHCP_SET,DHCP_IP,DHCP_OPT):
        macb = getMacInBytes()
        packet = b''
        packet += DHCP_SET   #Message type: Boot Request (1)
        packet += b'\x01'   #Hardware type: Ethernet
        packet += b'\x06'   #Hardware address length: 6
        packet += b'\x00'   #Hops: 0 
        packet += self.transactionID       #Transaction ID
        packet += b'\x00\x00'    #Seconds elapsed: 0
        packet += b'\x80\x00'   #Bootp flags: 0x8000 (Broadcast) + reserved flags
        packet += b'\x00\x00\x00\x00'   #Client IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'   #Your (client) IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'   #Next server IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'   #Relay agent IP address: 0.0.0.0
        #packet += b'\x00\x26\x9e\x04\x1e\x9b'   #Client MAC address: 00:26:9e:04:1e:9b
        packet += macb
        for i in range (0,202):
            packet += b'\x00'
        packet += b'\x63\x82\x53\x63'   #Magic cookie: DHCP
        packet += DHCP_OPT   #Option: (t=53,l=1) DHCP Message Type = DHCP Discover
        packet += b'\xff'
        #packet += b'\x3d\x06\x00\x26\x9e\x04\x1e\x9b'   #Option: (t=61,l=6) Client identifier
 

        return packet
	

def server(interface,port):
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.bind((interface,67))
	print('Listening at {}'.format(sock.getsockname()))
	while True:
		data,address = sock.recvfrom(BUFSIZE)
		print('Client at {} says {!r}'.format(address,data[0:1]))
		if(data[0:1] == b'\x01'):
			break
	print('Get the discover message from Client!')
	
	
	sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
	offerpacket = DHCPMAKE()
	sock.sendto(offerpacket.buildPacket(BOOTREPLY,Server_IP,DHCP_OFFER),('192.168.5.255',68))
	
	
	while True:
		data,address = sock.recvfrom(BUFSIZE)
		print('Client at {} says {!r}'.format(address,data[0:1]))
		if(data[0:1] == b'\x01'):
			break
	print('Get the request message from Client!')
	
	ackpacket = DHCPMAKE()
	sock.sendto(ackpacket.buildPacket(BOOTREPLY,Server_IP,DHCP_ACK),('192.168.5.255',68))
	
		
def client(network,port):
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
	sock.bind(('', 68))
	discoverPacket = DHCPMAKE()
	sock.sendto(discoverPacket.buildPacket(BOOTREQUEST,IP,DHCP_DISCOVER),(network,67))
	
	
	while True:
		data,address = sock.recvfrom(BUFSIZE)
		print('Server at {} says {!r}'.format(address,data[0:1]))
		if(data[0:1] == b'\x02'):
			break
	print('Get the offer message from Server!')
	
	requestpacket = DHCPMAKE()
	sock.sendto(requestpacket.buildPacket(BOOTREQUEST,IP,DHCP_REQUEST),(network,67))
	
	
	while True:
		data,address = sock.recvfrom(BUFSIZE)
		print('Server at {} says {!r}'.format(address,data[0:1]))
		if(data[0:1] == b'\x02'):
			break
	print('Get the ACK message from Server!')
	
	

if __name__ == '__main__' :
	choices = {'client':client,'server':server}
	parser = argparse.ArgumentParser(description = 'send and receive UDP Broadcast')
	parser.add_argument('role',choices = choices,help = 'which role to take')
	parser.add_argument('host',help = 'interface the server listens at;''network the client sends to')
	parser.add_argument('-p',metavar='PORT',type=int, default = 1060, help = 'UDP port(default 1060)')
	
	args = parser.parse_args()
	function = choices[args.role]
	function(args.host,args.p)
import socket
import json
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the server is listening
server_address = ('windows-wired', 5000)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
t0 = time.time()

def _send_command(command,value):
	# Send data
	message = json.dumps({'action':command,'value':value}).encode()
	#print('sending {!r}'.format(message))
	sock.sendall(message)
	# Look for the response
	amount_received = 0
	amount_expected = 32
	#print('amount expected', amount_expected)
	while amount_received < amount_expected:
		data = sock.recv(64)
		jsonstr = json.loads(data.decode())
		amount_received += len(data)
		#print('received {!r}'.format(data))
		#print('jsondata',jsonstr['value'])
	if jsonstr['action'] == 'close':
		sock.close()
		print('closing socket')
	return jsonstr

print(time.time()-t0)
if __name__ == "__main__":
	while True:
		command = str(input("Enter command (zmove, close): "))
		if command == "zmove":value = float(input("input value: " ))
		elif command == 'close':value = ""
		_send_command(command,value)

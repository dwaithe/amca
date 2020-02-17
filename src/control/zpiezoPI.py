from ctypes import*
import json
import socket
def initiate_axis(pidll,ID, axis,verbose=False):
	""" 
	Initiate PI controller along an axis.
	
	Inputs
	--------------

	pidll - library functions.
	ID - reference to connection.
	axis - controller axis on which to apply.
	verbose - print outputs.

	Outputs
	--------------
	init - If axis was successfully initiated (1), if not (0).

	"""

	charptr = create_string_buffer(100) 
	pidll.E7XX_qSAI_ALL(ID,charptr,100)

	init = pidll.E7XX_INI(ID,axis)
	if verbose:
		print("Available axis",charptr.value)
		if init:
			print('Axis',axis,' initiated')
		else:
			print('Axis',axis,' failed to init')

	return init


def turn_servo_on(pidll,ID,axis,verbose=False):
	""" 
	Turn servo on for an axis.
	
	Inputs
	--------------

	pidll - library functions.
	ID - reference to connection.
	axis - controller axis on which to apply.
	verbose - print outputs.

	Outputs
	--------------
	query_servo - If servo is on (1), or off (0).

	"""
	
	cint = c_int32(1)
	pidll.E7XX_SVO(ID,axis,byref(cint))
	
	query_servo = c_int32()
	pidll.E7XX_qSVO(ID,axis,byref(query_servo))
	
	if verbose:
		if query_servo:
			print('servo is on.')
		else:
			print('servo is not on.')
	return query_servo


def move_piezo(pidll,ID,axis,pos,verbose=False):
	""" 
	Tests the movement by initiating movement to predefined position e.g. 4.5.
	
	Inputs
	--------------

	pidll - library functions.
	ID - reference to connection.
	axis - controller axis on which to apply.
	pos - sets the position to move to.
	verbose - print outputs.

	Outputs
	--------------
	move_succ - If move is successful (1), if not (0).

	"""
	move_pntr = c_double(pos)
	move_succ = pidll.E7XX_MOV(ID, axis, byref(move_pntr))
	
	if verbose:
		if move_succ:
			print('Move was successful.')
		else:
			print('move failed.')
	return move_succ

def check_for_errors(pidll,ID,verbose=False):
	"""
	Check for errors.
	
	Inputs
	--------------

	pidll - library functions.
	ID - reference to connection.
	verbose - print error code.

	Outputs
	--------------
	Returns error code.

	"""
	piError = c_long()
	pidll.E7XX_qERR(ID,byref(piError))
	if verbose:
		
		print('piError (0 == no error).',piError.value)
	
	return piError

def query_position(pidll,ID,axis,verbose=False):
	""" 
	Query the position.
	
	Inputs
	--------------

	pidll - library functions.
	ID - reference to connection.
	axis - controller axis on which to apply.
	verbose - print outputs.

	Outputs
	--------------
	query_pos - returns the position of the stage


	"""
	cdb1 = c_double(0.0)
	query_pos = pidll.E7XX_qPOS(ID, axis, byref(cdb1))
	if verbose:
		if query_pos:	
			print('Position of piezo.',cdb1.value)
		else:
			print('Error finding position')
	return	cdb1.value	

if __name__ == "__main__":

	axis = '3'
	verbose = 1

	pidll = cdll.LoadLibrary('c:/Documents and Settings/LattePanda/Downloads/E710/E710/E7XX_GCS_DLL_x64.dll')
	port = 4
	print('port',port)
	ID = pidll.E7XX_ConnectRS232(port,57600)

	initiate_axis(pidll,ID, axis,verbose)
	turn_servo_on(pidll,ID,axis,verbose)
	#move_piezo(pidll,ID,axis,0,verbose)
	
	check_for_errors(pidll,ID,verbose)
	#query_position(pidll,ID,axis,verbose)
	
	

	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Bind the socket to the port
	server_address = ('0.0.0.0', 5000)
	print('Starting up on {} port {}'.format(*server_address))
	sock.bind(server_address)

	# Listen for incoming connections
	sock.listen(1)

	while True:
		# Wait for a connection
		print('waiting for a connection')
		connection, client_address = sock.accept()
		try:
		   print('connection from', client_address)
		   while True:
		   	data = connection.recv(64)
		   	
		   	#print('received {!r}'.format(data))
		   	if data:
		   		jsondata = json.loads(data.decode())
		   		if jsondata['action'] == 'zmove_only':
		   			#print('postomove',float(jsondata['value']))
		   			move_piezo(pidll,ID,axis,float(jsondata['value']),verbose)
		   			check_for_errors(pidll,ID,verbose)
			   		jsonreturn = json.dumps({'action':'report','value':'moved'}).encode()
		   			connection.sendall(jsonreturn)
		   		if jsondata['action'] == 'zmove':
		   			#print('postomove',float(jsondata['value']))
		   			move_piezo(pidll,ID,axis,float(jsondata['value']),verbose)
		   			check_for_errors(pidll,ID,verbose)
			   		#print('sending data back to the client')
			   		q_pos = query_position(pidll,ID,axis,verbose)
			   		#print('qpos',q_pos)
			   		jsonreturn = json.dumps({'action':'report','value':str(q_pos)}).encode()
		   			connection.sendall(jsonreturn)
		   		if jsondata['action'] == 'qpos':
		   			q_pos = query_position(pidll,ID,axis,verbose)
			   		jsonreturn = json.dumps({'action':'report','value':str(q_pos)}).encode()
		   			connection.sendall(jsonreturn)
		   		if jsondata['action'] == 'close':
		   			pidll.E7XX_CloseConnection(ID)
		   			jsonreturn = json.dumps({'action':'report','value':"closed"}).encode()
		   			connection.sendall(jsonreturn)
		   			exit()
		   	else:
			   	print('no data from', client_address)
			   	break
		finally:
		   # Clean up the connection
		   print("Closing current connection")
		   connection.close()


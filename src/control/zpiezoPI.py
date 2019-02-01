from ctypes import*

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

	pidll = cdll.LoadLibrary('c:/Users/immuser/Documents/E710_GCS_DLL/E7XX_GCS_DLL_x64.dll')
	ID = pidll.E7XX_ConnectRS232(5,57600)

	initiate_axis(pidll,ID, axis,verbose)
	turn_servo_on(pidll,ID,axis,verbose)
	move_piezo(pidll,ID,axis,4.5,verbose)
	
	check_for_errors(pidll,ID,verbose)
	query_position(pidll,ID,axis,verbose)
	pidll.E7XX_CloseConnection(ID)

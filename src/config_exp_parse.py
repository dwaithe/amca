import numpy as np

def parse_acquisition_def(path):
	commands ={}
	commands['ch_to_image']= None
	commands['excitation_lines']= None
	commands['exposures']= None
	commands['ch_to_analyze']= None
	commands['ch_to_save']= None
	commands['cam_gain']= None
	commands['cam_binning']= None
	commands['lim_min_x']= None
	commands['lim_max_x']= None
	commands['lim_min_y']= None
	commands['lim_max_y']= None
	commands['clim_min_x']= None
	commands['clim_max_x']= None
	commands['clim_min_y']= None
	commands['clim_max_y']= None
	commands['digital_binning']= None
	commands['cam_pixel_size']= None
	commands['objective_mag']= None
	commands['objective_type']= None
	commands['camera_type']= None
	commands['lamp_type']= None
	commands['microscope_type']= None
	commands['analysis_method']= None
	commands['z_stage_move']= None
	
	commands['display_out']= None
	commands['out_path']= None
	commands['save_out']= None
	commands['positions_file_path']= None
	commands['output_positions_name']= None
	commands['exp_depth']= None
	
	commands['dkrepo']= None
	commands['algorithm_name']= None
	commands['config_path']= None
	commands['meta_path']= None
	commands['weight_path']= None
	
	
	

	f = open(path, "rt")
	lines = f.readlines()
	for pr in lines:
		line = pr.strip("\n").split('#')[0]
		chunk = None
		if line.split("=").__len__() >1:
			chunk = line.split("=")[0].strip(" ")
			value = line.split("=")[1].strip(" ")
			
			if chunk in commands:
				#print(chunk,value)
				if chunk == "ch_to_image": commands['ch_to_image'] = int(value)
				elif chunk == "excitation_lines": 
					commands['excitation_lines'] =value.strip("[").strip("]").replace('"', '').replace("'", '').split(",")
				elif chunk == 'exposures': 
					values = value.strip("[").strip("]").split(",")
					commands['exposures'] = []
					for val in values:
						commands['exposures'].append(int(val))
				elif chunk == 'ch_to_analyze': commands['ch_to_analyze'] = int(value)
				elif chunk == 'ch_to_save': commands['ch_to_save'] = int(value)
				elif chunk == 'cam_gain': commands['cam_gain'] = int(value)
				elif chunk == 'cam_binning': commands['cam_binning'] = int(value)
				elif chunk == 'lim_min_x': commands['lim_min_x'] = int(value)
				elif chunk == 'lim_max_x': commands['lim_max_x'] = int(value)
				elif chunk == 'lim_min_y': commands['lim_min_y'] = int(value)
				elif chunk == 'lim_max_y': commands['lim_max_y'] = int(value)
				elif chunk == 'clim_min_x': commands['clim_min_x'] = int(value)
				elif chunk == 'clim_max_x': commands['clim_max_x'] = int(value)
				elif chunk == 'clim_min_y': commands['clim_min_y'] = int(value)
				elif chunk == 'clim_max_y': commands['clim_max_y'] = int(value)
				elif chunk == 'digital_binning': commands['digital_binning'] = int(value)
				elif chunk == 'cam_pixel_size': commands['cam_pixel_size'] = float(value)
				elif chunk == 'objective_mag': commands['objective_mag'] = int(value)
				elif chunk == 'objective_type': commands['objective_type'] = str(value.strip('"').strip("'"))
				elif chunk == 'camera_type': commands['camera_type'] = str(value.strip('"').strip("'"))
				elif chunk == 'lamp_type': commands['lamp_type'] = str(value.strip('"').strip("'"))
				elif chunk == 'microscope_type': commands['microscope_type'] = str(value.strip('"').strip("'"))
				elif chunk == 'analysis_method': commands['analysis_method'] = str(value.strip('"').strip("'"))
				elif chunk == 'z_stage_move': commands['z_stage_move'] = float(value)
				
				elif chunk == 'display_out': 
					booln = value.replace('"', '').replace("'", '')
					if booln == "False":
						 commands['display_out'] = False
					if booln == "True":
						 commands['display_out'] = True
						
				
				elif chunk == 'out_path': commands['out_path'] =  str(value.strip('"').strip("'"))
				elif chunk == 'save_out': commands['save_out'] =  str(value.strip('"').strip("'"))
				elif chunk == 'positions_file_path': commands['positions_file_path'] =  str(value.strip('"').strip("'"))
				elif chunk == 'output_positions_name': commands['output_positions_name'] =  str(value.strip('"').strip("'"))

				elif chunk == 'exp_depth': 
					if value == 'np.uint16':
						commands['exp_depth'] = np.uint16
				elif chunk == 'dkrepo':commands['dkrepo'] = str(value).replace('"', '').replace("'", '')
				elif chunk == 'algorithm_name':commands['algorithm_name'] = str(value).replace('"', '').replace("'", '')
				elif chunk == 'config_path':commands['config_path'] = str(value).replace('"', '').replace("'", '')
				elif chunk == 'meta_path':commands['meta_path'] = str(value).replace('"', '').replace("'", '')
				elif chunk == 'weight_path':commands['weight_path'] = str(value).replace('"', '').replace("'", '')
	for it in commands:
		if commands[it] == None:
			print(commands[it])		
	return commands
	

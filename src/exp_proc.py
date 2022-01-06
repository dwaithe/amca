import convert_voc_to_other as cvto
import numpy as np
def get_class_names(class_name_path):
	f = open(class_name_path)
	class_names = []
	for line in f.readlines():
		line = line.strip("\n")
		if line != '':
			class_names.append(line)
	return class_names
def get_experiment_parameters(path_to_amca_config,exp_id):
	f = open(path_to_amca_config+exp_id)
	def next_line():
		line = f.readline().strip("\n")
		while line == '':
				line = f.readline().strip("\n")
		if '#' in line:
			line = line.split('#')[0]
		return line
	
	model_array = []
	train_array = []
	classes = []
	test_array = []
	rep_array = []
	flip_on_array = []
	focus_mode_array = []
	psf_width_pixels_array = []
	z_depth_meters_array = []
	focus_levels_array = []
	depth_of_network_array = []
	
	while 1:
		line = f.readline()
		if not line:
			break
		line = line.strip("\n")
		if line[0:13] == "out_file_log=":
			out_file_log = line[13:].strip("\"").strip("\'")
			line = next_line()
		
		if line[0:5] =="start":
			models = {}
			line = next_line()
			if line[0:23] == "faster_rcnn_model_init=":
				models['faster_rcnn_model_init'] = line[23:].strip("\"")
				line = next_line()
			if line[0:20] == "darknet2_model_init=":
				models['darknet2_model_init'] =line[20:].strip("\"")
				line = next_line()
			if line[0:20] == "darknet3_model_init=":
				models['darknet3_model_init'] =line[20:].strip("\"")
				line = next_line()
			if line[0:21] == "retinanet_model_init=":
				models['retinanet_model_init'] =line[21:].strip("\"")
				line = next_line()
			model_array.append(models)
			if line[0:17] == "depth_of_network=":
				depth_of_network_array.append(line[17:].strip("\"").strip("\'"))
			line = next_line()
			
			

			if line[0:17] == "train_on_dataset=":
				train_array.append(line[17:].strip("\"").strip("\'"))
			line = next_line()
			if line[0:11] == "focus_mode=":
				focus_mode_array.append(line[11:].strip("\"").strip("\'"))
			line = next_line()

			if line[0:8] == "classes=":
				classes.append(line[8:].strip("\"").strip("\'"))
			line = next_line()
			
			if line[0:8] == "flip_on=":

				flip_on_array.append(line[8:].strip("\"").strip("\'"))
			line = next_line()
			temp_test_array = []
			while line[0:22] != "number_of_repetitions=":
				if line[0:16] == "test_on_dataset=":
					temp_test_array.append(line[16:].strip("\"").strip("\'").split(","))
				if line[0:17] == "psf_width_pixels=":
					psf_width_pixels_array.append(line[17:].strip("\"").strip("\'"))
				if line[0:15] == "z_depth_meters=":
					z_depth_meters_array.append(line[15:].strip("\"").strip("\'"))
				if line[0:13] == "focus_levels=":
					focus_levels_array.append(line[13:].strip("\"").strip("\'"))
				line = next_line()
			test_array.append(temp_test_array)
			if line[0:22] == "number_of_repetitions=":
				rep_array.append(int(line[22:].strip("\"").strip("\'")))
			
			
			if model_array.__len__() == train_array.__len__() == rep_array.__len__() == test_array.__len__() == flip_on_array.__len__() == classes.__len__():
				pass
			elif focus_mode_array.__len__() == psf_width_pixels_array.__len__() == z_depth_meters_array.__len__() == focus_levels_array.__len__():
				pass
			else:
				print('failed\n')
				print('One of your datasets was not complete:',model_array.__len__())
				print('start #Erythroblast dapi class')
				print('faster_rcnn_model_init=""')
				print('darknet2_model_init="darknet19_448.conv.23"')
				print('darknet3_model_init="darknet53.conv.74"')
				print('retinanet_model_init="../../models/pytorch/erythroblast_dapi_class80/modal_final.pt"')
				print('depth_of_network="50"')
				print('train_on_dataset=""')
				print('focus_mode=True')
				print('classes=1')
				print('flip_on=True')
				print('test_on_dataset="dataset8"')
				print('psf_width_pixels="51"')
				print('z_depth_meters="584e-9"')
				print('focus_levels="10"')
				print('number_of_repetitions=1')
				assert False
	
	exp_param = {}
	
	exp_param['model_array'] = model_array
	exp_param['train_on_dataset'] = train_array
	exp_param['test_on_dataset'] = test_array
	exp_param['rep_array'] = rep_array
	exp_param['depth_of_network'] = depth_of_network_array
	exp_param['flip_on_array'] = flip_on_array
	exp_param['focus_mode'] = focus_mode_array
	exp_param['classes'] = classes
	exp_param['out_file_log'] = out_file_log
	exp_param['psf_width_pixels'] = psf_width_pixels_array
	exp_param['z_depth_meters'] = z_depth_meters_array
	exp_param['focus_levels'] = focus_levels_array
	


	return exp_param
def load_dataset(path_to_data,path_to_amca_config,dataset):
	
	if dataset[0:7] == 'dataset':
		path_to_spec = path_to_amca_config+"dataset_spec.txt"
		blk_dataset_param = cvto.return_dataset_spec(path_to_spec)

		indices = blk_dataset_param['indices']
		datasets = blk_dataset_param['datasets']
		datasets_size = blk_dataset_param['datasets_size']
		datasets_class = blk_dataset_param['datasets_class']
		pixel_size_meters_arr = blk_dataset_param['pixel_size_meters_arr']
		wavelength_arr = blk_dataset_param['wavelength_arr']
		num_aperture_arr = blk_dataset_param['num_aperture_arr']
		refractive_ind_arr = blk_dataset_param['refractive_ind_arr']
		
		idx = int(dataset[7:].strip("\""))
		print(idx,indices)
		c = 0
		d = 0
		for ind in indices:

			if ind == idx:
				dataset_dir = datasets[c]
				dataset_size = datasets_size[c]
				dataset_class = datasets_class[c]
				pixel_size_meters = pixel_size_meters_arr[c]
				wavelength = wavelength_arr[c]
				num_aperture = num_aperture_arr[c]
				refractive_ind = refractive_ind_arr[c]
				d+=1
			c+=1
		assert d != 0, "A test dataset was referenced which doesn't exist."
		
		#Experiment specific.
		num_of_train = str(dataset_size[0])
		year = dataset_dir.split('/')[1]
		test_set="test_dn_n"+str(dataset_size[1])
		cell_class=dataset_class
		dataset = dataset_dir.split('/')[0]

		#The .data object.
		dn_mixed_class_name=dataset+num_of_train
		path_to_training_def = path_to_data+dataset_dir+"/obj_"+dn_mixed_class_name+".data"
		path_to_class_names = path_to_data+dataset_dir+"/obj_"+dataset+".names"
		cell_classes = get_class_names(path_to_class_names)

		
		dataset_param = {}
		dataset_param['num_of_train'] = num_of_train
		dataset_param['year'] = year
		dataset_param['test_set'] = test_set
		dataset_param['cell_classes'] = cell_classes
		dataset_param['dataset'] = dataset
		dataset_param['path_to_training_def'] = path_to_training_def
		dataset_param['pixel_size_meters'] = pixel_size_meters
		dataset_param['wavelength'] = wavelength
		dataset_param['num_aperture'] = num_aperture
		dataset_param['refractive_ind'] = refractive_ind

		return dataset_param
		
	elif dataset[0:5] == 'mixed':
		path_to_spec = path_to_amca_config+"mixed_dataset_spec.txt"
		indices, param = cvto.return_mixed_dataset_spec(path_to_spec)
		idx = int(dataset[5:].strip("\""))
		
		
		c = 0
		d = 0
		for ind in indices:

			if ind == idx:

				dataset_dir = param[ind]['dataset_path']
				dataset_size = ''
				dataset_class = param[ind]['dn_mixed_class_name']
				test_set = param[ind]['dn_testing_set_name']
				d+=1
			c+=1
		assert d != 0, "A test dataset was referenced which doesn't exist."
		num_of_train = ''
		year = dataset_dir.split('/')[1]
		dataset = dataset_dir.split('/')[0]
		

		path_to_training_def = path_to_data+dataset_dir+"/"+dataset_class+".data"
		path_to_class_names = path_to_data+dataset_dir+"/"+dataset_class+".names"

		cell_classes = get_class_names(path_to_class_names)
		print('test_set',test_set)
		
		return num_of_train,year,test_set,cell_classes,dataset,path_to_training_def
		
	else:
		print ('dataset not recognised as single dataset or mixed dataset',dataset[0:5],dataset[0:7])
		return False
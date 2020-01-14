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
	
	dk2_model_array =[]
	dk3_model_array =[]
	train_array =[]
	test_array = []
	rep_array = []
	flip_on_array = []
	
	while 1:
		line = f.readline()
		if not line:
			break
		line = line.strip("\n")
		if line[0:13] == "out_file_log=":
			out_file_log = line[13:].strip("\"").strip("\'")
			line = next_line()
		
		if line[0:19] == "darknet_model_init=":
			model_array.append(line[19:])
			line = next_line()
			if line[0:20] == "darknet3_model_init=":
			model_array.append(line[20:])
			line = next_line()
			
			if line[0:17] == "train_on_dataset=":
				train_array.append(line[17:])
			line = next_line()

			if line[0:8] == "flip_on=":

				flip_on_array.append(line[8:].strip("\"").strip("\'"))
			line = next_line()
			temp_test_array = []
			while line[0:22] != "number_of_repetitions=":
				if line[0:16] == "test_on_dataset=":
					temp_test_array.append(line[16:])
				line = next_line()
			test_array.append(temp_test_array)
			if line[0:22] == "number_of_repetitions=":
				rep_array.append(int(line[22:].strip("\"").strip("\'")))
			
			
			if model_array.__len__() == train_array.__len__() == rep_array.__len__() == test_array.__len__():
				
				pass
			else:
				print('failed\n')
				print('One of your datasets was not complete:',model_array.__len__())
				print('Please make sure you have the following structure, e.g:')
				print('darknet_model_init="darknet19_448.conv.23"')
				print('train_on_dataset="dataset01"')
				print('test_on_dataset="mixed01"')
				assert False

	return model_array, train_array, test_array, rep_array, flip_on_array, out_file_log
def load_dataset(path_to_data,path_to_amca_config,dataset):
	
	if dataset[0:8] == '"dataset':
		path_to_spec = path_to_amca_config+"dataset_spec.txt"
		indices, datasets, datasets_size, datasets_class = cvto.return_dataset_spec(path_to_spec) 
		idx = int(dataset[8:].strip("\""))
		print(idx,indices)
		c = 0
		d = 0
		for ind in indices:

			if ind == idx:
				dataset_dir = datasets[c]
				dataset_size = datasets_size[c]
				dataset_class = datasets_class[c]
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
		return num_of_train,year,test_set,cell_classes,dataset,path_to_training_def
		
	elif dataset[0:6] == '"mixed':
		path_to_spec = path_to_amca_config+"mixed_dataset_spec.txt"
		indices, param = cvto.return_mixed_dataset_spec(path_to_spec)
		idx = int(dataset[6:].strip("\""))
		
		
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
		print ('dataset not recognised as single dataset or mixed dataset')
		return False
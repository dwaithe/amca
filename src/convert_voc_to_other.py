import os
import sys
import numpy as np
import os
from numpy.random import RandomState
import os
from shutil import copyfile
def write_xml(xml_path, roi_list, name_of_file, dataset_name, class_name, year, img_width,img_height,sf):
    f = open(xml_path+'/'+str(name_of_file)+".xml" ,'w');
    f.writelines("<annotation>\n");
    f.writelines("\t<folder>"+dataset_name+"</folder>\n")
    f.writelines("\t<filename>"+str(name_of_file)+".jpg</filename>\n")
    f.writelines("\t<source>\n")
    f.writelines("\t\t<database>The "+str(year)+" cell Database</database>\n")
    f.writelines("\t\t<annotation>Waithe "+str(year)+"</annotation>\n")
    f.writelines("\t\t<image>confocal</image>\n")
    f.writelines("\t\t<omeroid></omeroid>\n")
    f.writelines("\t</source>\n")
    f.writelines("\t<owner>\n")
    f.writelines("\t\t<name></name>\n")
    f.writelines("\t</owner>\n")
    f.writelines("\t<size>\n")
    f.writelines("\t\t<width>"+str(img_width)+"</width>\n")
    f.writelines("\t\t<height>"+str(img_height)+"</height>\n")
    f.writelines("\t\t<depth>3</depth>\n")
    f.writelines("\t</size>")
    f.writelines("\t<segmented>0</segmented>\n")
    for roi in roi_list:
        x, y, width, height, roi_class_name = roi
        if roi_class_name in class_name:
            f.writelines("<object>\n")
            f.writelines("<name>"+roi_class_name+"</name>\n")
            f.writelines("<pose>Unspecified</pose>\n")
            f.writelines("<truncated>0</truncated>\n")
            f.writelines("<difficult>0</difficult>\n")
            f.writelines("<bndbox>\n")
            f.writelines("\t\t<xmin>"+str(round(x*sf)+1)+"</xmin>\n")
            f.writelines("\t\t<ymin>"+str(round(y*sf)+1)+"</ymin>\n")
            f.writelines("\t\t<xmax>"+str(round(x*sf+width*sf)+1)+"</xmax>\n")
            f.writelines("\t\t<ymax>"+str(round(y*sf+height*sf)+1)+"</ymax>\n")
            f.writelines("\t</bndbox>\n")
            f.writelines("\t</object>\n")
    f.writelines("</annotation>\n")
    f.close()
def create_retinaNet_single(datasets,datasets_size,path,path_on_server):
    
    
    
    for dataset,dataset_size in zip(datasets,datasets_size):
        
        path_dir = path+dataset
        
        fclasses = open(path_dir+'retina_classes.csv',"w")

        #input data, from PASCAL imageSets
        path_in = path_dir+"ImageSets/Main/"
        directory = path_in
        if not os.path.exists(directory):
            os.makedirs(directory)

        datain =  open(path_in+'train_n'+str(dataset_size[0])+'.txt',"r")
        out_str = ""
        
        #output as csv, in each directory.
        csvfileout = open(path_dir+'retina_train_dn_n'+str(dataset_size[0])+'.csv',"w")
        
        def read_data(datain,csvfileout,fclasses):
            while 1:
                line = datain.readline()
                if not line:
                    break

                file_nm = line[:-1]
                file_path = path+dataset+"Annotations/"+file_nm+'.xml'

                data =  open(file_path,"r")
                out_str = ""
                while 1:
                    line = data.readline()
                    if not line:
                        break
                    if line.find("<name>") >-1:
                        im_class = line.split("<name>")[1].split("</name>")[0]
                    if line.find("<width>") >-1:
                        im_width = float(line.split("<width>")[1].split("</width>")[0])
                    if line.find("height") >-1:
                        im_height = float(line.split("<height>")[1].split("</height>")[0])
                    if line.find("<bndbox>") > -1:
                        xmin_str = data.readline()
                        xmin = int(xmin_str.split("<xmin>")[1].split("</xmin>")[0])
                        ymin_str = data.readline()
                        ymin = int(ymin_str.split("<ymin>")[1].split("</ymin>")[0])
                        xmax_str = data.readline()
                        xmax = int(xmax_str.split("<xmax>")[1].split("</xmax>")[0])
                        ymax_str = data.readline()
                        ymax = int(ymax_str.split("<ymax>")[1].split("</ymax>")[0])

                        out_str += path_on_server+dataset+"JPEGImages/"+file_nm+'.jpg,'
                        out_str += str(xmin-1)+","+str(ymin-1)+","+str(xmax-1)+","+str(ymax-1)+','+im_class+"\n"

                csvfileout.write(out_str)
            fclasses.write(im_class+",0"+'\n');
        read_data(datain,csvfileout,fclasses)
        datain.close()
        fclasses.close()
        csvfileout.close()
        
        
        fclasses = open(path_dir+'retina_classes.csv',"w") #Yes this gets written twice.
        #input data, from PASCAL imageSets
        path_in = path_dir+"ImageSets/Main/"
        datain =  open(path_in+'test_n'+str(dataset_size[1])+'.txt',"r")
        out_str = ""

        #output as csv, in each directory.
        csvfileout = open(path_dir+'retina_test_dn_n'+str(dataset_size[1])+'.csv',"w")
        read_data(datain,csvfileout,fclasses)
        datain.close()
        fclasses.close()
        csvfileout.close()
        
        
def create_retinaNet_global(params,datasets,datasets_size,path,path_on_server):
     ##For the global single channel dataset.
    for ind in params:
        param = params[ind]
        directory = path+param['dataset_path']
        if not os.path.exists(directory):
            os.makedirs(directory)

        fclasses = open(path+param['dataset_path']+'retina_classes.csv',"w")
        #output as csv, in each directory.
        csvfileout_train = open(path+param['dataset_path']+param['rn_training_set_name']+'.csv',"w")
        csvfileout_test = open(path+param['dataset_path']+param['rn_testing_set_name']+'.csv',"w")
        type_of_mixed = param['type']
        c=0
        d=0

        

        for dataset,dataset_size in zip(datasets,datasets_size):

            if c in param['indices_to_use']:
                path_dir = path+dataset



                #input data, from PASCAL imageSets
                path_in = path_dir+"ImageSets/Main/"
                directory = path_in
                if not os.path.exists(directory):
                    os.makedirs(directory)


                datain_train =  open(path_in+'train_n'+str(dataset_size[0])+'.txt',"r")
                out_str1 = ""

                #read_data(datain_train,csvfileout_train,fclasses,d)
                datain_test =  open(path_in+'test_n'+str(dataset_size[1])+'.txt',"r")
                out_str2 = ""
                #read_data(datain_test,csvfileout_test,None,d)
                e = 0
                for out_str, input_file, csv_out in zip([out_str1,out_str2],[datain_train,datain_test],[csvfileout_train,csvfileout_test]):

                        #def read_data(datain,csvfileout,fclasses,d):
                        while 1:
                            line = input_file.readline()
                            if not line:
                                break

                            file_nm = line[:-1]
                            file_path = path+dataset+"Annotations/"+file_nm+'.xml'

                            data =  open(file_path,"r")
                            out_str = ""
                            while 1:
                                line = data.readline()
                                if not line:
                                    break
                                if line.find("<name>") >-1:
                                    im_class = line.split("<name>")[1].split("</name>")[0]
                                if line.find("<width>") >-1:
                                    im_width = float(line.split("<width>")[1].split("</width>")[0])
                                if line.find("height") >-1:
                                    im_height = float(line.split("<height>")[1].split("</height>")[0])
                                if line.find("<bndbox>") > -1:
                                    xmin_str = data.readline()
                                    xmin = int(xmin_str.split("<xmin>")[1].split("</xmin>")[0])
                                    ymin_str = data.readline()
                                    ymin = int(ymin_str.split("<ymin>")[1].split("</ymin>")[0])
                                    xmax_str = data.readline()
                                    xmax = int(xmax_str.split("<xmax>")[1].split("</xmax>")[0])
                                    ymax_str = data.readline()
                                    ymax = int(ymax_str.split("<ymax>")[1].split("</ymax>")[0])

                                    out_str += path_on_server+dataset+"JPEGImages/"+file_nm+'.jpg,'
                                    if type_of_mixed == "hetero":
                                        out_str += str(xmin-1)+","+str(ymin-1)+","+str(xmax-1)+","+str(ymax-1)+','+im_class+"\n"
                                    else:
                                        out_str += str(xmin-1)+","+str(ymin-1)+","+str(xmax-1)+","+str(ymax-1)+",cell - multiple types\n"

                            csv_out.write(out_str)
                        if fclasses !=None:
                            if type_of_mixed == "hetero" and e == 0:
                                fclasses.write(im_class+","+str(d)+'\n');
                            e+=1
                d+=1
            c+=1
        if type_of_mixed == "homo":
            fclasses.write("cell - multiple types,0\n");
        csvfileout_train.close()
        csvfileout_test.close()
        fclasses.close()
        datain_test.close()
        datain_train.close()
def convert_to_yolo_format(xmin,xmax,ymin,ymax,im_height,im_width):
    hei = ymax-ymin
    wid = xmax-xmin
    xcen = (xmin+(wid//2))/im_width
    ycen = (ymin+(hei//2))/im_height
    widc = wid/im_width
    heic = hei/im_height
    return np.round(xcen,12), np.round(ycen,12), np.round(widc,12), np.round(heic,12)

#Generates Global lists.
def generate_global_list(number_to_include, directory,outF1,outF2):
    store_lines = []
    for file in os.listdir(directory+"/Annotations"):
        if file.endswith(".xml"):
            store_lines.append(str(file[:-4]))
    
    np.random.seed(seed=500)
    if np.sum(number_to_include) > store_lines.__len__():
        print(np.sum(number_to_include), store_lines.__len__())
        print('error the number to include exceeds total files present:' )
        print(directory)
        return
   

    indices_to_use = np.random.choice(np.arange(0,store_lines.__len__()), size=store_lines.__len__(), replace=False)
    training_list = np.sort(indices_to_use[:number_to_include[0]])
    test_list = np.sort(indices_to_use[-number_to_include[1]:])
    
    store_lines = np.array(store_lines)
    textList = list(map(lambda x: x, store_lines[training_list]))
    outF1.writelines("%s\n" % l for l in textList)
    
    textList = list(map(lambda x: x, store_lines[test_list]))
    outF2.writelines("%s\n" % l for l in textList)
    
    print("train_n"+str(int(number_to_include[0]))+".txt")
    print("test_n"+str(int(number_to_include[1]))+".txt")


def generate_random_list(number_to_include, directory):
    store_lines = []
    for file in os.listdir(directory+"/Annotations"):
        if file.endswith(".xml"):
            store_lines.append(str(file[:-4]))
    
    np.random.seed(seed=500)
    if np.sum(number_to_include) > store_lines.__len__():
        print(np.sum(number_to_include), store_lines.__len__())
        print('error the number to include exceeds total files present:' )
        print(directory)
        return
   

    indices_to_use = np.random.choice(np.arange(0,store_lines.__len__()), size=store_lines.__len__(), replace=False)
    training_list = np.sort(indices_to_use[:number_to_include[0]])
    test_list = np.sort(indices_to_use[-number_to_include[1]:])
    
    
    if not os.path.exists(directory+"ImageSets/Main/"):
                os.makedirs(directory+"ImageSets/Main/")
    
    outF = open(directory+"ImageSets/Main/"+"train_n"+str(int(number_to_include[0]))+".txt", "w")
    store_lines = np.array(store_lines)
    textList = list(map(lambda x: x, store_lines[training_list]))
    outF.writelines("%s\n" % l for l in textList)
    outF.close()

    outF = open(directory+"ImageSets/Main/"+"test_n"+str(int(number_to_include[1]))+".txt", "w")
    textList = list(map(lambda x: x, store_lines[test_list]))
    outF.writelines("%s\n" % l for l in textList)
    outF.close()
    print("train_n"+str(int(number_to_include[0]))+".txt")
    print("test_n"+str(int(number_to_include[1]))+".txt")
    print("written to directory:", directory+"ImageSets/Main/")
def create_YOLO_single(datasets,datasets_size,datasets_class,path,path_on_server,backup_path):

    #This Reads the Pascal format and converts to label format for YOLO. This is the default format, which I start from.
    for dataset in datasets:
        print(dataset)

        for file_nm in os.listdir(path+dataset+'Annotations/'):
            if file_nm.endswith(".xml"):       
                data =  open(path+dataset+'Annotations/'+file_nm,"r")
                out_str = ""
                while 1:
                    line = data.readline()
                    if not line:
                        break
                    if line.find("<name>") >-1:
                        im_class =  line.split("<name>")[1].split("</name>")[0]
                    if line.find("<width>") >-1:
                        im_width =  float(line.split("<width>")[1].split("</width>")[0])
                    if line.find("height") >-1:
                        im_height =  float(line.split("<height>")[1].split("</height>")[0])
                    if line.find("<bndbox>") > -1:
                        xmin_str = data.readline()
                        xmin = float(xmin_str.split("<xmin>")[1].split("</xmin>")[0])
                        ymin_str = data.readline()
                        ymin = float(ymin_str.split("<ymin>")[1].split("</ymin>")[0])
                        xmax_str = data.readline()
                        xmax = float(xmax_str.split("<xmax>")[1].split("</xmax>")[0])
                        ymax_str = data.readline()
                        ymax = float(ymax_str.split("<ymax>")[1].split("</ymax>")[0])


                        xcen, ycen, widc, heic = convert_to_yolo_format(xmin,xmax,ymin,ymax,im_height,im_width)
                        out_str +=  str(0)+" "+str(xcen)+" "+str(ycen)+" "+str(widc)+" "+str(heic)+"\n"

                f = open(path+dataset+'labels/'+file_nm[:-4]+'.txt',"w")
                f.write(out_str)
                f.close()
                data.close()

    for dataset,dataset_size in zip(datasets,datasets_size):

            path_dir = path+dataset
            f = open(path_dir+'train_dn_n'+str(dataset_size[0])+'.txt',"w")
            path_in = path_dir+"ImageSets/Main/"
            data =  open(path_in+'train_n'+str(dataset_size[0])+'.txt',"r")
            out_str = ""

            while 1:
                line = data.readline()
                if not line:
                    break
                f.write(path_on_server+dataset+"JPEGImages/"+line[:-1]+'.jpg\n')
            f.close()
            data.close()

            path_dir = path+dataset
            f = open(path_dir+'test_dn_n'+str(dataset_size[1])+'.txt',"w")
            path_in = path_dir+"ImageSets/Main/"
            data =  open(path_in+'test_n'+str(dataset_size[1])+'.txt',"r")
            out_str = ""

            while 1:
                line = data.readline()
                if not line:
                    break
                f.write(path_on_server+dataset+"JPEGImages/"+line[:-1]+'.jpg\n')
            f.close()
            data.close()


    for dataset,dataset_size,dataset_class in zip(datasets,datasets_size,datasets_class):
        path_dir = path+dataset
        print (dataset)
        f = open(path_dir+'obj_'+str(dataset.split("/")[0])+str(dataset_size[0])+'.data',"w")
        f.write("classes = 1\n")
        f.write("train = "+path_on_server+dataset+'train_dn_n'+str(dataset_size[0])+'.txt'+"\n")
        f.write("valid = "+path_on_server+dataset+'test_dn_n'+str(dataset_size[1])+'.txt'+"\n")
        f.write("names = "+path_on_server+dataset+'obj_'+str(dataset.split("/")[0])+'.names'+"\n")
        f.write("backup = "+backup_path+'darknet/'+str(dataset.split("/")[0])+str(dataset_size[0])+"\n")
        f.close()

        f = open(path_dir+'obj_'+str(dataset.split("/")[0])+'.names',"w")
        f.write(dataset_class+"\n")
        f.close()
def create_FasterRCNN_mixed_dataset(params, datasets,datasets_size,datasets_class,path,path_on_server,backup_path):


    for ind in params:
        param = params[ind]
        global_path = param['dataset_path']
        indices_to_use = param['indices_to_use']
        global_test_name = param['dn_mixed_class_name']
        training_set_name = param['dn_training_set_name']
        testing_set_name = param['dn_testing_set_name']
        type_of_mixed = param['type']
        
    



        glb_datasets = []
        glb_datasets_size = []
        glb_datasets_class = []
        for index_to_use in indices_to_use:
            glb_datasets.append(datasets[index_to_use]) 
            glb_datasets_size.append(datasets_size[index_to_use])
            glb_datasets_class.append(datasets_class[index_to_use])
        directory = (path+global_path+"ImageSets/Main/")

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = (path+global_path+"JPEGImages/")
        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = (path+global_path+"Annotations/")
        if not os.path.exists(directory):
            os.makedirs(directory)

        

        outF1 = open(path+global_path+"ImageSets/Main/"+"train_n.txt", "w")
        outF2 = open(path+global_path+"ImageSets/Main/"+"test_n.txt", "w")
        for dataset,dataset_size in zip(glb_datasets,glb_datasets_size):
            path_dir = path+dataset
            inftr = open(path_dir+"ImageSets/Main/"+'train_n'+str(dataset_size[0])+'.txt',"r")
            infte = open(path_dir+"ImageSets/Main/"+'test_n'+str(dataset_size[1])+'.txt',"r")

            ab = inftr.readlines()
            outF1.writelines(ab)
            ab = infte.readlines()
            outF2.writelines(ab)
        outF1.close()
        outF2.close()


        
        for dataset,dataset_size in zip(glb_datasets,glb_datasets_size):
            path_dir = path+dataset
            path_in = path_dir+"ImageSets/Main/"    
            data1 = open(path_in+"train_n"+str(int(dataset_size[0]))+".txt","r")
            data2 = open(path_in+"test_n"+str(int(dataset_size[1]))+".txt","r")

            for data in [data1,data2]:
                while 1:
                    line = data.readline()
                    if not line:
                        break
                
                    src = path_dir+ "JPEGImages/"+line[:-1]+'.jpg'
                    dst = path+global_path+"JPEGImages/"+line[:-1]+'.jpg'
                    copyfile(src, dst)
                    src = path_dir+ "Annotations/"+line[:-1]+'.xml'
                    dst = path+global_path+"Annotations/"+line[:-1]+'.xml'
                    copyfile(src, dst)
                    if type_of_mixed == "homo":
                        xml_data =  open(dst,"r")
                        out_str = ""
                        while 1:
                            line_xml = xml_data.readline()
                            if not line_xml:
                                break
                            if line_xml.find("<name>") >-1:
                                preline = line_xml.split("<name>")[0]
                                postline = line_xml.split("</name>")[1]
                                line_xml = preline+"<name>cell - multiple types</name>"+postline
                            out_str += line_xml
                        xml_data.close()
                        xml_data = open(dst,"w")
                        xml_data.writelines(out_str)  
                        xml_data.close()                  

     

def create_YOLO_mixed_hetero_class(params, datasets,datasets_size,datasets_class,path,path_on_server,backup_path):
    """ Generate global list
        This is where we generate the ImageSets for the YOLO algorithm, from those defined for the Faster-RCNN.
        A global list is a list of images which encompasses multiple different classes."""
    for ind in params:
        param = params[ind]
        global_path = param['dataset_path']
        indices_to_use = param['indices_to_use']
        global_test_name = param['dn_mixed_class_name']
        training_set_name = param['dn_training_set_name']
        testing_set_name = param['dn_testing_set_name']
        type_of_mixed = param['type']
        
    



        glb_datasets = []
        glb_datasets_size = []
        glb_datasets_class = []
        for index_to_use in indices_to_use:
            glb_datasets.append(datasets[index_to_use]) 
            glb_datasets_size.append(datasets_size[index_to_use])
            glb_datasets_class.append(datasets_class[index_to_use])
        

        directory = (path+global_path+"labels")
        if not os.path.exists(directory):
            os.makedirs(directory)

        


        f1 =  open(path+global_path+training_set_name+'.txt',"w")
        f2 =  open(path+global_path+testing_set_name+'.txt',"w")

        label_count = 0
        for dataset,dataset_size in zip(glb_datasets,glb_datasets_size):
            path_dir = path+dataset
            path_in = path_dir+"ImageSets/Main/"    
            data1 = open(path_in+"train_n"+str(int(dataset_size[0]))+".txt","r")
            data2 = open(path_in+"test_n"+str(int(dataset_size[1]))+".txt","r")

            for data,f in zip([data1,data2],[f1,f2]):
                while 1:
                    line = data.readline()
                    if not line:
                        break
                    f.write(path_on_server+global_path+"JPEGImages/"+line[:-1]+'.jpg\n')
                                        
                    src = path_dir+ "labels/"+line[:-1]+'.txt'
                    dst = path+global_path+"labels/"+line[:-1]+'.txt'
                   
                    
                    label1 =  open(src,"r")
                    label2 =  open(dst,"w")
                    while 1:
                        label_line = label1.readline()
                        if not label_line:
                            break
                        labels_ = label_line.split(" ")
                        labels_[0] = str(label_count)
                        out_label = " ".join(labels_)
                        label2.write(out_label)
                    label1.close()
                    label2.close()

            if type_of_mixed == "hetero":
                label_count +=1                        




        f1.close()
        data1.close()
        f2.close()
        data2.close()

        f = open(path+global_path+global_test_name+'.data',"w")
        f1 = open(path+global_path+global_test_name+'.names',"w")
        c = 0

        
        if type_of_mixed == "hetero":
            for dataset,dataset_size,dataset_class in zip(glb_datasets,glb_datasets_size,glb_datasets_class):
                path_dir = path+dataset
                c+=1
                f1.write(dataset_class+"\n")
            f.write("classes = "+str(c)+"\n")
        else:
            f1.write("cell - multiple types"+"\n")
            f.write("classes = "+str(1)+"\n")
        f.write("train = "+path_on_server+global_path+training_set_name+'.txt'+"\n")
        f.write("valid = "+path_on_server+global_path+testing_set_name+'.txt'+"\n")
        f.write("names = "+path_on_server+global_path+global_test_name+'.names'+"\n")
        f.write("backup = "+backup_path+'darknet/'+global_path.split("/")[0]+'/')

        f.close()


def return_dataset_spec(path_to_spec):
    """opens spec file and returns contents as arrays"""
    f = open(path_to_spec,"r")
    indices = []
    datasets = []
    datasets_size = []
    datasets_class = []
    def next_line():
        line = f.readline().strip("\n")
        while line == '':
                line = f.readline().strip("\n")
        if '#' in line:
            line = line.split('#')[0]
        return line


    while 1:
        line = f.readline()
        if not line:
            break
        line = line.strip("\n")
        #print(line)
        if line[0:8] == "dataset=":
            indices.append(int(line[8:]))

            line = next_line()

            if line[0:4]=="dir=":
                datasets.append(str(line[4:].strip("\"")))

            line = next_line()


            if line[0:16]=="training_images=":
                training_images = int(line[16:])

            line = next_line()

            if line[0:15]=="testing_images=":
                testing_images = int(line[15:])
                datasets_size.append([training_images,testing_images])

            line = next_line()


            if line[0:11]=="cell_class=":
                datasets_class.append(line[11:].strip('"'))
                

            #check:
            if indices.__len__() == datasets.__len__() == datasets_class.__len__() == datasets_size.__len__():
                if np.unique(indices).shape[0] != indices.__len__(): 
                    print('not unique')
                    print("Your dataset ids are not unique e.g.(0,1,2,3,4), you have repetition.")
                    return False, False, False, False

            else:
                print('failed\n')
                print('One of your datasets was not complete:',indices.__len__())
                print('Please make sure you have the following structure, e.g:')
                #Erythroblast dapi glycophorinA, full data:
                print('dataset=9')
                print('dir="erythroblast_dapi_glycophorinA_class/2018/"')
                print('training_images=80')
                print('testing_images=80')
                print('cell_class="cell - erythroblast dapi glycophorinA"')
                return False, False, False, False
                break



    for i,c in enumerate(datasets):
        print('index:',i,'dataset',c)
    
    return indices, datasets, datasets_size, datasets_class
def return_mixed_dataset_spec(path_to_spec):
    f = open(path_to_spec,"r")
    indices = []
    params = {}
    def next_line():
        line = f.readline().strip("\n")
        while line == '':
                line = f.readline().strip("\n")
        if '#' in line:
            line = line.split('#')[0]
        return line
    while 1:
        line = f.readline()
        if not line:
            break
        line = line.strip("\n")
        #print(line)
        if line[0:14] == "mixed_dataset=":
            indices.append(int(line[14:]))
            param = {}
            line = next_line()
           
            if line[0:4]=="dir=":
                param['dataset_path'] = str(line[4:].strip("\""))
            line = next_line()
            
            val = "type="
            if line[0:val.__len__()]==val:
                param[val.strip("=")] = line[val.__len__():].strip('\"').strip('\'')
            line = next_line()

            val = "indices_to_use="
            if line[0:val.__len__()]==val:
                param['indices_to_use'] = np.array(line[val.__len__():].strip('\"').split(',')).astype(np.int)
            
            line = next_line()
            val = "dn_mixed_class_name="
            if line[0:val.__len__()]==val:
                param[val.strip("=")] = line[val.__len__():].strip('\"')
                
            line = next_line()
            val = "dn_training_set_name="
            if line[0:val.__len__()]==val:
                param[val.strip("=")] = line[val.__len__():].strip('\"')
            
            line = next_line()
            val = "dn_testing_set_name="
            if line[0:val.__len__()]==val:
                param[val.strip("=")] = line[val.__len__():].strip('\"')
            
            line = next_line()
            val = "rn_training_set_name="
            if line[0:val.__len__()]==val:
                param[val.strip("=")] = line[val.__len__():].strip('\"')
            
            line = next_line()
            val = "rn_testing_set_name="
            if line[0:val.__len__()]==val:
                param[val.strip("=")] = line[val.__len__():].strip('\"')
            
            params[indices[-1]] = param
            if param.__len__() != 8:
                
                print('fail. One of your param entries is not complete: mixed dataset',indices[-1])
                return False,False;
            
    return indices,params


import tifffile as tifffile
import numpy as np
import os

def read_meta_data_from_micro_manager_stack(path):
    """
    Retrieves stage coordinates from micromanager tiff stack file.
    The metadata is embedded in the file.
    
    input:
    ---------------
    path - the path to the MicroManager metadata.txt file.
    
    
    output:
    ---------------
    xpos - an array of the stage x position (um).
    ypos - an array of the stage y position (um).
    zpos - an array of the stage z position (um)."""
    
    
    zpos = []
    xpos = []
    ypos = []
    with tifffile.TiffFile(path) as tif:
        
        for page in tif.pages:
            for tag in page.tags.values():
                content = tag.name, tag.value
                if content[0] == 'image_description':
                    
                    conten = content[1].decode()
                    for sect in conten.split(' '):
                        if "slices=" in sect:
                            for itm in sect.split("\n"):
                                if "slices" in itm:
                                    number_of_images = int(itm.strip("slices="))
                        if "PositionX=" in sect:
                            XPositionUm = float(sect.strip( " \"PositionX=").strip(",\n"))
                            xpos.append(XPositionUm)
                        if "PositionY=" in sect:   
                            YPositionUm = float(sect.strip( " \"PositionY=").strip(",\n"))
                            ypos.append(YPositionUm)
                        if "PositionZ=" in sect:   
                            ZPositionUm = float(sect.strip( " \"PositionZ=").strip(",\n"))
                            zpos.append(ZPositionUm)
             
            
            
    return xpos, ypos, zpos, number_of_images

def read_meta_data_from_micro_manager(path):
    """
    Retrieves stage coordinates from micromanager metadata.txt file.
    N.B. The metadata.txt is created when a stack of images from Micromanager is exported as single files.
    
    input:
    ---------------
    path - the path to the MicroManager metadata.txt file.
    
    
    output:
    ---------------
    xpos - an array of the stage x position (um).
    ypos - an array of the stage y position (um).
    zpos - an array of the stage z position (um).
    
    """
    zpos = []
    xpos = []
    ypos = []
    with open(path,'r') as f:
        content = f.readlines()
        for sect in content:
            if "\"Slices\"" in sect:
                number_of_images = int(sect.strip( " \"Slices\":").strip(",\n"))
            if "XPositionUm" in sect:   
                XPositionUm = float(sect.strip( " \"XPositionUm\":").strip(",\n"))
                xpos.append(XPositionUm)
            if "YPositionUm" in sect:   
                YPositionUm = float(sect.strip( " \"YPositionUm\":").strip(",\n"))
                ypos.append(YPositionUm)
            if "ZPositionUm" in sect:   
                ZPositionUm = float(sect.strip( " \"ZPositionUm\":").strip(",\n"))
                zpos.append(ZPositionUm)
            
            
    return xpos, ypos, zpos, number_of_images



def convert_Faster_RCNN_output(path,class_filter=False):
    """
    Converts a Faster-RCNN text output file to det.txt format.
    
    input:
    ---------------
    path - the path to the the file
    class_filter - filters the output to a particular class, default = False (no filtering)
    
    output:
    ---------------
    p - an array of the probabilites for each detected cell.
    c - an array of the coordinates for each detected cell. Each entry [x0,y0,x1,y1]
    d - an array of the class names for each cell detection.
    
    """
    
    c = []
    p = []
    d = []
    with open(path,'r') as f:
        content = f.readlines()
        if content != []:
            for itc in content:
            
                trct = itc.strip("\n").split("\t")
                if trct[0] == class_filter:
                    c.append(np.array(trct[2:6]).astype(np.float64))
                    p.append(float(trct[1]))
                    d.append(trct[0])
                elif class_filter == False:
                    c.append(np.array(trct[2:6]).astype(np.float64))
                    p.append(float(trct[1]))
                    d.append(trct[0])
                    
    
    
    return p, c, d

def register_new_img(dz,stack,d4,zp0):
    """


    """
    d_z[d4][zp0] ={}
    d_z[d4][zp0]['fieldx'] = xp0
    d_z[d4][zp0]['fieldy'] = yp0
    d_z[d4][zp0]['cellx'] = int(d[1])
    d_z[d4][zp0]['celly'] = int(d[0])
    d_z[d4][zp0]['im'] = im[int(d[1]):int(d[3]),int(d[0]):int(d[2])]
    orix = d_z[d4]['ori']['orix']
    oriy = d_z[d4]['ori']['oriy']
    oriz = d_z[d4]['ori']['oriz']

    out = d_z[d4][zp0]['im']
    stack[d4] = tifffile.TiffWriter('Stack'+str(d4)+"_"+str(d[-1])+"_"+str(int(d[0]+xp0-orix))+"_"+str(int(d[1]+yp0-oriy))+'.tif')  
    stack[d4].save(out)
    #If this is a new id.  


def sort_imgs_into_stacks(input_raw_folder,output_stacks_folder):
    """
    Assembles the individual images into corrected stacks.
    The files have to be prefixed with "Stack".
    If they are not or if misc files have this name, bad things will happen.

    inputs:
    -------------------------
    input_raw_folder			- path to folder containing the images.
    output_stacks_folder        - where the output stacks will be saved.

    returns:
    -------------------------
    Nothing, but will output complete stacks into folder specified by output_stacks_folder

    """

    files = os.listdir(input_raw_folder) #Finds all files in the directory specified.
    

    names = {}
    for file in files:
        txts = file.split("_")
        if txts[0][:5] == "Stack": 
            num = txts[0][5:]
            if num in names:
                names[num].append([float(txts[1]),file])
            else:
                names[num] = []
                names[num].append([float(txts[1]),file])
    for num in names:
        names[num] = sorted(names[num],key=takeFirst)

    process_imgs(input_raw_folder,output_stacks_folder,names)

def takeFirst(elem):
    return elem[0]

def read_img(path_to_file):
    return tifffile.imread(path_to_file)


def process_imgs(input_raw_folder,output_stacks_folder,names):
    """ """
    for num in names:
        img_stk = {}
        for idz,file in names[num]:
            path_to_file = input_raw_folder + file
            txts = file.split("_")
            img = read_img(path_to_file)
            if img.shape.__len__() >1:
                img_stk[txts[1]] = {'img':img,'file_name':file}
            else:
                img_stk[txts[1]] = {'img':np.zeros((25,25)),'file_name':file}
            #tif_stack.save(img)
            
        img_stk = correct_offset(*calculate_offset(img_stk))
        save_stks(output_stacks_folder,names[num],num,img_stk)

def save_stks(output_stacks_folder,names_array,num,img_stk):
    """


    """
    tif_stack = tifffile.TiffWriter(output_stacks_folder+"Stack"+num+".tif",imagej=True)
    out_img = []
    for idz,file in names_array:
        #print file
        txts = file.split("_")
        out_img.append(img_stk[txts[1]]['out_img'].astype(np.float32))
    if out_img != []:
        tif_stack.save(np.array(out_img).astype(np.float32))

def calculate_offset(img_stk):
    max_wid = 0
    max_hei = 0
    mx_corr_x = 99999999
    mx_corr_y = 99999999
    for zsl in img_stk:
        sz = img_stk[zsl]['img'].shape
        
        img_stk[zsl]['hei'] = sz[0]
        img_stk[zsl]['wid'] = sz[1]
        txts = img_stk[zsl]['file_name'].split("_")
        corr_x = float(txts[2])
        corr_y = float(txts[3].split(".")[0])
        img_stk[zsl]['corr_x'] = corr_x
        img_stk[zsl]['corr_y'] = corr_y
        full_wid = corr_x+sz[1]
        full_hei = corr_y+sz[0]
        if max_wid < full_wid: max_wid = full_wid
        if max_hei < full_hei: max_hei = full_hei
        if mx_corr_x > corr_x: mx_corr_x = corr_x
        if mx_corr_y > corr_y: mx_corr_y = corr_y


        
    return img_stk, max_hei, max_wid, mx_corr_x, mx_corr_y

def correct_offset(img_stk, max_hei, max_wid, mx_corr_x, mx_corr_y):
    for zsl in img_stk:
        img = img_stk[zsl]['img']
        hei = img_stk[zsl]['hei']
        wid = img_stk[zsl]['wid']
        corr_x = img_stk[zsl]['corr_x']
        corr_y = img_stk[zsl]['corr_y']
        out_img = np.zeros((int(-mx_corr_y+max_hei),int(-mx_corr_x+max_wid)))
        y0 = -mx_corr_y+corr_y
        y1 = -mx_corr_y+corr_y+hei
        x0 = -mx_corr_x+corr_x
        x1 = -mx_corr_x+corr_x+wid
        out_img[int(y0):int(y1),int(x0):int(x1)] = img[:,:]
        img_stk[zsl]['out_img'] = out_img
    return img_stk



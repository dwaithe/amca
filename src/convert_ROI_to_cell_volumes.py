
import numpy as np
import det_sort as ds
import sys
from ijroi.ij_roi import Roi
from ijroi.ijpython_encoder import encode_ij_roi,RGB_encoder
from ijroi.ijpython_decoder import decode_ij_roi
import tifffile
import matplotlib.pylab as plt
import glob
import pyperclip

class ConvertROItoCellVolumes():
    def __init__(self,img_width, img_height, border_offset, scale, zspacing, filepath, outpath):
        """
        The goal of this class is to provide a framework which allows detected cell regions in 
        individual image slices to be connected up through 'z' to yield cell volumes.
        Tiff stacks, if supplied, can also be appended with the overlays that represent the 
        detected volumes. In addition, this class can also be used to sample individual TIFF files
        to make measurements specific to the cell volumes.
        
        The AMCA system will export several files that are needed by this class:
        
        POS_FILE.txt           -- This is original point list which the microscope visited.
        file_pos_export.txt    -- This is a file which documents all the 2-D detected regions
                                  at different z-points.
        
        These two files should be placed in a folder and referenced with the below 'filepath' variable. If
        annotation of TIFF files from the microscope are also required these should be placed in a subfolder 
        named 'images'.
        
        
        -----------------------------
        INPUTS:
        img_width     -- Width of input images
        img_height    -- Height of input images
        border_offset -- pixels to ignore around the perimeter of the image
        scale         -- The xy pixel size in um (e.g. 0.25 um)
        zspacing      -- The z-step between slices. (e.g. 0.5 um)
        filepath      -- The input directory containing the files to be annotated
        
        -----------------------------
        OUTPUTS:
        connected_pos_exp.txt  -- This is file exported with all the 2-D detected regions annotated with their
                                  associated volume id. The regions are corrected to be a consistent width and 
                                  height within each volume.
        "Annotated tiffs"      -- Files which have been annotated with the detected volume regions.
        "Data from regions"    -- This represents measurements made on the cellular volumes and can be exported
                                  in multiple different forms.
        
        """
        
        
        self.img_width = img_width
        self.img_height = img_height
        self.border_offset = border_offset
        self.scale = scale
        self.zspacing = zspacing
        self.filepath = filepath
        
        self.subfolder_for_images = "images/" #The subfolder within the filepath.
        self.POS_FILE_NAME = "POS_FILE.txt"
        self.INPUT_PRED_FILE = "file_pos_export.txt"
        self.OUTPUT_PRED_FILE = 'connected_pos_exp.txt'
        
        #Initialisation commands:
        self.x_unq, self.y_unq, self.z_unq, self.ref_loc, self.trk_mat = self.establish_coordinates()
        self.final_out = self.connect_tracks()
        
        
       

    def establish_coordinates(self):
        """This function reads and interprets the microscope position file and
        also the exported measurement file. The microscope position file ('POS_FILE.txt')
        yields the x and y coordinates for the stage. The exported measurement file ('file_pos_export.txt') 
        gives the Z-range acquired in each location, and the number of slices.
        The two files should be positioned in the folder pointed to by 'self.filepath' variable.
        
        OUTPUT:
        x_unq        - A list of unique 'x' positions where the microscope has visited. 
        y_unq        - A list of unique 'y' positions where the microscope has visited.
        z_unq        - A list of unique 'z' positions where the microscope has visited.
        ref_loc      - A dictionary of positions and there corresponding Z-ranges
        trk_mat      - A matrix of bounding boxes coords acquired during the experiment
        """
        file_name = self.filepath+self.INPUT_PRED_FILE
        
        
        num_lines = 0
        file = open(file_name,"r")
        
        lines_to_keep = []
        for line in file:
            line = line.strip('\n')
            items = line.split(",")
            #print(items)
            if items.__len__()<8:
                print('line',num_lines,'excluded as was not complete.')
                break;
            line = []
            for i in range(0,8):
                 line.append(np.float(items[i]))
            lines_to_keep.append(line)
            num_lines += 1
        
        trk_mat = np.zeros((9,num_lines)).astype(np.float64)
        for c,line in enumerate(lines_to_keep):
            for i in range(0,8):
                trk_mat[i,c] = np.float(line[i])
            trk_mat[8,c] = -1
        

        #We find only save regions and exclude the rest.

        ref_loc = {}

        #This is the unique values from an array.
        x_unq = np.unique(trk_mat[0,:])
        y_unq = np.unique(trk_mat[1,:])
        z_unq = np.unique(trk_mat[2,:])
        
        #Scans all positions and finds size of tiff files.
        for y_pos in y_unq:
            for x_pos in x_unq:
                bint = np.where(trk_mat[0,:] ==x_pos)[0]
                cint = np.where(trk_mat[1,bint] ==y_pos)[0]
                zval = trk_mat[2,bint[cint]]
                if zval.__len__() >0:
                    nmin = np.round(np.min(zval),2)
                    nmax = np.round(np.max(zval),2)
                    ref_loc[str(x_pos)+'_'+str(y_pos)] = [nmin,nmax,int(((nmax-nmin)/self.zspacing)+1),0]
        file.close()
        ##In the position file            
        #file_name = self.filepath+self.POS_FILE_NAME
        #file = open(file_name,"r")


        #for line in file:
        #    coord = line.strip('\n').split('\t')
        #    if coord[0]+'_'+coord[1] in ref_loc:
        #        ref_loc[coord[0]+'_'+coord[1]].append(np.round(float(coord[2]),2))
        #file.close()
        return x_unq, y_unq, z_unq, ref_loc, trk_mat
    
    
    def create_neighbour_directory(self):
        """This function is no longer used."""
    
        def rtn_comp(ax, alt, aht, bx, blt, bht):#, cx, clt, cht):
            return (ax > alt ) & (ax < aht)	& (bx > blt ) & (bx < bht )# & (cx > clt ) & (cx < cht )
        def rtn_hyp(ax0,ax1,bx0,bx1,xy_dist):
            return sqrt((ax0-ax1)**2 + (bx0-bx1)**2)<xy_dist
        
        xy_dist = 101 #um
        coord = {} 

        #Populate a list of all possible coordinate neighbours within threshold.
        for xk0 in self.x_unq:
            for yk0 in self.y_unq:
                ent  =str(xk0)+'_'+str(yk0)

                coord[ent] = []


                for xk1 in xuni:
                    for yk1 in yuni:
                        #if xk0 != xk1 or yk0 != yk1:
                            hit = rtn_comp(xk0,xk1,xk1+xy_dist//2,yk0,yk1,yk1+xy_dist+xy_dist//2)
                            #hit = rtn_hyp(xk0,xk1,yk0,yk1,xy_dist)
                            if hit == True:
                                coord[ent].append([xk1,yk1]) 

        return coord  
    def return_neighbours(self,coord,x,y):
        return coord[str(x)+"_"+str(y)]
    
    
    def connect_tracks(self):
        """This is the workflow for finding the tracks."""

        first_glance = []
        trs = self.trk_mat

        #for c in range(0,trs.shape[1]):
        a1 = (self.img_width*self.scale - trs[3,:]) - trs[5,:]
        x1 = a1 + trs[0,:] 
        b1 = trs[4,:]
        y1 = b1 + trs[1,:] 

        x2 = x1+(trs[5,:])
        a2 = a1+(trs[5,:])
        y2 = y1+(trs[6,:])
        b2 = b1+(trs[6,:])

        #Filter away regions near edge of image.
        boolind = (a1/self.scale > self.border_offset) & (a2/self.scale < (self.img_width-self.border_offset)) & (b1/self.scale > self.border_offset) & (b2/self.scale < (self.img_width-self.border_offset))

        up = boolind
        dn = (1-boolind).astype(np.bool)
        self.trk_mat = self.trk_mat[:,up]
        
        #coord = self.create_neighbour_directory()#Find neighbouring regions.


        in_results = []
        out_results = []
        for stg_x in self.x_unq:
            for stg_y in self.y_unq:
                ind = ((self.trk_mat[0,:] == float(stg_x)) & (self.trk_mat[1,:] == float(stg_y)))
                trks = self.trk_mat[:,ind]
                mot_tracker = []
                mot_tracker = ds.Sort(max_age=100,min_hits=0)

                trackers = None
                for z in self.z_unq:
                    ind = np.where(trks[2,:] == z)[0]
                    trs = trks[:,ind]

                    dets = []
                    for c in range(0,trs.shape[1]):
                        x1 = trs[0,c] + (self.img_width*self.scale - trs[3,c]) - trs[5,c]
                        y1 = trs[1,c] + trs[4,c]
                        z = float(trs[2,c])
                       
                        x2 = x1+(trs[5,c])
                        y2 = y1+(trs[6,c])
                        detstxt = np.array([x1,y1,x2,y2]).astype(np.float64)
                        dets.append(detstxt)
                        in_results.append(detstxt)
                    if dets.__len__() == 0 or dets[0].__len__() >0:
                        trackers = mot_tracker.update(np.array(dets))
                    trackers_wz = []
                    for track in trackers:
                        trackers_wz.append(np.append(track.astype(np.float64),[stg_x,stg_y,z]))
                    out_results.extend(trackers_wz)
                    #roiX0,roiY0,roiX1,roiY1,uniqueID,stagex,stagey,stagez

        out_results = np.array(out_results)

        #Correct regions to be same size.
        ids = np.unique(out_results[:,4])
        out_out =[]
        for idt in ids:
            idx = np.where(out_results[:,4] == idt)
            if idx[0].shape[0] >2:

                out_results[idx,0] = np.average(out_results[idx,0])
                out_results[idx,1] = np.average(out_results[idx,1])
                out_results[idx,2] = np.average(out_results[idx,2])
                out_results[idx,3] = np.average(out_results[idx,3])
                for idx0 in idx[0]:
                    out_out.append(out_results[idx0,:])
        
        final_out = np.array(out_out).T
        
        with open(self.filepath+self.OUTPUT_PRED_FILE, 'w') as the_file:
            out_str =""
            for outline in out_out:
                newline = np.array2string(outline.astype(np.float64), precision=2, separator=',', suppress_small=True, max_line_width=1000000)
                out_str += newline[1:-1] +'\n'
                
            the_file.write(out_str)
        return final_out
    def append_new_regions(self, outpath, extend_roi=True):
        """Function which will take images and append ROI as overlays to them.
        outpath       -- The output directory for images with annotation, can be same as input to save space.
        
        If extend_roi=True then any overlays present will be added to the existing ones.
        If extend_roi=False then any overlays present in the file will be replaced by the old ones.
        """
        for stg_x in self.x_unq:
            for stg_y in self.y_unq:
                pathname2 ="img_stk_x_"+str(stg_x)+"y_"+str(stg_y)+"t_0021.tif"
                input_file = self.filepath+self.subfolder_for_images+pathname2



                output_file = outpath+pathname2
                #for ref in ref_loc:
                if str(stg_x)+'_'+str(stg_y) in self.ref_loc:
                    
        
                    tfile = tifffile.TiffFile(input_file)

                    slices = self.ref_loc[str(stg_x)+'_'+str(stg_y)] 
                    #Short lists all of the regions in an image.
                    ind = ((self.final_out[5,:] == float(stg_x)) & (self.final_out[6,:] == float(stg_y)))
                    trks = self.final_out[:,ind]
                    data = []

                    #Get existing metadata
                    metadata = tfile.imagej_metadata
                    #Get existing image-data.
                    
                    im_stk = tfile.asarray()
                    

                    


                    #Run through each region in the image.
                    for trk in range(0,trks.shape[1]):

                        trkv = trks[:,trk]
                        x0 = (trkv[0]-trkv[5])
                       
                        y0 = (trkv[1]-trkv[6])

                        wid = (trkv[2]-trkv[5])-x0
                        hei = (trkv[3]-trkv[6])-y0


                        #Inititate each region.
                        roi_b = Roi(self.img_width-(x0/self.scale)-(wid/self.scale),y0/self.scale, hei/self.scale, wid/self.scale, self.img_height, self.img_width,0)
                        roi_b.name = "Region-"+str(int(trkv[4]))
                        roi_b.roiType = 1
                        
                        #Find which slice the location refers to.
                        
                        slices = self.ref_loc[str(trkv[5])+'_'+str(trkv[6])]
                       
                        ranget = list(np.round(np.arange(slices[0],slices[1]+self.zspacing,self.zspacing),2))

                        
                        roi_b.position = ranget.index(np.round(trkv[7],2))+1
                        
                        roi_b.channel = 1
                        
                        roi_b.setPositionH( 1, ranget.index(np.round(trkv[7],2))+1, 0)

                        roi_b.strokeLineWidth = 3.0
                        #Colours each volume-region uniquely.
                        np.random.seed(int(trkv[4]))
                        roi_b.strokeColor = RGB_encoder(255,np.random.randint(0, 255),np.random.randint(0, 255),np.random.randint(0, 255))

                        data.append(encode_ij_roi(roi_b))

                    #We overwrite the existing overlays in the file.
                    if extend_roi == True:
                        metadata['Overlays'].extend(data)
                    else:
                        metadata['Overlays'] = data


                    tifffile.imsave(output_file,im_stk, shape=im_stk.shape, imagej=True, ijmetadata=metadata)
                    tfile.close()
                    
    def plot_reg(self,input_file,ch):
        """plot the roi_array for an image stack.
        
        This function will for an input image export the overlays.
        The colours of the overlays should be consistent for each cell across the stack.
        It will not work for overlays which do not result from the processing of this function.
        This is because it relies on the naming convention of the regions within the Tiff meta-data.
        
        """
        tfile = tifffile.TiffFile(input_file)
        img_stk = tfile.asarray()
        img_shape = img_stk.shape
        

        roi_array = return_overlay(tfile)
        
        for z in range(0,img_stk.shape[0]):
            im = img_stk[z,ch,:,:]
            plt.figure()
            plt.imshow(im)
            for roi in roi_array:

                if roi.position == z+1 or roi.slice == z+1:
                    
                    idname = int(roi.name.replace('\x00', '').split('-')[1])
                    rx0 = roi.x
                    rx1 = roi.x+roi.width
                    ry0 = roi.y
                    ry1 = roi.y+roi.height
                    np.random.seed( idname )
                    R = (np.random.random())  # same random number as before
                    G = (np.random.random())  # same random number as before
                    B = (np.random.random()) # same random number as before
                    plt.plot([rx0,rx0,rx1,rx1,rx0],[ry0,ry1,ry1,ry0,ry0],'-o',c=[R,G,B])

def return_data_from_reg(img_stk, roi_array,type_of_data,zpos_ind=False):
        """This function allows you to extract data from the processed regions.
        In each case, the function will return a dictionary, with one entry per cell. Depending on the 
        type_of_data variable value a different thing will returned:
        type_of_data = 'raw'              -- This will return a dictionary with each cell region returned.
        type_of_data = 'max_project'       -- This will return a single image per cell which has been max projected through z.
        type_of_data = 'sum'              -- This will return the sum of the intensities for each cell.
        type_of_data = 'area'             -- This will return the size of the detection regions in terms of area.
        type_of_data = 'volume'           -- This will return the size of the detection regions in terms of volume
        type_of_data = 'mean_max_project' -- This will return the mean intensity of the max_projection image of each cell.
        """
        regions = {}

        for z in range(0,img_stk.shape[0]):
            im = img_stk[z,:,:]

            for roi in roi_array:

                if roi.position == z+1 or roi.slice == z+1:
                    rx0 = int(roi.x)
                    rx1 = int(roi.x+roi.width)
                    ry0 = int(roi.y)
                    ry1 = int(roi.y+roi.height)

                    
                    if zpos_ind == False:
                        idname = roi.name.replace('\x00', '').split('-')[1]
                    else:
                        idname = z
                    if idname not in regions:
                        regions[idname] = []
                    if type_of_data == 'raw' or type_of_data == 'max_project' or type_of_data == 'mean_max_project':  
                        #print(idname,ry0,ry1,rx0,rx1)               
                        regions[idname].append(im[ry0:ry1,rx0:rx1])
                        
                    if type_of_data == 'mean':                 
                        regions[idname].append(np.average(im[ry0:ry1,rx0:rx1]))
                    if type_of_data == 'sum':
                         regions[idname].append(np.sum(im[ry0:ry1,rx0:rx1]))
                    if type_of_data == 'area' or type_of_data == 'volume':
                         regions[idname].append((ry1-ry0)*(rx1-rx0))
        
        if type_of_data == 'max_project':
            for cell in regions:

                regions[cell] = np.max(np.array(regions[cell]),0)
        if type_of_data == 'mean':                 
            for cell in regions:
                regions[cell] = np.average(regions[cell])
        if type_of_data == 'sum':                 
            for cell in regions:
                regions[cell] = np.sum(regions[cell])
        if type_of_data == 'mean_max_project':
            for cell in regions:
                regions[cell] = np.average(np.max(regions[cell],0))
        if type_of_data == 'area':
            for cell in regions:
                regions[cell] = regions[cell][0]
        if type_of_data == 'volume':
            for cell in regions:
                regions[cell] = np.sum(regions[cell])

        return regions
def return_overlay(tfile):
    """ Get existing metadata"""
    metadata = tfile.imagej_metadata
    img_stk = tfile.asarray()
    img_shape = img_stk.shape
    if img_shape.__len__()>3:#If it's a hyperstack, we skip channels.
        img_shape = [img_shape[0],img_shape[2],img_shape[3]]


    roi_array = []
    if 'Overlays' in tfile.imagej_metadata:
        overlays = tfile.imagej_metadata['Overlays']
        if overlays.__class__.__name__ == 'list':
            #Multiple overlays and so iterate.
            for overlay in overlays:
                roi_array.append(decode_ij_roi(overlay,img_shape))
        else:
            #One overlay.
            print ('overlays',overlays)
            roi_array = decode_ij_roi(overlays,img_shape)
    else:
        print('no Overlays present in file.')
    return roi_array
def collect_info(outpath,channel,method,zpos_ind=False):
    store_cell_data = []
    filenames = glob.glob(outpath+"/*.tif*")
    for pathname in filenames:
        print('pathname',pathname)
        tfile = tifffile.TiffFile(pathname)
        img_stk = tfile.asarray()
        roi_array = return_overlay(tfile)
        if img_stk.shape.__len__() == 3:
            img_stk = img_stk[:,:,:]
        if img_stk.shape.__len__() == 4:
            img_stk = img_stk[:,channel,:,:]
        data = return_data_from_reg(img_stk, roi_array, method,zpos_ind)
        for cell in data:
            store_cell_data.append(data[cell])
        tfile.close()
    return store_cell_data, roi_array
def normalise_for_8bit(raw_img):
    sorted_img = np.sort(raw_img.flatten())
    sat_fac = 0.3 #Matches Fiji/ImageJ saturation factor of 0.3%
    img_min = int(np.ceil(sorted_img.shape[0]*((sat_fac/2.)/100.)))
    img_max = int(np.floor(sorted_img.shape[0]*((100.-(sat_fac/2.))/100.)))

    lower_bound = sorted_img[img_min]
    upper_bound = sorted_img[img_max]
    #This is very similar to the ImageJ/Fiji methodoloy when saving JPEGs but isn't exactly the same.
    lut = np.concatenate([
            np.zeros(lower_bound, dtype=np.uint16),
            np.linspace(0, 255, upper_bound - lower_bound).astype(np.uint16),
            np.ones(2**16 - upper_bound, dtype=np.uint16) * 255
        ])

    bit_img = lut[raw_img].astype(np.uint8)
    return bit_img
def copy_to_clipboard(cell_data):
    stg = ""
    maxt = 0
    for num in range(0,cell_data.__len__()):
        if cell_data[num].__len__() > maxt:
            maxt = cell_data[num].__len__()
    for idx in range(0,maxt):
        for num in range(0,cell_data.__len__()):
            if idx < cell_data[num].__len__():
                stg += str(cell_data[num][idx]) 
            stg+="\t"
        stg+='\n'
    pyperclip.copy(stg)
    spam = pyperclip.paste()
input_dir = "/Users/dwaithe/Documents/collaborators/WaitheD/Faster-RCNN-TensorFlow-Python3.5/data/MP6843phaldapi_class/";
output_dir = "/Users/dwaithe/Documents/collaborators/WaitheD/Faster-RCNN-TensorFlow-Python3.5/data/MP6843phaldapi_class/";

cell_type = "cell - neuroblastoma phalloidin dapi";

file_list = getFileList(input_dir);

count = 010037;
for (fl = 0; fl < file_list.length; fl++){

if(endsWith(file_list[fl], 'zip')==true){
run("Close All");
//newImage("Untitled", "8-bit black", 532, 532, 1);
roiManager("Reset");
a = IJ.pad(count,6);
count = count+1;

end = lengthOf(file_list[fl])-4;
open(input_dir+"zipsB/"+substring(file_list[fl],0,end)+".zip");
open(input_dir+"JPEGImages/"+substring(file_list[fl],0,end)+".jpg");

ted = substring(file_list[fl],0,6);
//print(ted);
//ted = IJ.pad(a,6);
//print(ted);
//exit();
//print(substring(file_list[fl],14,20));

num = a;
//saveAs("Jpeg", output_dir+"Images/"+ted+".jpg");
path = output_dir+"Annotations/"+ted+".xml";

roiCount = roiManager("Count");
if(File.exists(path)){
File.delete(path) 
	}
f = File.open(path);

File.append("<annotation>", path);
File.append("\t<folder>dc2018</folder>", path);
File.append("\t<filename>"+ted+".jpg</filename>", path);
File.append("\t<source>", path);
File.append("\t\t<database>The 2018 cell Database</database>", path);
File.append("\t\t<annotation>Waithe 2018</annotation>", path);
File.append("\t\t<image>confocal</image>", path);
File.append("\t\t<omeroid></omeroid>", path);
File.append("\t</source>", path);
File.append("\t<owner>", path);
File.append("\t\t<name></name>", path);
File.append("\t</owner>", path);
File.append("\t<size>", path);
File.append("\t\t<width>"+(getWidth())+"</width>", path);
File.append("\t\t<height>"+(getHeight())+"</height>", path);
File.append("\t\t<depth>3</depth>", path);
File.append("\t</size>", path);
File.append("\t<segmented>0</segmented>", path);
for (obj=0;obj<roiCount;obj++){

name =	call("ij.plugin.frame.RoiManager.getName", obj);
roiManager("select",obj);
Roi.getBounds(x, y, width, height);

File.append("<object>", path);
File.append("<name>"+cell_type+"</name>", path);
File.append("<pose>Unspecified</pose>", path);
File.append("<truncated>0</truncated>", path);
File.append("<difficult>0</difficult>", path);
File.append("<bndbox>", path);
File.append("\t\t<xmin>"+(x+1)+"</xmin>", path);
File.append("\t\t<ymin>"+(y+1)+"</ymin>", path);
File.append("\t\t<xmax>"+(x+width)+"</xmax>", path);
File.append("\t\t<ymax>"+(y+height)+"</ymax>", path);
File.append("\t</bndbox>", path);
File.append("\t</object>", path);
}




File.append("</annotation>", path);
File.close(f);
}
//runMacro("/Users/dwaithe/Documents/collaborators/WaitheD/region_prop/peroxisomes_B/sata.ijm")
}


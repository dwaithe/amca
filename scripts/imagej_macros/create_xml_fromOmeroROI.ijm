titl = getTitle();
output_dir = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/erythroid_dapi_class/2019/";
print(titl);
index1 = lastIndexOf(titl, "OMERO ID:")+9;
ted = substring(titl, index1, lengthOf(titl));
print(ted);

cell_type = "cell - erythroid dapi";

path = output_dir+"Annotations/"+ted+".xml";
JPEGpath = output_dir+"JPEGImages/"+ted+".jpg";

roiCount = roiManager("Count");
if(File.exists(path)){
File.delete(path) 
	}
f = File.open(path);

File.append("<annotation>", path);
File.append("\t<folder>dc2019</folder>", path);
File.append("\t<filename>"+ted+".jpg</filename>", path);
File.append("\t<source>", path);
File.append("\t\t<database>The 2019 cell Database</database>", path);
File.append("\t\t<annotation>Waithe 2019</annotation>", path);
File.append("\t\t<image>confocal</image>", path);
File.append("\t\t<omeroid></omeroid>", path);
File.append("\t</source>", path);
File.append("\t<owner>", path);
File.append("\t\t<name></name>", path);
File.append("\t</owner>", path);
File.append("\t<size>", path);
File.append("\t\t<width>"+(round(getWidth()/2))+"</width>", path);
File.append("\t\t<height>"+(round(getHeight()/2))+"</height>", path);
File.append("\t\t<depth>3</depth>", path);
File.append("\t</size>", path);
File.append("\t<segmented>0</segmented>", path);
for (obj=0;obj<roiCount;obj++){

name =	call("ij.plugin.frame.RoiManager.getName", obj);
print(">"+name+"<>"+obj+"-class one"+"<");
if(name == obj+"-class one"){
print("works");


roiManager("select",obj);
Roi.getBounds(x, y, width, height);

File.append("<object>", path);
File.append("<name>"+cell_type+"</name>", path);
File.append("<pose>Unspecified</pose>", path);
File.append("<truncated>0</truncated>", path);
File.append("<difficult>0</difficult>", path);
File.append("<bndbox>", path);
File.append("\t\t<xmin>"+(round(x/2)+1)+"</xmin>", path);
File.append("\t\t<ymin>"+(round(y/2)+1)+"</ymin>", path);
File.append("\t\t<xmax>"+(round(x/2+width/2)+1)+"</xmax>", path);
File.append("\t\t<ymax>"+(round(y/2+height/2)+1)+"</ymax>", path);
File.append("\t</bndbox>", path);
File.append("\t</object>", path);
}}




File.append("</annotation>", path);
File.close(f);
run("Select None");
run("Scale...", "x=0.5 y=0.5 width=512 height=512 interpolation=Bilinear average create");
saveAs("Jpeg", JPEGpath);
if (isOpen("ROI Manager")) {
     selectWindow("ROI Manager");
     run("Close");
  }
run("Close All");




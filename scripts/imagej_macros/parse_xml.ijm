//for(i=108632;i<108633;i++){
//info_path = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/c127_dapi_class/2018/Annotations/"+i+".xml";
//img_dir ="/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/c127_dapi_class/2018/JPEGImages/";

//for(i=110087;i<110088;i++){
//info_path = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/neuroblastoma_phal_class/2018/Annotations/"+i+".xml";
//img_dir = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/neuroblastoma_phal_class/2018/JPEGImages/";

//for(i=63754;i<63755;i++){
//info_path = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/erythroblast_dapi_class/2018/Annotations/0"+i+".xml";
//img_dir = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/erythroblast_dapi_class/2018/JPEGImages/";

//for(i=110089;i<110090;i++){
//info_path = "/Users/dwaithe/Documents/collaborators/WaitheD/region_prop/broad/MP6843/Annotations/"+i+".xml";
//img_dir = "/Users/dwaithe/Documents/collaborators/WaitheD/region_prop/broad/MP6843/JPEGImages/";
//for(i=61678;i<61679;i++){
//info_path = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/eukaryote_dapi_class/2018/Annotations/0"+i+".xml";
//img_dir = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/eukaryote_dapi_class/2018/JPEGImages/";
//for(i=10045;i<10046;i++){
//info_path = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/fibroblast_nucleopore_class/2018/Annotations/0"+i+".xml";
//img_dir   = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/fibroblast_nucleopore_class/2018/JPEGImages/";
//print(info_path);
for(i=107614;i<107615;i++){
info_path ="/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/hek_peroxisome_class/2018/Annotations/"+i+".xml";
img_dir = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/hek_peroxisome_class/2018/JPEGImages/";
info_string = File.openAsString(info_path);
roiManager("Reset");
//run("Close All");
stt = indexOf(info_string, "<filename>");
end = indexOf(info_string, "</filename>");
filename = substring(info_string,stt+10,end);
open(img_dir+filename);

for(obj=0;obj<500;obj++){
stto = indexOf(info_string, "<object>",stt);
if (stto == -1){
	break;
	}
endo = indexOf(info_string, "</object>",stt);

stt = indexOf(info_string, "<name>",stto);
end = indexOf(info_string, "</name>",stto);
name = substring(info_string,stt+6,end);
stt = indexOf(info_string, "<xmin>",stto);
end = indexOf(info_string, "</xmin>",stto);
xmin = parseFloat(substring(info_string,stt+6,end));
stt = indexOf(info_string, "<ymin>",stto);
end = indexOf(info_string, "</ymin>",stto);
ymin = parseFloat(substring(info_string,stt+6,end));
stt = indexOf(info_string, "<xmax>",stto);
end = indexOf(info_string, "</xmax>",stto);
xmax = parseFloat(substring(info_string,stt+6,end));
stt = indexOf(info_string, "<ymax>",stto);
end = indexOf(info_string, "</ymax>",stto);
ymax = parseFloat(substring(info_string,stt+6,end));

makeRectangle(xmin-1, ymin-1, xmax-xmin, ymax-ymin);
roiManager("Add");
roiManager("select",roiManager("count")-1);
roiManager("rename", name)
setColor(255,255,255);
//run("Draw");
print(name,xmin,xmax,ymin,ymax);
//roiManager("Save", "/Users/dwaithe/Documents/collaborators/WaitheD/Faster-RCNN-TensorFlow-Python3.5/data/nucleopore_class/2018/zips/0"+i+".zip");
stt = end;
}}
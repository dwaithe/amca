//pathfile=File.openDialog("Choose the file to Open:"); 
filestring=File.openAsString("/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/scripts/somefile.txt"); 

title = getTitle();

readMinX = -9421;
readMinY = 391.2;

rows=split(filestring, "\n"); 
x0=newArray(rows.length); 
y0=newArray(rows.length);
x1=newArray(rows.length); 
y1=newArray(rows.length);
c =newArray(rows.length);
for(i=0; i<rows.length; i++){ 
columns=split(rows[i],","); 
x0[i]=parseInt(columns[0])/0.26; 
y0[i]=parseInt(columns[1])/0.26; 
x1[i]=parseInt(columns[2])/0.26; 
y1[i]=parseInt(columns[3])/0.26;
c[i]  =parseInt(columns[4]);

} 
Array.getStatistics(x0, minx, maxx, mean, stdDev) ;
Array.getStatistics(y0, miny, maxy, mean, stdDev) ;
print(minx,miny);
for(i=0; i<rows.length; i++){ 
random("seed", c[i]);
makeRectangle(x0[i]-(readMinX/0.26), y0[i]-(readMinY/0.26), x1[i]- x0[i],y1[i]- y0[i]);
run("Measure");
r = round(random()*255);
g = round(random()*255); 
b = round(random()*255);
 
setForegroundColor(r,g,b);
run("Draw");

}


from omero.gateway import BlitzGateway
import omero
# Pixels and Channels will be loaded automatically as needed

def rtn_raw_image(imageId,conn):
    image = conn.getObject("Image", imageId)
    z = 0
    t = 0
    c = 0
    pixels = image.getPrimaryPixels()
    plane = pixels.getPlane(z, c, t) 
    return plane


def rtn_roi(imageId,conn):
    roi_service = conn.getRoiService()
    result = roi_service.findByImage(imageId, None)
    out_roi = []
    for roi in result.rois:
        #print ("ROI:  ID:", roi.getId().getValue())
        for s in roi.copyShapes():
            shape = {}
            shape['id'] = s.getId().getValue()
            #shape['theT'] = s.getTheT().getValue()
            shape['theZ'] = s.getTheZ().getValue()
            if s.getTextValue():
                shape['textValue'] = s.getTextValue().getValue()
            if type(s) == omero.model.RectangleI:
                shape['type'] = 'Rectangle'
                shape['x'] = s.getX().getValue()
                shape['y'] = s.getY().getValue()
                shape['width'] = s.getWidth().getValue()
                shape['height'] = s.getHeight().getValue()
            elif type(s) in (
                    omero.model.LabelI, omero.model.PolygonI):
                print (type(s), " Not supported by this code")
            x = shape['x']
            y = shape['y']
            wid = shape['width'] 
            hei = shape['height']
            class_name = shape['textValue']
            
            out_roi.append([x,y,wid,hei,class_name])
            
    return out_roi




def rtn_img_ids_from_dataset(dataset_id,conn):
    my_exp_id = conn.getUser().getId()
    default_group_id = conn.getEventContext().groupId
    out_list = []
    for project in conn.getObjects("Project", opts={'owner': my_exp_id,'group': default_group_id,'order_by': 'lower(obj.name)',
                                                'limit': 5, 'offset': 0}):
        for dataset in project.listChildren():
            if dataset.id == dataset_id:
                #print_obj(dataset, 2)
                for image in dataset.listChildren():
                    out_list.append(image.id)
    return out_list

#
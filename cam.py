import numpy as np
import cv2
import os
import time
from datetime import datetime
from config import *
from imgproc import *

#capture frame from camera
def cameraRead(camera):
    #first photo is from buffer
    _, _ = camera.read()
    _, photo = camera.read()
    return photo
    

def timestr():
    now = datetime.now()
    return now.strftime("%d%m%y_%H%M%S")


#clean storage if coun of images is more than Archive size
def autoClean():
    count = len([name for name in os.listdir("pic")])-1
    if count > ARCHIVE_SIZE:
        os.system(CLEAR_CMD)
        
#cap , save , and draw contours
def capimg(camera,aws_client):
    if not camera.isOpened():
        raise IOError("Cannot open webcam")
    
    print("cheesus")
    image = cameraRead(camera)
    
    #draw rectangle around person
    #image = findFace(image)
    image = findPersons(image,aws_client)

    #save image in storage
    dirpath = os.getcwd()
    imgname = "pic{}NEK{}.png".format(SEP,timestr())
    filename = dirpath+SEP+imgname
    cv2.imwrite(filename, image)
    return filename

##old
#def capimgCMD():
#    dirpath = os.getcwd()
#    imgname = "pic/NEK{}.png".format(timestr())
#    
#    filename = dirpath+"/"+imgname
#    str = "fswebcam {}".format(imgname)
#    os.system(str)
#    return filename


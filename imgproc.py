import cv2
import numpy as np
import boto3
import csv
import base64
from PIL import Image
import io

from config import *

#outputs pythagorean distance between two frames
def distMap(frame1, frame2):
    frame1_32 = np.float32(frame1)
    frame2_32 = np.float32(frame2)
    diff32 = frame1_32 - frame2_32
    norm32 = np.sqrt(diff32[:, :, 0] ** 2 + diff32[:, :, 1] ** 2 + diff32[:, :, 2] ** 2) / np.sqrt(
    255 ** 2 + 255 ** 2 + 255 ** 2)
 
    dist = np.uint8(norm32 * 255)
    return dist

def stDev2frames(bg,fg):
    dist = distMap(bg,fg)
    mod = cv2.GaussianBlur(dist, (9, 9), 0)
    _, stDev = cv2.meanStdDev(mod)
    return stDev

#contours around changes zones between CV2 frames
def findContours(bg,fg):
    d =cv2.absdiff(bg,fg)
    grey = cv2.cvtColor(d , cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey,(9,9),0)
    _, thresh = cv2.threshold(blur, 50, 255, 0)
    dilated = cv2.dilate(thresh,np.ones((3,3), np.uint8),iterations=3)
    eroded = cv2.dilate(dilated,np.ones((5,5), np.uint8),iterations=10)
    _ , contours , hierarchy = cv2.findContours(eroded , cv2.RETR_TREE , cv2.CHAIN_APPROX_SIMPLE)
    return contours 
    
#draw cv2 contours on frame 
def drawContours(frame , contours):
    output = copy.deepcopy(frame)
    #count of countor bigger than CONT_AREA
    n = 0
    cv2.drawContours(output,contours, -1,255,3)
    for contour in contours:
        (x,y,w,h) = cv2.boundingRect(contour)         
        if cv2.contourArea(contour)<CONT_AREA:
            continue
        cv2.rectangle(output , (x,y) , (x+w,y+h),(0,255,0),2)
        n+=1
    
    #if all countors are small , draw biggest
    if n == 0 and len(contours)!=0:
        maxcontour = max(contours,key = cv2.contourArea)
        (x,y,w,h) = cv2.boundingRect(maxcontour)
        cv2.rectangle(output , (x,y) , (x+w,y+h),(0,255,0),2)
           
    return output

#find face using haarcascade classifiers and draw rectangles around them
def findFace(image):
    faceCascade = cv2.CascadeClassifier(HAARCASCADE)
    proFaceCascade = cv2.CascadeClassifier(HAARCASCADE2)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minSize=(20, 20))
    profaces = proFaceCascade.detectMultiScale(gray,scaleFactor=1.1,minSize=(20, 20))
    
    facecount = 0
    for (x, y, w, h) in faces:
        facecount = facecount + 1
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
    for (x, y, w, h) in profaces:
        facecount = facecount + 1
        cv2.rectangle(image, (x, y), (x + w, y + h), (255,0, 0), 1)   
    return image 


#fit coord from AWS response instace into image size
def getInstanceCoord(instance , image):
    height, width, channels = image.shape

    w = int(instance["BoundingBox"]["Width"] * width)
    h = int(instance["BoundingBox"]["Height"] *height)
    x = int(instance["BoundingBox"]["Left"] *width)
    y = int(instance["BoundingBox"]["Top"] *height)
    return (x,y,w,h)

#parse AWS response and draw bounding box aroun Person and Face
def drawBoundingBox(response,frame):
     
    for label in response['Labels']:
        print(label['Name'])
        if label['Name'] == 'Person':
            for instance in label['Instances']:
                x, y, w, h = getInstanceCoord(instance, frame)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1) #green
        if label['Name'] == 'Face':
            for instance in label['Instances']:
                x, y, w, h = getInstanceCoord(instance, frame)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1) #red
    return frame

def opencvFrameToBin(frame):
    # convert opencv frame (with type()==numpy) into PIL Image
    pil_img = Image.fromarray(frame)
    stream = io.BytesIO()
    # convert PIL Image to Bytes
    pil_img.save(stream, format='JPEG')  
    bin_img = stream.getvalue()
    return bin_img

#make request to AWS cloud
def makeRequestAWS(client, bin_img):
    response = client.detect_labels(Image ={'Bytes': bin_img } , MaxLabels =10  )
    return response

#find persons on photo using aws rekongnition and draw rectangles around 
def findPersons(frame , aws_client):
    bin_img = opencvFrameToBin(frame)
    response = makeRequestAWS(aws_client,bin_img)
    frame = drawBoundingBox(response,frame)
    return frame
    
    
    
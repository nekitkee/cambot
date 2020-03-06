from telebot import types
import datetime
import time
import logging
import threading
import copy

import csv
import boto3

import telebot
from subprocess import Popen , PIPE
import ssl
from aiohttp import web


from cam import *
from imgproc import *
import numpy as np

import cv2


import config
from config import *

#SETUP
logging.basicConfig(filename="logs.log" , level=logging.INFO , format="%(asctime)s:%(levelname)s:%(message)s")
bot = telebot.TeleBot(TOKEN)
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_BUFFERSIZE , 1)
#setup aws client
with open(CREDENTIALS, 'r') as input:
    next(input)
    reader = csv.reader(input)
    for line in reader:
        access_key_id = line[2]
        secret_access_key=line[3]

    aws_client = boto3.client('rekognition',
                          aws_access_key_id = access_key_id,
                          aws_secret_access_key = secret_access_key ,region_name=AWS_region_name )


alarmState = False
StartBtnPressed = False

logging.info("START:")
print("ALIVE")

@bot.message_handler(commands=["ping"])
def ping_cmd(message):
    logging.info("\nchat:{}  \n ping \n".format( str(message.chat.id)  ))
    bot.send_message(message.chat.id, "pong")
    
@bot.message_handler(commands=["temp"])
def temp_cmd(message):
    logging.info("\nchat:{}  \n temp \n".format( str(message.chat.id)  ))
    output = Popen(TEMP_CMD , stdout=PIPE)
    response = output.communicate()
    bot.send_message(message.chat.id, response)
    
@bot.message_handler(commands=["clear"])
def clear_cmd(message):
    if not message.from_user.id in WHITELIST:
        return
    output = Popen(CLEAR_CMD.split(" ") , stdout=PIPE)
    bot.send_message(message.chat.id, MESSAGE_FOLDER_CLEAR)
    logging.info("\nchat:{}  \n clear \n".format( str(message.chat.id)  ))

@bot.message_handler(commands=["count"])
def count_cmd(message):
    if not message.from_user.id in WHITELIST:
        return
    count = len([name for name in os.listdir("pic")])-1
    bot.send_message(message.chat.id, count)
    logging.info("\nchat:{}  \n clear \n".format( str(message.chat.id)  ))


@bot.message_handler(commands=["photo"])
def photo_cmd(message):
    try:
        if not message.from_user.id in WHITELIST:
            return
        bot.send_message(message.chat.id,MESSAGE_WAIT)
        
        #if (not alarmState):
            #initCam(True)
        file = capimg(camera,aws_client)
    
        #if (not alarmState):
        #    initCam(False)
    
        userid = message.from_user.id
        if userid != SUPERUSER:
            photo = open(file, 'rb')
            bot.send_message(SUPERUSER, "new capture request from user {}.".format(userid))
            bot.send_photo(SUPERUSER ,photo )
            del(photo)
    
        photo = open(file, 'rb')
        bot.send_photo(message.chat.id ,photo )
        del(photo)
    
        autoClean()
        logging.info("\nchat:{}  \n file: {} \n".format( str(message.chat.id) , file ))
    except:
        bot.send_message(message.chat.id , MESSAGE_WAIT2 )

#test
#def initCam(init):
#    global camera
#    
#    #true positive
#    try:
#        if init and camera.isOpened():
#            return
#    except:
#        pass
#
#    if (not init):
#        camera.release()
#    #true negative
#    else:
#        camera = cv2.VideoCapture(-1)
#        camera.set(cv2.CAP_PROP_BUFFERSIZE , 1)
#        while(not camera.isOpened()):
#            pass
    
        
        
@bot.message_handler(commands=["stop"])
def stop_cmd(message):
    if not message.from_user.id in WHITELIST:
        return
    
    bot.send_message(SUPERUSER , MESSAGE_ALARM_OFF)
    global alarmState
    alarmState = False
    #initCam(False)

 
@bot.message_handler(commands=["start"])
def start_cmd(message):
    if not message.from_user.id in WHITELIST:
        return
    #initCam(True)
    global alarmState
    alarmState =True
    global StartBtnPressed
    StartBtnPressed = True
    
    bot.send_message(SUPERUSER, MESSAGE_ALARM_ON )

    




    


def doOnAlarm(bg,fg):
    bot.send_message(SUPERUSER , "ALARM")
    
    #DRAWING CONTOURS#### (3 options)
    
    ####1. changing zones 
    #contours = findContours(bg,fg)
    #alarmframe = drawContours(fg , contours)
    
    ####2.find faces using haar-cascade (look in config for xlm)
    #alarmframe = findFace(fg)
    
    ####3.find persons using AWS rekongnition
    alarmframe = findPersons(fg , aws_client)
    
    
    file = "alarm.png"
    cv2.imwrite(file ,alarmframe)
    photo = open(file,'rb')
    bot.send_photo(SUPERUSER ,photo )
    photo.close()
           
           
def updateBg(bg):
     global StartBtnPressed
     if StartBtnPressed:
        newbg = cameraRead(camera)
        StartBtnPressed = False
        return newbg
     else:
         return bg

    
def Alarm_thread():    
    bot.send_message(SUPERUSER , "Alarm is initialized.")
    #background
    bg = None
    while (True):
        #delay when checking working mode
        time.sleep(0.5)
        #active mode
        if alarmState:
            #after START command we have to update background to compare next photos
            #(only once)
            bg = updateBg(bg)
            #foreground
            fg = cameraRead(camera)  
            if stDev2frames(bg,fg) > SD_THREASH:
                doOnAlarm(bg,fg)
                time.sleep(2)
            #shift frames    
            bg=fg
    

x = threading.Thread(target= Alarm_thread)
x.start()

async def handle(request):
    print("new request from Telegram")
    request_body_dict = await request.json()
    #print(request_body_dict)
    update = telebot.types.Update.de_json(request_body_dict)
    bot.process_new_updates([update])
    return web.Response()


def gpsUpdate(gps_json):
    print(gps_json)


async def gps_handler(request):
    print("New GPS Data")
    #print(request.scheme)
    gps_json = await request.json()
    gpsUpdate(gps_json)
    return web.Response( status=200 , text="test")
    


app = web.Application()
app.router.add_post("/"+TOKEN , handle)
app.router.add_post( "/"+GPS_PATH, gps_handler)


context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT , WEBHOOK_SSL_PRIV)
web.run_app(app , host=WEBHOOK_LISTEN , port = WEBHOOK_PORT ,ssl_context = context)




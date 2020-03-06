# About Project

This is source code of my custom security device!
Device is powered on Raspbery pi with a simple webcam.
***
### Features:
1. Moving detection using CV2 library.
2. Control access and notifications through Telegram webhook bot running on aiohttp server.
3. Person detection on captured images (in 3 ways): _haar-cascade functions, aws rekognition service, cv2._

Planed upgrade:
* Devices auto switching on/off when you come/leave home, based on gps data automatecly sent from Android self-writen service. 

***
### Telegram commands:

`/start` - Switch on moving detection

`/stop` - Switch off moving detection 

`/photo` - Make a photo

`/ping` - Test connection 

`/count ` - images count on storage 

`/clear` - delete iamges

`/temp ` - Raspberry Pi CPU temperature 

***

### SETUP

If you want to deploy the project, you have to install all required python libraries and create new telegram bot.
Replace **TOKEN** string in **config file** with your own. 

Next, you have to set Telegram webhook: Use command from **ssl cmds.txt** file to generate SSL certificates, and **uploadcer.html** for sending them to the telegram server.

For AWS rekognition feature create a free account and download credentials.csv.




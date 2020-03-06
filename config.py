


tempcmd = ["vcgencmd"," measure_temp"]

WEBHOOK_SSL_CERT = "/home/pi/bot_public.pem"
WEBHOOK_SSL_PRIV = "/home/pi/bot_private_key.key"
WEBHOOK_LISTEN = "0.0.0.0"
WEBHOOK_PORT = 8443

#aws
CREDENTIALS = "/home/pi/credentials.csv"
AWS_region_name= 'us-west-2'

#bot token
TOKEN = "PLACEYOURTOKENHERE___I0z3Vggdsf-Rua8k"

HAARCASCADE='haar_face.xml'
HAARCASCADE2 = 'haarcascade_profileface.xml'

SEP= "/"

ARCHIVE_SIZE = 100
CONT_AREA= 2500
SD_THREASH = 10

GPS_PATH = "gps"

TEMP_CMD = ["vcgencmd"," measure_temp"]
CLEAR_CMD = "find . -name NEK* -type f -delete"

#telegram id
WHITELIST = [563245445234 , 3523453253 ]
SUPERUSER = 563545345325


#messages
MESSAGE_UNEXP_ERROR = "Unexpected error , try again.."
MESSAGE_WAIT = "Wait..."
MESSAGE_WAIT2="Be patient and wait"

MESSAGE_ALARM_OFF = "Alarm is turned off"
MESSAGE_ALARM_ON = "Alarm is turned on"
MESSAGE_FOLDER_CLEAR = "Pic folder is clean"

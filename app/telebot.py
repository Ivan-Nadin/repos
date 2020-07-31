
#-------Import necessary packages-------#
import requests
import io
from pydub import AudioSegment
import cv2
from mtcnn import MTCNN
import numpy as np


detector = MTCNN() # create detector with weights set by default

class Telebot():
    def __init__(self,token,server):
        self.token = token
        self.server = server # Server for deploy telegram bot
        self.url_api = f'https://api.telegram.org/bot{token}/' # link bot
        self.url_api_file = f'https://api.telegram.org/file/bot{token}/' # link bot's getting file

    # for getting updates from telegram need to activate method webhook for server where bot is deployed
    def setWebhook(self):
        url = self.url_api+f'setWebhook?url={self.server}'
        r_hook = requests.get(url).json()
        print(r_hook["description"])

    # generate response to user ,including (text,file,caption) with helping API methods (sendmessage,sendaudio,sendphoto)
    def send_message(self,chat_id,type_message,text=None,file=None,caption=None):
        url = self.url_api + f'send{type_message}?chat_id={chat_id}'
        files = {type_message: file}
        answer = { 'text': text
                  ,'caption' : caption}
        r_answer = requests.post(url, data=answer,files=files)

    # decorator for function which work with file getting from telegram server (voice,photo)
    # function  get_file_content  obtain file contents in binary format
    def get_file_content(f):
        def get_file_content(self,file_id):
            url_file_path = self.url_api+f'getFile?file_id={file_id}' # API method getFile
            r_file_path = requests.get(url_file_path).json() # get location file
            file_path = r_file_path['result']['file_path']
            url_file = self.url_api_file+file_path
            r_file = requests.get(url_file)
            file_content = f(self,r_file.content,file_id)
            return file_content
        return get_file_content

    # checking the presence of faces in the photo
    @get_file_content
    def detect_face(self,file_content,file_id):
        # https://stackoverflow.com/questions/44324944/how-to-decode-jpg-image-from-memory
        image = cv2.imdecode(np.frombuffer(file_content, dtype=np.uint8), cv2.IMREAD_UNCHANGED) # original photo
        result = detector.detect_faces(image)  # recognize face on photo
        if len(result) > 0:
            for i in range(len(result)): # loop over all found objects (faces)
              bounding_box = result[i]['box']  # array with detected bounding boxes
              cv2.rectangle(image,
                            (bounding_box[0], bounding_box[1]),
                            (bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3]),
                            (0,155,255),
                            2) # rendering bounding boxes on photo
        # https://stackoverflow.com/questions/17967320/python-opencv-convert-image-to-byte-string
        image_bytes = cv2.imencode('.jpg', image)[1].tobytes() # convert image to bytes for storage in db
        return file_content,image_bytes,len(result)

    # convert voice to format wav with 16kHZ rate
    @get_file_content
    def convert_voice(self,file_content,file_id):
        s = io.BytesIO(file_content) # convert to bytes
        audio = AudioSegment.from_file(s) # original voice
        # https://stackoverflow.com/questions/44035217/pydub-how-to-change-frame-rate-without-changing-playback-speed
        audio = audio.set_frame_rate(16000) # change sampling rate
        # https://github.com/jiaaro/pydub/issues/270
        buf = io.BytesIO()
        audio.export(buf, format = "wav") # convert voice to bytes for storage in db
        return file_content,buf.getvalue()

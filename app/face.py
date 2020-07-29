import cv2
from mtcnn import MTCNN
import matplotlib.pyplot as plt
import numpy as np

#MTCNN
detector = MTCNN() # создание детектора, с установленными весами  по умолчанию

def detect_face(content):
    image = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_UNCHANGED) # исходное изображение
    result = detector.detect_faces(image)  # обнаружение лиц на изображении
    if len(result)>0:
        #print(f'Найдено лиц в количестве {len(result)} ')
        for i in range(len(result)): # цикл по всем найденным объектам
          bounding_box = result[i]['box']  # массив со  обнаруженными ограничивающими рамками
          cv2.rectangle(image,
                        (bounding_box[0], bounding_box[1]),
                        (bounding_box[0]+bounding_box[2], bounding_box[1] + bounding_box[3]),
                        (0,155,255),
                        2) # отрисовка ограничительность области на изображении
    image_bytes=cv2.imencode('.jpg', image)[1].tobytes()
    return image_bytes,len(result)

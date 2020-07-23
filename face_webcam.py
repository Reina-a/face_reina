import face_recognition
import facekit_reina
from cv2 import cv2
import os

'''
快速开始, 请修改ip_camera_url(必要)
'''



#-------------预设/初始化-------------#

#设置url
ip_camera_url = 'http://192.168.31.251:4747/mjpegfeed'

#根据url新建video capture
video_capture = cv2.VideoCapture(ip_camera_url)

#设置视频参数
codec = cv2.VideoWriter_fourcc(*'MJPG')
fps= 20.0
framesize=(640, 480)

#根据视频参数新建VideoWriter
out = cv2.VideoWriter('output.avi', codec, fps, framesize)

#设置捕获总帧数
total_frame = 200

# 设置人脸定位相关参数
raw_img_path = 'src/webcam/'
#positioned_img_path = 'imgs/posotioned/'
recognized_img_path = 'src/webcam/recognized/'
known_img_path = 'src/known/'

if not os.path.exists(raw_img_path):
    os.mkdir(raw_img_path)

if not os.path.exists(recognized_img_path):
    os.mkdir(recognized_img_path)

#-------------开始捕获-------------#

for i in range(total_frame):
    
    #截获一帧
    ret, frame = video_capture.read()
    
    #设置保存文件名
    file_name = 'imgs/test' + "{:0>4d}".format(i) + '.jpg'
    cv2.imwrite(file_name, frame)
#捕获帧完毕, 释放摄像头
video_capture.release()

#-------------后期处理-------------#

# 人脸识别(reina自定义模块)
print("Start positioning...")
facekit_reina.start_recognition(raw_img_path, recognized_img_path, known_img_path)
print("Positioned.")

# 读入处理后的图片
print("Start reading...")
imgs = []
for i in range(total_frame):
    imgs.append(cv2.imread(recognized_img_path + 'test' + "{:0>4d}".format(i) + '.jpg'))
print("Read.")

# 编码成视频
print("Start encoding...")
for img in imgs:
    out.write(img)
print("Encoded.")

# 释放资源
cv2.destroyAllWindows()
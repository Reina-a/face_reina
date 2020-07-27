'''
@author Reina
@desc 基于opencv与face_recognition开源项目的自定义模块
@date 2020/7/20
描述 :
包含两个子模块: 人脸定位模块和人脸识别模块
人脸定位: 
- position_an_image函数: 为单张图片进行定位和绘制
- position_a_folder函数: 一个文件夹内批量生成定位图片的流程控制
人脸识别:
- gen_sav_encodings_dict函数: 生成并保存已知'编码字典'
- face_people_match函数: 根据'编码字典', 匹配一张人脸
- crop_and_recognize函数: 找到一张图片中的所有人脸, 依次裁剪后识别, 返回识别结果
- recognize_an_imge函数: 对一张图片进行识别, 并根据结果绘制图像
- recognize_a_folder函数: 一个文件夹内批量生成识别图片的流程控制

description:
2 module included: face position and face recognition
face position:
- function: position_an_image: position and draw for a single image
- function: position_a_folder: position and draw for a folder
face recognition:
- function: gen_sav_encodings_dict: generate and save the encoding dictionary
- function: face_people_match: match a face with data in encoding dictionary
- function: crop_and_recognize: find all faces in one image, crop and recognize for each, return the results
- function: recognize_an_imge: recognize and draw results for one image
- function: recognize_a_folder: recognition flow control in a single folder
'''

#coding=utf-8

import face_recognition
import folder_manager_reina

import os
import json
import numpy

# if you are not using a wsl, replace it with 'import cv2'
# 如果你不使用WSL的话, 请用'import cv2'代替它
from cv2 import cv2



###------------------预定义变量 predefinition------------------###

# Compatible Formats  
# 支持的文件格式
compatible_formats=['.jpg','.jpeg','.gif','.png']

# json path without filename
# json文件目录(无文件名)
json_path = 'src/known/.json/'

# json filename
# json文件名
encoding_json = 'encoding.json'
modate_json = 'modate.json'

# face rocognition tolerance
# 人脸识别容错率
fault_tolerance = 0.5


# reference of coordinate(same as opencv)
# 坐标系参考(同opevcv)

#   ——————————— --→ x
#   |         |
#   |  IMAGE  |
#   |         |
#   ———————————
#   ↓
#   y

###------------------定位模块 position module------------------###

#============================================================== 
# generate position for one image                                                       
# 为单张图片进行定位和绘制
# @parameter:                                                 
# - filename_withpath:  file name with path (e.g. 'src/unpositioned/img1.png')
#                       带目录的文件名 (例: 'src/unpositioned/img1.png')
# - positioned_path:    the target path which will store the positioned image. (e.g. 'src/positioned/')
#                       保存定位生成图片的目标路径 (例: 'src/positioned/')  
# @return: (no return)
def position_an_image(filename_withpath:str, positioned_path:str):
    
    # get filename
    # 得到文件名
    filename = os.path.split(filename_withpath)[1]

    if os.path.splitext(filename)[1] not in compatible_formats:
        return None
    # load file
    # 加载图片文件
    image = face_recognition.load_image_file(filename_withpath)
    
    face_locations=face_recognition.face_locations(image)
     # face_locations eg:(139,283,325,97) (y1,x1,y2,x2)
   
    for face in face_locations:
        y1=face[0]
        x1=face[1]
        y2=face[2]
        x2=face[3]
        xmin = min(x1,x2)
        ymin = min(y1,y2)
        xmax = max(x1,x2)
        ymax = max(y1,y2)
        # draw rectangle according to face position
        # 根据人脸位置画矩形
        cv2.rectangle(image,(xmin,ymin),(xmax,ymax),(255,0,0),3)

    # make the positioned_path directory if not exists
    # 如果没有, 则创建定位图片的路径
    if not os.path.exists(positioned_path):
        os.makedirs(positioned_path)

    # save image
    # 保存图片
    cv2.imwrite(positioned_path + 'p_' + filename, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))


#==============================================================
# position flow control                                                                 
# 单个文件夹内, 批量生成定位图片的流程控制 
# @parameter:
# - raw_path: the path which stores the source image for positioning. (e.g. 'src/unpositioned/')
#             保存待定位图片的路径 (例: 'src/unpositioned/')
# - positioned_path:  the target path which will store the positioned image. (e.g. 'src/positioned/')
#                     保存定位生成图片的目标路径 (例: 'src/positioned/')  
# @return: (no return)
def position_a_folder(raw_path, positioned_path):

    # filename List under the path (all file and floder included)
    # 文件名的列表 (包括所有的文件和文件夹)
    image_name_list=os.listdir(raw_path)

    # make the positioned_path directory if not exists
    # 如果没有, 则创建定位图片的路径
    if not os.path.exists(positioned_path):
        os.makedirs(positioned_path)

    # overwrite flag
    # 覆写标志
    all_overwrite = False

    # process every image with this loop
    # 使用这个循环处理每个图片
    for filename in image_name_list:

        filename_withpath = raw_path + filename
        # make sure that file is compatible
        # 确保文件格式支持

        # if compatible:
        # 如果文件格式支持
        if (os.path.splitext(filename)[1] in compatible_formats):
            
            # detect if the positioned file is already generated
            # 检测是否已经生成定位图片

            # if not generated
            # 如果还没有生成
            if (filename not in os.listdir(positioned_path)):
                # generate positioned image
                # 生成定位图片
                position_an_image(filename_withpath, positioned_path)
            
            # if generated
            # 如果已经被生成
            else:
                # check the overwrite flag
                # 检查覆写标志

                # if overwrite flag is true
                # 如果覆写为真
                if all_overwrite == True:
                    # overwrrite
                    # 覆写
                    position_an_image(filename_withpath, positioned_path)
                # if overwrite is false
                # 如果覆写为假
                else:
                    # wait for choice
                    # 等待选择
                    while True:
                        is_overwrite = input(filename+" already exists, do you want to overwrite it? (Y/n/all): ")
                        if str.lower(is_overwrite) == 'y':
                            # overwrite for this time
                            # 这一张图片覆写
                            position_an_image(filename_withpath, positioned_path)
                            break
                        elif str.lower(is_overwrite) == 'n':
                            # skip
                            # 跳过
                            break
                        elif str.lower(is_overwrite) == 'all':
                            # overwrite for this time and set the overwrite flag to True
                            # 这一张图片覆写并将覆写标志置为真(即之后的所有图片全部覆写)
                            position_an_image(filename_withpath, positioned_path)
                            all_overwrite = True
                            break
                        # invalid input, ask again
                        # 输入不合法, 重新输入
                        else:
                            pass
        # if file is not compatible
        # 如果文件格式不支持
        else:
            print("Format not supported!")
            # show all supported formats
            # 显示所有支持的格式
            for one_format in compatible_formats:
                print(one_format)

    print("All completed!")


###------------------识别模块 recognition module------------------###

#==============================================================
# generate and save the encoding dictionary                                                              
# 生成和保存一个文件夹中人脸的'编码字典'
# @parameter:
# - known_path: the path which stores the known images for encoding. (e.g. 'src/known/')
#               保存待编码人脸图片的路径 (例: 'src/known/')
# @return: 
# - new_dict:   generated encoding dictionary | name -> str: encoding ->ndarray
#               生成的编码字典 | name -> str: encoding ->ndarray
def gen_sav_encodings_dict(known_path : str) -> dict:

    # if the encoding dictionary not exists
    # 如果'编码字典'文件不存在
    if not os.path.exists(json_path + encoding_json):
        # generate the encoding dictionary and modification record file
        # 第一次生成'编码字典'文件和'文件解析记录'文件

        # generate the encoding directory for the first time
        # 第一次生成'编码字典'

        # filename List under the path (all file and floder included)
        # 文件名的列表 (包括所有的文件和文件夹)
        known_image_name_list=os.listdir(known_path)

        # initialize the encoding dictionary
        # 初始化编码字典
        new_dict={}
        print("Generating known image encoding directory...")
        for one_file in known_image_name_list:
            if os.path.isdir(one_file) or (os.path.splitext(one_file)[1] not in compatible_formats):
                continue
            print("Generating encoding for " + one_file + " ...")
            known_image = face_recognition.load_image_file(known_path + one_file)
            new_dict[os.path.splitext(one_file)[0]] = (face_recognition.face_encodings(known_image)[0])
        
        # searialize ndarray (to save in the json file)
        # 将ndarray序列化, 以保存进json文件
        new_dict_save = {}
        for name in new_dict:
            new_dict_save[name] = new_dict[name].tolist()
        
        # save encoding dictionary to encoding dictionary file: json_path ('encoding.json' by default)
        # 保存'编码字典'至'编码字典'文件: json_path (默认文件为'encoding.json')
        # if json_path not exists, new it
        # 如果json_path不存在, 就创建它
        if not os.path.exists(json_path):
            os.makedirs(json_path)

        # write the serialized encoding dictionary into 'encoding.json'
        # 将序列化后的'编码字典'写入encoding.json
        with open(json_path + encoding_json, 'w', encoding='utf-8') as encoding_json_file:
            encoding_json_s = json.dumps(new_dict_save)
            encoding_json_file.write(encoding_json_s)

        # initialize the modification record file('modate.json' by default)
        # 初始化'文件解析记录'文件:modate_json(默认文件为'modate.json')
        # write it to modate_json
        # 写入mdate_json
        modate_dict = folder_manager_reina.parse_modate(known_path)
        folder_manager_reina.save_dict(modate_dict, json_path + modate_json)

    else:
        # read the modate_json and update, get the change dictionary
        # 读取文件解析记录并更新, 得到'变化字典'
        is_changed, change = folder_manager_reina.get_change_and_renew(known_path, json_path + modate_json)
        
        # read the old and serialized 'enoding dictionary'
        # 读取旧'编码字典'(序列化后)
        with open(json_path + encoding_json, 'r', encoding='utf-8') as encoding_file:
            old_json_save_s = encoding_file.read()
        old_dict_save = json.loads(old_json_save_s)

        # undo serialization to get the original ndarray
        # 反序列化, 获得原始ndarray
        old_dict = {}
        for name in old_dict_save:
            old_dict[name] = numpy.array(old_dict_save[name])
        
        # initialize new 'encoding dictionary' (inherit from the old one)
        # 初始化新'编码字典'(继承旧'编码字典')
        new_dict = old_dict
        # if file is not changed, there is no need for encoding dictionary to change.
        # 如果文件没有改变, 那么'编码字典'也无需改变
        if not is_changed:
            print("modate.json not changed, pass")
            pass
        
        # if file is changed, the 'encoding dictionary' should be changed according to it.
        # 如果文件改变, 则'编码字典'对应改变
        else:
            # load 'new' and 'deleted' from the change dictionary
            # 从'变化字典'中加载'new'和'deleted'
            new = change['new']
            deleted = change['deleted']

            # processing 'new' List
            # 处理'new'列表 
            if len(new) != 0:
                print("something newed: ")
                for new_filename in new:
                    # check the compatibility of the file format
                    # 检测文件格式是否支持, 如果不支持则跳过
                    if os.path.splitext(new_filename)[1] not in compatible_formats:
                        print(new_filename + ' is not supported, skip.')
                        continue
                    # save 'key:value's of every image in 'new' to new_dict
                    # 把'new'中的每一个图片的键值对收录进'new_dict'
                    print("processing(new) " + new_filename + " ...")
                    this_image = face_recognition.load_image_file(known_path + new_filename)
                    new_dict[os.path.splitext(new_filename)[0]] = face_recognition.face_encodings(this_image)[0]

            # processing 'deleted' List
            # 处理'deleted'列表
            if len(deleted) != 0:
                print("something deleted:")

                # check the compatibility of the file format
                # 检测文件格式是否支持, 如果不支持则跳过
                for deleted_filename in deleted:
                    if os.path.splitext(deleted_filename)[1] not in compatible_formats:
                        print(deleted_filename + ' is not supported, skip.')
                        continue
                    print("processing(delete) " + deleted_filename + " ...")

                    # delete 'key:value's of every image in 'deleted' from new_dict
                    # 把'deleted'中的每一个图片的键值对从'new_dict'移除
                    new_dict.pop(os.path.splitext(deleted_filename)[0]) 

            # serialize the new_dict
            # 序列化新字典
            new_dict_save = {}
            for name in new_dict:
                new_dict_save[name] = new_dict[name].tolist()

            #save new_dict into json file
            # 更改结束之后, 将序列化后的新字典保存到文件中
            with open(json_path + encoding_json, 'w', encoding='utf-8') as encoding_file:
                new_dict_s = json.dumps(new_dict_save)
                encoding_file.write(new_dict_s)

    # return
    # 返回新'编码字典'
    return new_dict


#==============================================================
# match a face with data in encoding dictionary                                                              
# 根据'编码字典'匹配一张人脸
# @parameter:
# - unknown_face_img:   cropped unknown face image (ndarray format)
#                       裁剪后的未知人脸图像(ndarray格式)
# - known_encoding_dict:    known encoding dictionary | {name: encoding}
#                           已知的编码字典 | {name -> str: encoding -> ndarray}
# @return: 
# - matched_distance:   2 dim list of matiched people and its distance | [matched_people ->str, min_face_distance -> int]
#                       匹配到的人与其distance的二维列表 | [matched_people -> str, min_face_distance -> int]
def face_people_match(unknown_face_img: numpy.ndarray, known_encoding_dict: dict) -> list:
    if len(face_recognition.face_encodings(unknown_face_img))!=0:
        # preparation of unknown_face
        # 对unknown_face的预处理
        unknown_image_encoding = face_recognition.face_encodings(unknown_face_img)[0]
    else:
        return None
    
    # initialize face distance and default matched people
    # 初始化face distance和默认的matched people
    min_face_distance = 99999
    matched_people='unknown'
    is_matched = False
    
    # compare one by one
    # 逐个对比
    for name in known_encoding_dict:
        results = face_recognition.face_distance([known_encoding_dict[name]], unknown_image_encoding)
        if results[0] < min_face_distance:
            min_face_distance = results[0]
            matched_people = name
            if min_face_distance <= fault_tolerance:
                is_matched = True
    
    # if can not be matched
    # 如果没有匹配到        
    if not is_matched:
        matched_people='unknown'
        min_face_distance = 99999

    # return the list of matched people's name and its distance
    # 返回匹配度最高的人名和distance的列表
    matched_distance = [matched_people, min_face_distance]
    return matched_distance


#==============================================================
# find all faces in one image, crop and recognize for each
# return the dictionary of name:[[xmin, xmax, ymin, ymax]]

# 找到一张图片中的所有人脸, 依次裁剪后识别, 返回识别结果 
# 返回人名与[[xmin, xmax, ymin, ymax], distance]的字典

# @parameter:
# - unknown_file_withpath:  image file with path, which will be recognized | str (e.g. 'src/unknown/unknown1.jpg')  
#                           待识别带路径的图片文件名 | str (例:'src/unknown/unknown1.jpg')  
# - known_encoding_dict:    known encoding dictionary
#                           已知的编码字典
#                           {name: encoding} -> str: ndarray
# @return: 
# - name__position_distance:    dictionary that stores recognition info
#                               保存识别信息的字典 
#                               {name:[xmin, xmax, ymin, ymax], distance} -> {str:[float, float, float, float], float}
def crop_and_recognize(unknown_file_withpath, known_encoding_dict):
    
    image = face_recognition.load_image_file(unknown_file_withpath)
    face_locations=face_recognition.face_locations(image)
    
    
    if len(face_locations) == 0:
        return None

    # face_locations eg:(139,283,325,97) (y1,x1,y2,x2)
    name__position_distance = {}
    for face in face_locations:
        y1=face[0]
        x1=face[1]
        y2=face[2]
        x2=face[3]
        xmin = min(x1,x2)
        ymin = min(y1,y2)
        xmax = max(x1,x2)
        ymax = max(y1,y2)
        croped_image=image[ymin:ymax, xmin:xmax]

        name_distance = face_people_match(croped_image, known_encoding_dict)
        if name_distance == None:
            continue

        # name:[[xmin, xmax, ymin, ymax], distance]
        name__position_distance[name_distance[0]] = [[xmin, xmax, ymin, ymax],name_distance[1]]
    return name__position_distance



#==============================================================
# recognize and draw results for one image
# 对一张图片进行识别, 并根据结果绘制图像

# @parameter:
# - unknown_file_withpath:  image file with path, which will be recognized | str (e.g. 'src/unknown/unknown1.jpg')  
#                           待识别带路径的图片文件名 | str (例:'src/unknown/unknown1.jpg')  
# - known_encoding_dict:    known encoding dictionary
#                           已知的编码字典
#                           {name: encoding} -> str: ndarray
# - recog_file_path:        path to store recogized image file
#                           保存识别后图片文件的路径
# @return: (no return)
def recognize_an_imge(unknown_file_withpath, known_encoding_dict, recog_file_path):
    
    # get filename
    # 获取文件名
    filename = os.path.split(unknown_file_withpath)[1]

    # open image
    # 打开图片
    unknown_image = cv2.imread(unknown_file_withpath)

    # get the data of recognition (Essential)
    # 获取识别信息 (关键步骤)
    # dict {name:[[xmin, xmax, ymin, ymax], distance]}
    name__position_distance = crop_and_recognize(unknown_file_withpath, known_encoding_dict)
    
    if name__position_distance != None:
        for name in name__position_distance.keys():
            
            # processing the data
            # 整理数据
            xmin = name__position_distance[name][0][0]
            xmax = name__position_distance[name][0][1]
            ymin = name__position_distance[name][0][2]
            ymax = name__position_distance[name][0][3]
            distance = name__position_distance[name][1]
            
            # draw a rectangle according to a face position
            # 根据人脸位置画矩形
            cv2.rectangle(unknown_image,(xmin,ymin),(xmax,ymax),(0,0,255),3)
            
            # edit attributes of the text
            # 编辑文字属性
            text_content_name = name
            text_content_distance = "{:.3f}".format(distance)
            text_position_name = (xmin, ymin-10)        #左上角名字
            text_position_distance = (xmin, ymax+25)    #左下角匹配度
            text_font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = 0.8
            text_color = (0,0,255)
            text_thickness = 2
            
            # place text
            # 放置文字
            cv2.putText(unknown_image, text_content_name, text_position_name, text_font, text_size, text_color, text_thickness)
            cv2.putText(unknown_image, text_content_distance, text_position_distance, text_font, text_size, text_color, text_thickness)
    
    # save the picture
    # 保存图片
    cv2.imwrite(recog_file_path + filename, unknown_image)


#==============================================================
# recognition flow control in a single folder
# 一个文件夹内批量生成识别图片的流程控制
#
# @parameter:
# - unknown_path:           path which stores unknown iamges 
#                           待识别文件夹的路径
#                           str (e.g. 'src/unknown/')  
# - recog_file_path:        path to store recogized image file 
#                           保存识别后图片文件的路径
#                           str (e.g. 'src/recognized/')  
# - known_path:             path which stores known images
#                           已知人脸图片文件的路径
#                           str (e.g. 'src/known/')
# @return: (no return)
def recognize_a_folder(unknown_path, recog_file_path, known_path):
    
    # generate the encoding dictionary
    # 生成已知人脸编码字典
    known_image_encodings_directory = gen_sav_encodings_dict(known_path)

    # get all filenames in the unknown_path folder 
    # 得到未知人脸文件夹内所有文件名
    file_in_raw_list = os.listdir(unknown_path)
    
    # create recog_file_path if not exists
    # 如果目标文件夹不存在则创建
    if not os.path.exists(recog_file_path):
        os.makedirs(recog_file_path)

    for raw_file in file_in_raw_list:

        # if it's a folder, skip
        # 检测是否为文件夹, 如果是则跳过
        if os.path.isdir(raw_file):
            continue

        # check the compatibility of the file format
        # 检测文件格式是否支持, 如果不支持则跳过
        if os.path.splitext(raw_file)[1] not in compatible_formats:
            continue 
        print("recognizing for" + raw_file)
        recognize_an_imge(unknown_path + raw_file, known_image_encodings_directory, recog_file_path)
    
    print("Complete!")
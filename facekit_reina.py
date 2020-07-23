'''
@author Reina
@desc 基于opencv与face_recognition开源项目的自定义模块
@date 2020/7/20
描述 :
包含两个子模块: 人脸定位模块和人脸识别模块
人脸定位: 
- generate_face_positioned_img函数: 为单张图片进行定位和绘制
- start_position函数: 一个文件夹内批量生成定位图片的流程控制
人脸识别:
- gen_sav_encodings_dict函数: 生成并保存已知'编码字典'
- face_people_match函数: 根据'编码字典', 匹配一张人脸
- crop_and_recognize函数: 找到一张图片中的所有人脸, 依次裁剪后识别, 返回识别结果
- generate_face_recognition_img函数: 对一张图片进行识别, 并根据结果绘制图像
- start_recognition函数: 一个文件夹内批量生成识别图片的流程控制
'''


#coding=utf-8
import face_recognition
import folder_manager_reina
from cv2 import cv2     # WSL要求, 非WSL直接import cv2
import os
import json
import numpy


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


# reference of coordinate(the same as opencv)
# 坐标系参考(同opevcv)
# ######################---------→ x
# #                    #
# #                    #
# #                    #
# #                    #
# #       IMAGE        #
# #                    #
# #                    #
# #                    #
# #                    #
# ######################
# |
# |
# |
# ↓
# y

### 定位模块 position module ###

### ------------------------------------------------------------------------------------    
# generate position for one image                                                       
# 为单张图片进行定位和绘制                                                               
def generate_face_positioned_img(path, filename, positioned_path):
    image = face_recognition.load_image_file(path + filename)
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
        print(xmin,xmax,ymin,ymax)
        cv2.rectangle(image,(xmin,ymin),(xmax,ymax),(255,0,0),3)

    #os.mkdir(positioned_path)
    cv2.imwrite(positioned_path+filename,cv2.cvtColor(image, cv2.COLOR_RGB2BGR))


#=======================================================
# position flow control                                                                 
# 一个文件夹内批量生成定位图片的流程控制                                                                    
def start_position(raw_image_path, positioned_image_path):
    
    # directory of source files
    # 源文件的目录
    #raw_image_path='src/known/'

    # directory of output files
    # 输出文件的目录
    #positioned_image_path=raw_image_path+'positioned/'

    # filename List under the path (all file and floder included)
    # 文件名的列表 (包括所有的文件和文件夹)
    image_name_list=os.listdir(raw_image_path)

    if not os.path.exists(positioned_image_path):
        os.mkdir(positioned_image_path)

    all_overwrite = False

    for ifilename in image_name_list:
        if os.path.isdir(raw_image_path + ifilename):
            continue
        print("processing " + ifilename + ' ...')
        if (os.path.splitext(ifilename)[1] in compatible_formats):
            if (ifilename not in os.listdir(positioned_image_path)):
                generate_face_positioned_img(raw_image_path, ifilename, positioned_image_path)
            else:
                if all_overwrite == True:
                    generate_face_positioned_img(raw_image_path, ifilename, positioned_image_path)
                else:
                    while True:
                        is_overwrite = input(ifilename+" already exists, do you want to overwrite it? (Y/n/all): ")
                        if str.lower(is_overwrite) == 'y':
                            generate_face_positioned_img(raw_image_path, ifilename, positioned_image_path)
                            break
                        elif str.lower(is_overwrite) == 'n':
                            break
                        elif str.lower(is_overwrite) == 'all':
                            generate_face_positioned_img(raw_image_path, ifilename, positioned_image_path)
                            all_overwrite = True
                            break
                        else:
                            pass
        else:
            print("Format not supported!")
            while True:
                is_show_compatible_formats = input('Show all supported formats? (Y/n): ')
                if str.lower(is_show_compatible_formats) == 'y':
                    for one_format in compatible_formats:
                        print(one_format)
                    break
                elif str.lower(is_show_compatible_formats) == 'n':
                        break
                else:
                    pass

    print("All completed!")


### 定位识别模块 position and recogition module ###

#=======================================================
# 生成并保存已知'编码字典'
def gen_sav_encodings_dict(known_path):

    # 如果'编码字典'文件不存在
    if not os.path.exists(json_path + encoding_json):
        # 第一次生成'编码字典'文件和'文件解析记录'文件

        # 第一次生成'编码字典'

        # filename List under the path (all file and floder included)
        # 文件名的列表 (包括所有的文件和文件夹)
        known_image_name_list=os.listdir(known_path)

        #初始化编码字典
        new_dict={}
        print("Generating known image encoding directory...")
        for one_file in known_image_name_list:
            if os.path.isdir(one_file) or (os.path.splitext(one_file)[1] not in compatible_formats):
                continue
            print("Generating encoding for " + one_file + " ...")
            known_image = face_recognition.load_image_file(known_path + one_file)
            new_dict[os.path.splitext(one_file)[0]] = (face_recognition.face_encodings(known_image)[0])
        
        # 将ndarray序列化, 以保存进json文件
        new_dict_save = {}
        for name in new_dict:
            new_dict_save[name] = new_dict[name].tolist()

        # 保存'编码字典'至'编码字典'文件: encoding.json
        # 如果json_path不存在, 就创建它
        if not os.path.exists(json_path):
            os.mkdir(json_path)
        # 将序列化后的'编码字典'写入encoding.json
        with open(json_path + encoding_json, 'w', encoding='utf-8') as encoding_json_file:
            encoding_json_s = json.dumps(new_dict_save)
            encoding_json_file.write(encoding_json_s)

        # 初始化'文件解析记录'文件: modate.json
        # 写入modate.json
        modate_dict = folder_manager_reina.parse_modate(known_path)
        folder_manager_reina.save_dict(modate_dict, json_path + modate_json)

    else:
        
        # 读取文件解析记录并更新, 得到'变化字典'
        is_changed, change = folder_manager_reina.get_change_and_renew(known_path, json_path + modate_json)
        
        # 读取旧'编码字典'(序列化后)
        with open(json_path + encoding_json, 'r', encoding='utf-8') as encoding_file:
            old_json_save_s = encoding_file.read()
        old_dict_save = json.loads(old_json_save_s)

        #反序列化, 获得原始ndarray
        old_dict = {}
        for name in old_dict_save:
            old_dict[name] = numpy.array(old_dict_save[name])
        
        # 初始化新'编码字典'(继承旧'编码字典')
        new_dict = old_dict
        # 如果文件没有改变, 那么'编码字典'也无需改变
        if not is_changed:
            print("modate.json not changed, pass")
            pass
        
        # 如果文件改变, 则'编码字典'对应改变
        else:
            # 从'变化字典'中加载'new'和'deleted'
            new = change['new']
            deleted = change['deleted']

            # 处理'new'列表
            if len(new) != 0:
                print("something newed: ")
                for new_file_name in new:
                    # 检测文件格式是否支持, 如果不支持则跳过
                    if os.path.splitext(new_file_name)[1] not in compatible_formats:
                        print(new_file_name + ' is not supported, skip.')
                        continue
                    # 把'new'中的每一个图片的键值对收录进'new_dict'
                    print("processing(new) " + new_file_name + " ...")
                    this_image = face_recognition.load_image_file(known_path + new_file_name)
                    new_dict[os.path.splitext(new_file_name)[0]] = face_recognition.face_encodings(this_image)[0]

            # 处理'deleted'列表
            if len(deleted) != 0:
                print("something deleted:")
                # 检测文件格式是否支持, 如果不支持则跳过
                
                for deleted_file_name in deleted:
                    if os.path.splitext(deleted_file_name)[1] not in compatible_formats:
                        print(deleted_file_name + ' is not supported, skip.')
                        continue
                    print("processing(delete) " + deleted_file_name + " ...")
                    # 把'deleted'中的每一个图片的键值对从'new_dict'移除
                    new_dict.pop(os.path.splitext(deleted_file_name)[0]) 

            # 序列化新字典
            new_dict_save = {}
            for name in new_dict:
                new_dict_save[name] = new_dict[name].tolist()

            # 更改结束之后, 将序列化后的新字典保存到文件中
            with open(json_path + encoding_json, 'w', encoding='utf-8') as encoding_file:
                new_dict_s = json.dumps(new_dict_save)
                encoding_file.write(new_dict_s)
            
    # 返回新'编码字典'
    return new_dict


#=======================================================
# 根据'编码字典', 匹配一张人脸
def face_people_match(unknown_face_img, known_image_encoding_directory):
    if len(face_recognition.face_encodings(unknown_face_img))!=0:
        #对unknown_face的预处理
        unknown_image_encoding = face_recognition.face_encodings(unknown_face_img)[0]
    else:
        return None
    #初始化face distance和默认的matched people
    min_face_distance = 99999
    matched_people='unknown'
    is_matched = False
    #逐个对比
    for name in known_image_encoding_directory:
        results = face_recognition.face_distance([known_image_encoding_directory[name]], unknown_image_encoding)
        if results[0] < min_face_distance:
            min_face_distance = results[0]
            matched_people = name
            if min_face_distance <= 0.4:
                is_matched = True
    #如果没有匹配到        
    if not is_matched:
        matched_people='unknown'
        min_face_distance = 99999
    # 返回匹配度最高的人名和distance的列表
    return [matched_people, min_face_distance]



#=======================================================
# find all faces in one image, crop and recognize for each
# return the dictionary of name:[[xmin, xmax, ymin, ymax]]
# 找到一张图片中的所有人脸, 依次裁剪后识别, 返回识别结果 
# 返回人名与[[xmin, xmax, ymin, ymax], distance]的字典
def crop_and_recognize(unknown_file_withpath, known_image_encoding_directory):
    
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

        name_distance = face_people_match(croped_image, known_image_encoding_directory)
        if name_distance == None:
            continue

        # name:[[xmin, xmax, ymin, ymax], distance]
        name__position_distance[name_distance[0]] = [[xmin, xmax, ymin, ymax],name_distance[1]]
    return name__position_distance


#=======================================================    
# recognize and draw results for one image
# 对一张图片进行识别, 并根据结果绘制图像
def generate_face_recognition_img(unknown_file_withpath, known_image_encoding_directory, recog_file_path):
    
    #获取文件名
    file_name = os.path.split(unknown_file_withpath)[1]

    #打开图片
    unknown_image = cv2.imread(unknown_file_withpath)

    #获取识别信息 name:[[xmin, xmax, ymin, ymax], distance]
    name__position_distance = crop_and_recognize(unknown_file_withpath, known_image_encoding_directory)
    
    if name__position_distance != None:
        for name in name__position_distance.keys():
            # 整理数据
            xmin = name__position_distance[name][0][0]
            xmax = name__position_distance[name][0][1]
            ymin = name__position_distance[name][0][2]
            ymax = name__position_distance[name][0][3]
            distance = name__position_distance[name][1]
            # 根据人脸位置画矩形
            cv2.rectangle(unknown_image,(xmin,ymin),(xmax,ymax),(0,0,255),3)
            # 编辑文字属性
            text_content_name = name
            text_content_distance = "{:.3f}".format(distance)
            text_position_name = (xmin, ymin-10)        #左上角名字
            text_position_distance = (xmin, ymax+25)    #左下角匹配度
            text_font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = 0.8
            text_color = (0,0,255)
            text_thickness = 2
            #放置文字
            cv2.putText(unknown_image, text_content_name, text_position_name, text_font, text_size, text_color, text_thickness)
            cv2.putText(unknown_image, text_content_distance, text_position_distance, text_font, text_size, text_color, text_thickness)
    cv2.imwrite(recog_file_path + file_name, unknown_image)


#=======================================================
# recognition flow control in a single folder
# 一个文件夹内批量生成识别图片的流程控制
# 
def start_recognition(raw_image_path, recognized_image_path, known_image_path):
    
    #生成已知人脸编码字典
    known_image_encodings_directory = gen_sav_encodings_dict(known_image_path)

    #得到源文件夹内所有文件
    file_in_raw_list = os.listdir(raw_image_path)
    
    #如果目标文件夹不存在则创建
    if not os.path.exists(recognized_image_path):
        os.mkdir(recognized_image_path)

    for raw_file in file_in_raw_list:
        # 检测是否为文件夹, 如果是则跳过
        if os.path.isdir(raw_file):
            continue
        # 检测文件格式是否支持, 如果不支持则跳过
        if os.path.splitext(raw_file)[1] not in compatible_formats:
            continue 
        print("recognizing for" + raw_file)
        generate_face_recognition_img(raw_image_path + raw_file, known_image_encodings_directory, recognized_image_path)
    
    print("Complete!")
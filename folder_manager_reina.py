'''
- parse_modate: 解析文件修改时间
- save_dict: 将可以序列化的字典保存到文件中
- find_out_change: 根据新旧字典, 生成并返回'变化字典', 描述文件夹内容的增(改)删
'''

import os
import json

def parse_modate(target_folder_path):
    
    # 得到文件夹中的所有文件和子文件夹
    file_list_with_dir = os.listdir(target_folder_path)
    
    # 过滤掉子文件夹, 留下文件
    file_list_without_dir = []
    for document in file_list_with_dir:
        if not os.path.isdir(document):
            file_list_without_dir.append(document)

    # 初始化`文件名:修改时间`字典
    name__modate = {}

    # 遍历填充字典
    for file in file_list_without_dir:
        modate = os.path.getmtime(target_folder_path + file)
        name__modate[file] = modate

    # 返回`文件名:修改时间`字典
    return name__modate

# 将字典写入文件
def save_dict(target_dict, save_filename_with_path):
    # 调用json模块, 将字典生成特定的json字符串
    js_dict = json.dumps(target_dict)
    # 打开要写入的文件
    file_modate = open(save_filename_with_path , 'w')
    # 将json对象写入文件
    file_modate.write(js_dict)
    # 关闭文件
    file_modate.close()

def get_change_and_renew(target_folder_path, json_file_with_path):
    # 如果旧字典不存在
    if not os.path.exists(json_file_with_path):
        # 新建空字典文件
        with open(json_file_with_path, 'w', encoding="utf-8") as json_file:
            pass
    # 打开保存旧字典的json文件
    with open(json_file_with_path, 'r', encoding="utf-8") as json_file:
        old_name__modate_s = json_file.read()
    # 获取旧字典
    old_name__modate = json.loads(old_name__modate_s)
    # 获取新字典
    new_name__modate = parse_modate(target_folder_path)
    # 保存新字典
    save_dict(new_name__modate, json_file_with_path)

    # 定义描述变化字典, 包含'new', 'deleted'两个键, 每个键由对应状态的文件名组成的列表作为值
    change = {'new': [], 'deleted': []}

    #如果旧字典不为空
    if old_name__modate != None:

        # 获取'new'的值
        for mk_new_name__modate in new_name__modate.keys():
            
            #设置标志位
            is_new = True
            
            # 如果新字典的一个键在旧字典的键中存在
            if mk_new_name__modate in old_name__modate.keys():
                # 并且相同键对应的值相同
                if new_name__modate[mk_new_name__modate] == old_name__modate[mk_new_name__modate]:
                    # 不是新的键值对
                    is_new = False

            # 如果是新的键值对
            if is_new:
                # 加入'变化'字典中的'new'列表中
                change['new'].append(mk_new_name__modate)

        # 获取'deleted'的值

        is_deleted = False
        for mk_old_name__modate in old_name__modate.keys():
            # 如果旧键在新字典中找不到
            if mk_old_name__modate not in new_name__modate.keys():
                    # 被删除
                    is_deleted = True
                
            # 如果是新的键值对
            if is_deleted:
                # 加入'变化'字典中的'deleted'列表中
                change['deleted'].append(mk_old_name__modate)


        is_changed = False
        if is_new or is_deleted:
            is_changed = True
    
    # 如果旧字典为空
    else:
        # 变化判断为真
        is_changed = True
        # 把新字典中所有键值对加入'new'列表中
        for mk_new_name__modate in new_name__modate.keys():
            change['new'].append(mk_new_name__modate)

    # 返回变化判断, 变化字典 eg. True, {'new':[file3, file4], 'deleted':[file1, file2]}
    return is_changed, change




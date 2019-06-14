from celery import Celery
import time
import os
import re
import pickle
import numpy as np
import cv2
import multiprocessing as mp
from multiprocessing import current_process


app = Celery()

app.config_from_object("celeryconfig")

rev = []


def get_file_name(path):

    '''
    Args: path to list;  Returns: path with filenames
    '''

    filenames = os.listdir(path)
    path_filenames = []
    filename_list = []

    for file in filenames:

        if 'sift' not in file:
            if not file.startswith('.'):
                path_filenames.append(os.path.join(path, file))
                filename_list.append(file)

    return path_filenames


# 定义任务分割的函数
def task_split(re_list, count):
    result_list = []
    temp_list = []
    for re_index, re_ele in enumerate(re_list):
        if (re_index % count) == 0:
            if len(temp_list) > 0:
                result_list.append(temp_list.copy())
                temp_list.clear()
                temp_list.append(re_ele)
            else:
                temp_list.append(re_ele)

        else:
            temp_list.append(re_ele)

    if len(temp_list) <= count:
        result_list.append(temp_list)

    return result_list


def get_score(des1, des2):
    # FLANN parameters
    start_time = time.time()
    index_params = dict(algorithm=1, trees=1)
    search_params = dict(checks=20)  # or pass empty dictionary
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    end_time = time.time()
    # print(len(matches))

    matchesMask = [[0, 0] for i in range(len(matches))]

    count = 0

    for i, (m, n) in enumerate(matches):
        if m.distance < 0.7 * n.distance:
            matchesMask[i] = [1, 0]
            count += 1

    # print(end_time - start_time)

    return count


def get_best_match(re_des, search_pic_list):
    temp_score = 0
    temp_id = 0

    for e_des_dic in search_pic_list:

        e_item_id = e_des_dic['item_id']
        e_des = e_des_dic['pic_features']
        # print(e_item_id)
        e_score = get_score(re_des, e_des)

        if e_score > temp_score:
            temp_id = e_item_id
            temp_score = e_score

    # result_dict['item_id'] = temp_id

    return temp_id


def my_calculate(re_des, ever_list):
    temp_score = 0
    temp_id = 0
    # print("jisuan")
    for e_des_dic in ever_list:

        e_item_id = e_des_dic['item_id']
        e_des = e_des_dic['pic_features']
        print("==============================================")

        # print(e_item_id)
        print(e_item_id)
        e_score = get_score(re_des, e_des)

        print(e_score)

        if e_score > temp_score:
            temp_id = e_item_id
            temp_score = e_score

    return temp_id


def callback_log(rev_val):
    rev.append(rev_val)
    # print(rev_val)


# 定义全局变量
search_pics_list = []

if os.path.exists("/home/slaver-0/s_features/"):
    pic_files = get_file_name("/home/slaver-0/s_features/")
    for pic_file in pic_files:
        # print(pic_file)
        print("read the files")

        item_id = re.findall("([0-9]{1,8})", pic_file, re.S)[-1]

        # print(item_id)
        #
        # print(type(item_id))

        # 反序列化
        with open('/home/slaver-0/s_features/{}.pkl'.format(item_id), 'rb') as f:
            des = pickle.load(f)
            pic_info = {"item_id": item_id, "pic_features": des}
            search_pics_list.append(pic_info)

elif os.path.exists("/home/slaver-1/s_features/"):
    pic_files = get_file_name("/home/slaver-1/s_features/")
    for pic_file in pic_files:
        # print(pic_file)
        # print("read the files")
        # print(pic_file)

        item_id = re.findall("([0-9]{1,8})", pic_file, re.S)[-1]

        # print(item_id)
        #
        # print(type(item_id))
        # 反序列化
        with open('/home/slaver-1/s_features/{}.pkl'.format(item_id), 'rb') as f:
            des = pickle.load(f)
            pic_info = {"item_id": item_id, "pic_features": des}
            search_pics_list.append(pic_info)

elif os.path.exists("/home/slaver-2/s_features/"):
    pic_files = get_file_name("/home/slaver-2/s_features/")
    for pic_file in pic_files:
        # print(pic_file)
        # print("read the files")
        # print(pic_file)

        item_id = re.findall("([0-9]{1,8})", pic_file, re.S)[-1]

        # print(item_id)
        #
        # print(type(item_id))
        # 反序列化
        with open('/home/slaver-2/s_features/{}.pkl'.format(item_id), 'rb') as f:
            des = pickle.load(f)
            pic_info = {"item_id": item_id, "pic_features": des}
            search_pics_list.append(pic_info)

else:
    pic_files = get_file_name("/home/linlinan/s_features/")
    for pic_file in pic_files:
        # print(pic_file)
        print("read the files")

        item_id = re.findall("([0-9]{1,8})", pic_file, re.S)[-1]

        # print(item_id)
        #
        # print(type(item_id))
        # 反序列化
        with open('/home/linlinan/s_features/{}.pkl'.format(item_id), 'rb') as f:
            des = pickle.load(f)
            pic_info = {"item_id": item_id, "pic_features": des}
            search_pics_list.append(pic_info)


# slaver-0: worker
@app.task
def slaver_0_search(re_params):
    global pic_files, search_pics_list

    print(len(pic_files))
    print(len(search_pics_list))
    current_process()._config = {'semprefix': '/mp'}

    re_np = np.array(re_params, dtype=np.float32)

    re_des = re_np.reshape(-1, 128)

    task_split_list = task_split(search_pics_list, 400)

    curr_proc = mp.current_process()
    curr_proc.daemon = False
    p = mp.Pool(mp.cpu_count())
    curr_proc.daemon = True

    for i in task_split_list:
        p.apply_async(my_calculate, args=(re_des, i), callback=callback_log)
    p.close()
    p.join()

    print("after rev:", rev)

    # temp_id = get_best_match(re_des, search_pics_list)
    # print(len(re_params))

    return rev


# slaver-1: worker
@app.task
def slaver_1_search(re_params):
    global pic_files, search_pics_list

    # print(len(pic_files))

    # for e in pic_files:
    #     print(e)
    # print(len(search_pics_list))

    current_process()._config = {'semprefix': '/mp'}

    re_np = np.array(re_params, dtype=np.float32)

    re_des = re_np.reshape(-1, 128)

    task_split_list = task_split(search_pics_list, 400)

    curr_proc = mp.current_process()
    curr_proc.daemon = False
    p = mp.Pool(mp.cpu_count())
    curr_proc.daemon = True

    for i in task_split_list:

        print("xunhuan=====================================================")
        print(len(i))
        print(i[0]['item_id'])
        p.apply_async(my_calculate, args=(re_des, i), callback=callback_log)
    p.close()
    p.join()

    print("after rev:", rev)

    # temp_id = get_best_match(re_des, search_pics_list)
    # print(len(re_params))

    return rev


# slaver-2: worker
@app.task
def slaver_2_search(re_params):
    global pic_files, search_pics_list
    current_process()._config = {'semprefix': '/mp'}

    re_np = np.array(re_params, dtype=np.float32)

    re_des = re_np.reshape(-1, 128)

    task_split_list = task_split(search_pics_list, 400)

    curr_proc = mp.current_process()
    curr_proc.daemon = False
    p = mp.Pool(mp.cpu_count())
    curr_proc.daemon = True

    for i in task_split_list:
        p.apply_async(my_calculate, args=(re_des, i), callback=callback_log)
    p.close()
    p.join()

    print("after rev:", rev)

    # temp_id = get_best_match(re_des, search_pics_list)
    # print(len(re_params))

    return rev


# slaver-2: worker
@app.task
def slaver_3_search(re_params):
    global pic_files, search_pics_list
    current_process()._config = {'semprefix': '/mp'}

    re_np = np.array(re_params, dtype=np.float32)

    re_des = re_np.reshape(-1, 128)

    task_split_list = task_split(search_pics_list, 40)

    curr_proc = mp.current_process()
    curr_proc.daemon = False
    p = mp.Pool(mp.cpu_count())
    curr_proc.daemon = True

    for i in task_split_list:
        p.apply_async(my_calculate, args=(re_des, i), callback=callback_log)
    p.close()
    p.join()

    # print(type(rev[0]))

    print("after rev:", rev)

    # temp_id = get_best_match(re_des, search_pics_list)
    # print(len(re_params))

    return rev



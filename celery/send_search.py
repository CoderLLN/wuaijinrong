from celery import Celery
import cv2
import numpy as np
import re
import pickle
import os

app = Celery()

app.config_from_object("celeryconfig")


# def get_file_name(path):
#     '''''
#     Args: path to list;  Returns: path with filenames
#     '''
#     filenames = os.listdir(path)
#
#     path_filenames = []
#     filename_list = []
#     for file in filenames:
#
#         if 'sift' not in file:
#             if not file.startswith('.'):
#                 path_filenames.append(os.path.join(path, file))
#                 filename_list.append(file)
#
#     return path_filenames
#
#
# pic_files = get_file_name("/home/linlinan/yinzhang_features/")
#
# search_pics_list = []
#
# for pic_file in pic_files:
#     # print(pic_file)
#
#     item_id = re.findall("([0-9]{1,8})", pic_file, re.S)[-1]
#
#     # 反序列化
#     with open('/home/linlinan/yinzhang_features/{}.pkl'.format(item_id), 'rb') as f:
#         des = pickle.load(f)
#         pic_info = {"item_id": item_id, "pic_features": des}
#         search_pics_list.append(pic_info)


def get_score(des1, des2):
    # FLANN parameters
    # start_time = time.time()
    index_params = dict(algorithm=1, trees=1)
    search_params = dict(checks=20)  # or pass empty dictionary
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # end_time = time.time()
    # print(len(matches))

    matchesMask = [[0, 0] for i in range(len(matches))]

    count = 0

    for i, (m, n) in enumerate(matches):
        if m.distance < 0.7 * n.distance:
            matchesMask[i] = [1, 0]
            count += 1

    # print(end_time - start_time)

    return count


def get_best_match(re_des, result_list_dict):
    # global search_pics_list
    temp_score = 0
    temp_id = 0

    for e_des_dic in result_list_dict:

        e_item_id = e_des_dic['item_id']
        e_des = e_des_dic['pic_features']
        # print(e_item_id)
        e_score = get_score(re_des, e_des)

        if e_score > temp_score:
            temp_id = e_item_id
            temp_score = e_score

    # result_dict['item_id'] = temp_id

    return temp_id


print("into main function")

sift = cv2.xfeatures2d.SIFT_create(nfeatures=500)
re_img = cv2.imread("/home/linlinan/yinzhang_source/147.jpg")
first_kp, first_feature = sift.detectAndCompute(re_img, None)

print(type(first_feature[0][0]))

test_ff = first_feature.tolist()

result_slaver_0 = app.send_task("tasks.slaver_0_search", [test_ff])
#
result_slaver_1 = app.send_task("tasks.slaver_1_search", [test_ff])

result_slaver_2 = app.send_task("tasks.slaver_2_search", [test_ff])


result_list_0 = result_slaver_0.get(timeout=0)

result_list_1 = result_slaver_1.get(timeout=0)

result_list_2 = result_slaver_2.get(timeout=0)

result_list = result_list_0 + result_list_1 + result_list_2


print(type(result_list))

# result_list_dict = []

# print(len(result_list))

search_pics_list_temp_list = []

for e in result_list:
    with open('/home/linlinan/yinzhang_features/{}.pkl'.format(e), 'rb') as f:
        des = pickle.load(f)
        pic_info = {"item_id": e, "pic_features": des}
        search_pics_list_temp_list.append(pic_info)

temp_id = get_best_match(first_feature, search_pics_list_temp_list)

print(temp_id)

print("test")



# -*- coding:utf8 -*-

import tornado.ioloop
import tornado.web
from PIL import Image
import io
from mysql import connector
import numpy as np
import cv2
import time
import pickle
import os
import tornado
import re
from celery import Celery


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


def get_item_path(item_id):

    re_path = ''
    read_sql = 'select CONCAT from yinzhang where ID = {}'.format(item_id)

    conn = connector.connect(host="10.10.10.77", user="linlinan", password="ed35sdef123",
                             database="epai_spider_2018_"
                                      "linlinan",
                             charset="utf8")

    cur = conn.cursor()

    cur.execute(read_sql)

    result_set = cur.fetchall()

    if result_set:
        for row in result_set:
            # print(row[0])
            re_path = row[0]

    cur.close()
    conn.close()

    return re_path


class Picture_search_handler(tornado.web.RequestHandler):
    app = Celery()
    app.config_from_object("celeryconfig")

    sift = cv2.xfeatures2d.SIFT_create(nfeatures=1000)

    def get(self):
        self.write('<html><body><form action="/" enctype="multipart/form-data" method="post" name="up_load">'
                   '<input type="file" name="message">'
                   '<input type="submit" value="Submit">'
                   '</form></body></html>')

    def post(self):
        fileinfo = self.request.files["message"][0]

        im = Image.open(io.BytesIO(fileinfo['body']))
        if len(im.split()) == 3:
            b, g, r = im.split()
            im = Image.merge("RGB", (r, g, b))
            open_cv_image = np.array(im)

            kp1, nhist = self.sift.detectAndCompute(open_cv_image, None)

            print(len(nhist))

            test_ff = nhist.tolist()

            # result_slaver_0 = self.app.send_task("tasks.slaver_0_search", [test_ff])
            #
            result_slaver_1 = self.app.send_task("tasks.slaver_1_search", [test_ff])

            # result_slaver_2 = self.app.send_task("tasks.slaver_2_search", [test_ff])
            #
            # result_slaver_3 = self.app.send_task("tasks.slaver_3_search", [test_ff])

            # result_list_0 = result_slaver_0.get(timeout=0)

            result_list_1 = result_slaver_1.get(timeout=0)

            # result_list_2 = result_slaver_2.get(timeout=0)
            #
            # result_list_3 = result_slaver_3.get(timeout=0)

            # result_list = result_list_0 + result_list_1 + result_list_2 + result_list_3

            result_list = result_list_1

            print(type(result_list))
            print(len(result_list))

            # self.write(item_info)

            search_pics_list_temp_list = []

            for e in result_list:
                with open('/home/linlinan/yinzhang_features/{}.pkl'.format(e), 'rb') as f:
                    des = pickle.load(f)
                    pic_info = {"item_id": e, "pic_features": des}
                    search_pics_list_temp_list.append(pic_info)

            temp_id = get_best_match(nhist, search_pics_list_temp_list)

            print(temp_id)

            # print(temp_id)
            #
            pic_path = get_item_path(item_id=temp_id)

            self.write('<html><body>'
                       '<img src="{}" height = "500" width = "500">'
                       '</body></html>'.format(pic_path))

        else:
            self.write('<html><body>please upload the jpg'
                       '<form action="/" enctype="multipart/form-data" method="post" name="up_load">'
                       '<input type="file" name="message">'
                       '<input type="submit" value="Submit">'
                       '</form></body></html>')


if __name__ == "__main__":
    print('into main function')
    # tornado.options.parse_command_line()
    picture_search_application = tornado.web.Application([(r'/', Picture_search_handler)], debug=False)

    http_server = tornado.httpserver.HTTPServer(picture_search_application)

    http_server.bind(9999)
    http_server.start(0)
    # [I 150610 10:42:05 process:115] Starting 4 processes
    tornado.ioloop.IOLoop.instance().start()



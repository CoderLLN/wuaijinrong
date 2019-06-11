# -*- coding: utf-8 -*-
import requests
import time
import threading

from mysql import connector
import schedule


tabel_name_str = ""


def write_data_to_mysql(table_name, price, date_time):

    price_tt = str(price)

    price_str = price_tt.replace(".", "")

    print(price_str)

    insertsql = 'INSERT INTO `S{}` (`PRICE`, `DATE_TIME`) VALUES ({}, {})'.format(table_name, int(price_str), date_time)

    # insertvalues = [(int(price_str), int(date_time))]

    print(insertsql)

    # try:
    cnx = connector.connect(host="94.191.126.86", user="root", password="", database="wuaijinrong",
                        charset="utf8")

    db0 = cnx.cursor()

    db0.execute(insertsql)

    cnx.commit()
    db0.close()


def fun_timer_1():

    ts = time.time()

    url = 'https://hq.sinajs.cn/?_=' + str(ts) + '/&list=hf_XAU'

    try:

        response = requests.get(url)

        data_list = response.text.split(",")

        time_str = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())

        stand_time_str = time_str.replace("-", "").replace(" ", "")

        print("=" * 50)

        print(data_list[2])
        print(stand_time_str)

        global tabel_name_str

        write_data_to_mysql(tabel_name_str, data_list[2], stand_time_str)

    except:
        pass

    global timer_1

    timer_1 = threading.Timer(1, fun_timer_1)
    timer_1.start()


#
def day_job():

    global tabel_name_str

    time_str = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())

    print(time_str)

    tabel_name_str = time_str.split(" ")[0].replace("-", "")

    print(tabel_name_str)

    # 这里的建表语句需要每天执行一次
    tablesql = "Create Table If Not Exists `S{}`(Id INT(6) primary key auto_increment," \
               "PRICE INT(6),DATE_TIME  varchar(50))".format(tabel_name_str)

    # insertvalues = [(int(price_str), int(date_time))]

    print(tablesql)

    # try:
    cnx = connector.connect(host="94.191.126.86", user="root", password="", database="wuaijinrong",
                        charset="utf8")

    db0 = cnx.cursor()

    db0.execute(tablesql)

    cnx.commit()
    db0.close()


if __name__ == "__main__":
    print("into main function")

    # 这个和建表分开即可
    timer_1 = threading.Timer(1, fun_timer_1)

    timer_1.start()

    # 这里是每天定时的建表格
    schedule.every().day.at("10:05").do(day_job)

    while True:
        schedule.run_pending()
        time.sleep(1)



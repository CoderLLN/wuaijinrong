# -*- coding: utf-8 -*-
from mysql import connector
import schedule
import time

tabel_name_str = ""


def minute_job():

    global tabel_name_str

    print("fenzhong job")

    time_str = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())

    time_str_str = time_str.replace(" ", "").replace("-", "")

    print(time_str_str)

    if time_str_str[11:12] == "00":
        index_min_str = str(int(time_str_str[0:12]) - 42) + "59"
        the_time_str = str(int(time_str_str[0:12]) - 41) + "00"
    else:
        index_min_str = str(int(time_str_str[0:12]) - 2) + "59"
        the_time_str = str(int(time_str_str[0:12]) - 1) + "00"

    index_max_str = str(int(time_str_str[0:12])) + "00"

    print(index_min_str)
    print(the_time_str)
    print(index_max_str)

    price_start = 0
    price_end = 0
    price_max = 0
    price_min = 10000000

    try:

        select_sql = "select * from S{} where DATE_TIME > {} and DATE_TIME < {}".format(tabel_name_str,
                                                                                       index_min_str, index_max_str)

        print(select_sql)
        # 这里我们建立一次数据库链接即可

        cnx = connector.connect(host="94.191.126.86", user="root", password="Linlinan123!", database="wuaijinrong",
                            charset="utf8")

        db0 = cnx.cursor()

        db0.execute(select_sql)

        result_set = db0.fetchall()

        if result_set:
            price_start = result_set[0][1]
            price_end = result_set[-1][1]

            for row in result_set:
                if row[1] > price_max:
                    price_max = row[1]
                if row[1] < price_min:
                    price_min = row[1]

        print(price_start, price_end, price_max, price_min)

        write_sql = "INSERT INTO `M{}` (`START_PRICE`,`END_PRICE`,`MAX_PRICE`,`MIN_PRICE`, `DATE_TIME`) " \
                    "VALUES ({},{},{},{},{})".format(tabel_name_str, price_start, price_end, price_max, price_min, the_time_str)

        print(write_sql)

        db0.execute(write_sql)

    except:

        pass

    cnx.commit()
    db0.close()


#
def day_job():

    global tabel_name_str

    time_str = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())

    print(time_str)

    tabel_name_str = time_str.split(" ")[0].replace("-", "")

    print(tabel_name_str)

    # 这里的建表语句需要每天执行一次
    tablesql = "Create Table If Not Exists `M{}`(Id INT(6) primary key auto_increment," \
               "START_PRICE INT(6), END_PRICE INT(6), MAX_PRICE INT(6), MIN_PRICE INT(6), DATE_TIME  varchar(50))".format(tabel_name_str)

    # insertvalues = [(int(price_str), int(date_time))]

    print(tablesql)

    # try:
    cnx = connector.connect(host="94.191.126.86", user="root", password="Linlinan123!", database="wuaijinrong",
                        charset="utf8")

    db0 = cnx.cursor()

    db0.execute(tablesql)

    cnx.commit()
    db0.close()


if __name__=="__main__":
    print("into main function")

    # 这里是每天定时的建表格
    schedule.every().day.at("13:20").do(day_job)
    schedule.every().minute.do(minute_job)

    while True:
        schedule.run_pending()
        time.sleep(1)




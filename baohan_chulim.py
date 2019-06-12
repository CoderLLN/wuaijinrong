# -*- coding: utf-8 -*-
from mysql import connector
import schedule
import time

tabel_name_str = ""

current_max = 0
current_min = 0
current_time = ""

bhm_state = 0

insert_count = 0


#
def bao_ban(A_max, A_min, B_max, B_min):
    if (A_max >= B_max and A_min <= B_min) or (B_max >= A_max and B_min <= A_min):
        return True
    else:
        return False


#
def minute_job():

    global tabel_name_str, current_max, current_min, bhm_state, insert_count, current_time

    temp_max = 0
    temp_min = 0
    temp_time = 0

    print("fenzhong job")

    time_str = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())

    time_str_str = time_str.replace(" ", "").replace("-", "")

    print(time_str_str)

    if time_str_str[11:12] == "00":
        the_time_str = str(int(time_str_str[0:12]) - 41) + "00"
    else:
        the_time_str = str(int(time_str_str[0:12]) - 1) + "00"

    print(the_time_str)
    try:

        select_sql = "select MAX_PRICE, MIN_PRICE, DATE_TIME from M{} where DATE_TIME = " \
                     "{}".format(tabel_name_str, the_time_str)

        print(select_sql)

        cnx = connector.connect(host="94.191.126.86", user="root", password="Linlinan123!", database="wuaijinrong",
                            charset="utf8")

        db0 = cnx.cursor()

        db0.execute(select_sql)

        result_set = db0.fetchall()

        if result_set:
            temp_max = result_set[0][0]
            temp_min = result_set[0][1]
            temp_time = result_set[0][2]

        print("="*50)
        print(temp_max)
        print(temp_min)
        print(temp_time)

        if insert_count == 0:
            current_max = temp_max
            current_min = temp_min
            current_time = temp_time

            write_sql = "INSERT INTO `BHM{}` (`MAX_PRICE`,`MIN_PRICE`, `DATE_TIME`) " \
                        "VALUES ({},{},{})".format(tabel_name_str, current_max, current_min, current_time)

            print(write_sql)

            db0.execute(write_sql)
            cnx.commit()
            db0.close()

            insert_count += 1

            return

        if insert_count == 1:

            if (temp_max + temp_min)/2.0 >= (current_max + current_min)/2.0:
                bhm_state = 1
            else:
                bhm_state = -1

            current_max = temp_max
            current_min = temp_min
            current_time = temp_time

            write_sql = "INSERT INTO `BHM{}` (`MAX_PRICE`,`MIN_PRICE`, `DATE_TIME`) " \
                        "VALUES ({},{},{})".format(tabel_name_str, current_max, current_min, current_time)

            db0.execute(write_sql)

            print(write_sql)

            cnx.commit()
            db0.close()

            insert_count += 1

            return

        if insert_count > 1:
            print("处理K线")
            if bao_ban(temp_max, temp_min, current_max, current_min):
                if bhm_state == 1:
                    current_max = max(temp_max, current_max)
                    current_min = max(temp_min, current_min)
                if bhm_state == -1:
                    current_max = min(temp_max, current_max)
                    current_min = min(temp_min, current_min)

                print("这里只需更新数据库最后一条数据即可")
                update_sql = "update BHM{} set MAX_PRICE={},MIN_PRICE={},DATE_TIME={} " \
                             "order by id desc limit 1".format(tabel_name_str, current_max, current_min, current_time)

                db0.execute(update_sql)
                cnx.commit()
                db0.close()

            else:
                if (temp_max + temp_min)/2.0 >= (current_max + current_min)/2.0:
                    bhm_state = 1
                else:
                    bhm_state = -1

                current_max = temp_max
                current_min = temp_min
                current_time = temp_time

                print("因为不存在包含关系，更新趋势状态并插库即可")

                write_sql = "INSERT INTO `BHM{}` (`MAX_PRICE`,`MIN_PRICE`, `DATE_TIME`) " \
                        "VALUES ({},{},{})".format(tabel_name_str, current_max, current_min, current_time)

                db0.execute(write_sql)
                cnx.commit()
                db0.close()

            cnx.commit()
            db0.close()
    except:
        pass

#

def day_job():

    global tabel_name_str, current_max, current_min, bhm_state

    time_str = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())

    print(time_str)

    tabel_name_str = time_str.split(" ")[0].replace("-", "")

    print(tabel_name_str)

    # 这里的建表语句需要每天执行一次
    tablesql = "Create Table If Not Exists `BHM{}`(Id INT(6) primary key auto_increment," \
               "MAX_PRICE INT(6), MIN_PRICE INT(6), DATE_TIME  varchar(50))".format(tabel_name_str)

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
    schedule.every().day.at("06:00").do(day_job)
    schedule.every().minute.do(minute_job)

    while True:
        schedule.run_pending()
        time.sleep(1)







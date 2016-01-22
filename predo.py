#encoding=UTF-8
#
#  数据库关联工具 【 数据库 间 关联 】 B表记录生成器
#  ============================================
#	2016.1.22 by shenwei @GuiYang
#

import sys;

import MySQLdb

# 连接MySQL数据库
def mysql_conn():
    # !!!关键!!!
    # 设定环境字符串编码为utf-8
    reload(sys)
    sys.setdefaultencoding('utf-8')

    mysql_conn = MySQLdb.connect(
        host='10.169.6.20',
        port=3306,
        user='root',
        passwd='sw64419',
        db='gyrsj',
        charset="utf8")
    cur = mysql_conn.cursor()
    return cur

def main():

    cur_mysql = mysql_conn()

    # 从 oatables.sql 文件中解析出 表结构
    fp = open("oatables.sql")

    tables = {}
    while 1:
        line = fp.readline()

        if line is None:
            break
        if len(line)==0:
            break

        if "CREATE TABLE `" in line:

            v = line.split(' ')
            # 获得 表名
            table_name = v[2].strip('`')

            feilds = []

            i = 0

            while 1:
                line = fp.readline()

                if line is None:
                    return
                if len(line)==0:
                    return

                v = line.split(' ')
                #print v
                if v[0]==")":
                    # 一个表定义结束
                    # 给该表赋上 域名
                    tables[table_name] = feilds
                    break

                if "decimal(" in v[3]:
                    # 只需收集 类型=decimal 的域名
                    feilds.append(v[2].strip('`'))

                i += 1
                if i > 300:
                    # 防止死锁
                    return

    for tab in tables:

        if len(tables[tab])==0:
            continue

        sql = 'select '
        #print tables[tab]
        i = 0
        for s in tables[tab]:
            if i==0:
                # 注：省略第一个decimal，默认为是该表的 主键
                i = 1
            else:
                sql += ','
            sql += s
        sql += ' from ' + tab

        #print sql
        # 获取 表记录
        cnt = cur_mysql.execute(sql)
        if cnt>0:

            while 1:
                one = cur_mysql.fetchone()
                if one is None:
                    break

                j = 0
                res = tab + ":"
                for feild in one:
                    if j>0:
                        res += (tables[tab][j] + '^' + str(feild)+',')
                    j += 1
                # res中的数据结构
                # 表名:域名^域值
                #
                print res

    cur_mysql.close()

if __name__ == "__main__":

    reload(sys)
    sys.setdefaultencoding("utf8")

    main()

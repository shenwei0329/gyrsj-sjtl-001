#encoding=UTF-8
#
#   created by shenwei @GuiYang 2015.12.13
#
#

import sys
import utils

cur_mysql = utils.mysql_conn()

fn = sys.argv[1]
f = open(fn,'r')

cnt = 0

while cnt<400:

    data = (f.readline()).replace('\n','')
    data = data.split(',')
    if int(data[0])==2016:
        if int(data[3])>0:
            sql = 'insert into special_day(year,month,day) values(%s,%s,%s)' % (data[0],data[1],data[2])
            print sql
            cur_mysql.execute(sql)

    cnt += 1

cur_mysql.close()

#
# Eof
#

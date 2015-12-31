#encoding=UTF-8
#
#	2015.12.10 by shenwei @GuiYang
#	==============================
#	统计昨天完成的申请办理数，计入月份
#

import MySQLdb
import os
import sys
from subprocess import Popen,PIPE

import utils

cur_mysql = utils.mysql_conn()

#从命令行获取业务线id
line_id = sys.argv[1]

#获取指定业务线的表单ID项
form_id = utils.get_line(cur_mysql,line_id)

#从表单主表中获取昨天的已完成的表单记录
total = cur_mysql.execute('select id from col_summary where to_days(now())-to_days(finish_date)<=1 and state=3 and %s' % form_id)
#print total

#得到当前月份
m = utils.get_month(cur_mysql)

#获取本月业绩
mm = mt = 0
cnt = cur_mysql.execute('select m from year_total where id=%s and line_id=%s' % (m,line_id))
if cnt>0:
    v = cur_mysql.fetchone()
    mm = int(v[0])

#做业务累计
#print(">>> 1: %d,%d <<<" % (mm,mt))
mm += total
mt += total
cur_mysql.execute('update year_total set m=%d where id=%s and line_id=%s' % (mm,m,line_id));

cur_mysql.close()

#
# Eof
#

#encoding=UTF-8
#
#	2015.12.10 by shenwei @GuiYang
#	==============================
#	在每月1日00:00时，须清除本月的累计业绩
#

import MySQLdb
import os
import sys
from subprocess import Popen,PIPE

import utils

cur_mysql = utils.mysql_conn()

#清除本月累计业绩
m = utils.get_month(cur_mysql)
cur_mysql.execute('update year_total set m=0 where id=%s' % m);

cur_mysql.close()

#
# Eof
#

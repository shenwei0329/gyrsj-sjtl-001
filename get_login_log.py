#encoding=UTF-8
#
#	2015.12.10 by shenwei @GuiYang
#	==============================
#	从OA系统同步人员在线情况。
#
#

import cx_Oracle
import MySQLdb
import os
from subprocess import Popen,PIPE

import utils

def do_rec(cur,cur_mysql,in_sql):
	idx = 0
	while 1:
		one = cur.fetchone()
		if one!=None:
			idx += 1
			sql = in_sql
			#print(':\n-------------------------------%s' % type(one))
			cnt = len(one)
			for i in range(cnt):
				#print one[i]
				if i!=0:
					sql += ','
				else:
					id = one[0]
				sql += '"'+str(one[i])+'"'
		else:
			break
		sql += ")"
		#print("++++")
		#print(sql)
		cur_mysql.execute(sql)

tables = [{	"select":"id,member_id,logon_time,logout_time,ip_address",
		"table":'logon_log where logon_time=logout_time order by logon_time',
		"mysql_table":'login_log(id,member_id,login,logout,ip) values(',
	}]

cur_mysql = utils.mysql_conn()
oracle_conn = utils.oracle_conn()
cur_oracle = oracle_conn.cursor()

'''清除原有记录
'''
sql = 'DELETE FROM login_log'
cur_mysql.execute(sql)

sql = 'SELECT '+tables[0]["select"] + ' FROM ' + tables[0]["table"]
in_sql = 'INSERT into '+tables[0]["mysql_table"]
info = cur_oracle.execute(sql)

do_rec(info,cur_mysql,in_sql)

cur_oracle.close()
cur_mysql.close()
oracle_conn.close()

#
# Eof
#

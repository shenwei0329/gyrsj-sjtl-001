#encoding=UTF-8
#

from subprocess import Popen,PIPE
import cx_Oracle

def disp_rec(cur):
	while 1:
		one = cur.fetchone()
		if one!=None:
			print one
		else:
			break

tns_name = cx_Oracle.makedsn('10.169.8.59','1521','orcl')
db = cx_Oracle.connect('v3xuser','Www123456',tns_name)

print db.dsn

cur_src = db.cursor()

sql = 'SELECT * FROM logon_log'

info = cur_src.execute(sql)

disp_rec(info)

cur_src.close()
db.close()


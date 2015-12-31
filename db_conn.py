#encoding=UTF-8
#

from subprocess import Popen,PIPE
import cx_Oracle

tns_name = cx_Oracle.makedsn('10.169.8.59','1521','orcl')
db = cx_Oracle.connect('v3xuser','Www123456',tns_name)

print db.dsn

cur_src = db.cursor()

tables = ['org_member']

info = cur_src.execute('select * from '+tables[0])

while 1:
    one = info.fetchone()
    if one is not None:
        print one
    else:
        break

cur_src.close()
db.close()


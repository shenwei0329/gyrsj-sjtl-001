#encoding=UTF-8
#
#	2015.12.10 by shenwei @GuiYang
#	==============================
#	从OA系统同步业务日志到系统
#
#

import cx_Oracle
import MySQLdb
import os
from subprocess import Popen,PIPE

import utils

def get_summary_id_by_subject(cur,text):
    rec = utils.get_summary(cur)
    for r in rec:
        #print("%s:%s" % (r['subject'],text))
        # 通过信息中是否包含某summary主题来确定该信息是针对哪个summary的
        if str(r['subject']) in text:
            return r['id']
    return 0

def do_rec(cur,cur_mysql,in_sql):
    while 1:
        one = cur.fetchone()
        id = ''
        summary_id = 0
        if one!=None:
            sql = in_sql
            cnt = len(one)
            for i in range(cnt):
                if i!=0:
                    sql += ','
                else:
                    id = one[0]
                sql += '"'+str(one[i])+'"'
        else:
            break
        sql += ")"
        if utils.is_include(cur_mysql,'col_user_message',id)==0:
            #print("++++")
            #print(sql)
            cur_mysql.execute(sql)

tables = [{	"select":"id,sender_id,receiver_id,message_content,creation_date",
        "table":"ctp_user_history_message where creation_date>=to_date('2015-12-28 00:00:00','yyyy-mm-dd hh24:mi:ss')  order by creation_date",
        "mysql_table":'col_user_message(id,sender_id,receiver_id,message,create_date) values(',
    }]

cur_mysql = utils.mysql_conn()
oracle_conn = utils.oracle_conn()
cur_oracle = oracle_conn.cursor()

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

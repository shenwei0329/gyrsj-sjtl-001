#encoding=UTF-8
#
#   2015.12.10 by shenwei @GuiYang
#   ==============================
#   从OA系统同步业务日志到系统
#
#   在ctp_user_message表中存放着正在办理的协同。
#

import cx_Oracle
import MySQLdb
import os
from subprocess import Popen,PIPE

import utils

# 根据主题获取summaryID
def get_summary_id_by_subject(cur,text):
    rec = utils.get_summary(cur)
    for r in rec:
        #print("%s:%s" % (r['subject'],text))
        if str(r['subject']) in text:
            return r['id']
    return None

def do_rec(cur,cur_mysql,in_sql):
    while 1:
        out_flg = False
        id = ''
        one = cur.fetchone()
        summary_id = 0
        sender_id = ''
        if one is not None:
            sql = in_sql
            cnt = len(one)
            for i in range(cnt):
                if i != 0:
                    sql += ','
                    if i == 1:
                        sender_id = str(one[i])
                    if i == 2:
                        text = str(one[i])
                        # 过滤掉 政务大厅发起协同 的信息
                        #if "政务大厅发起协同" in text:
                        #    out_flg = True
                        #    break
                        summary_id = get_summary_id_by_subject(cur_mysql,text)
                        if sender_id == "8764456166134006930":
                            if "数据铁笼预警" in text:
                                # 预警中包含这些关键词
                                flg = 2
                            elif "数据铁笼风险提示" in text:
                                # 由数据铁笼发出信息，不是预警就是风险了
                                flg = 3
                            else:
                                # 应该是向上级的汇报信息
                                flg = 1
                        else:
                            flg = 1
                    if i==3:
                        create_date=str(one[3])
                else:
                    id = one[0]
                sql += '"'+str(one[i])+'"'
        else:
            break
        if out_flg:
            continue
        if summary_id is not None:
            sql += ",%d,%s)" % (flg,str(summary_id))
        else:
            sql += ",%d,0)" % flg

        if utils.is_include(cur_mysql,'ctp_user_message',id)==0:

            # 问题：即使ID不同，也会有很多内容相同的信息，也应该滤去
            sql1 = 'select * from ctp_user_message where message="%s" and create_date="%s"' % (text, create_date)
            cnt = cur_mysql.execute(sql1)
            if cnt > 0:
                continue

            #print("++++")
            #print(sql)
            cur_mysql.execute(sql)

tables = [{	"select":"id,sender_id,message_content,creation_date",
        "table":"ctp_user_message where creation_date>=to_date('2015-12-21 00:00:00','yyyy-mm-dd hh24:mi:ss') order by creation_date",
        "mysql_table":'ctp_user_message(id,sender_id,message,create_date,flg,summary_id) values(',
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

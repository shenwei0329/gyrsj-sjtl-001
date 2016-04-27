#encoding=UTF-8
#
#   2015.12.10 by shenwei @GuiYang
#   ==============================
#   从OA系统同步业务申请单到系统，用于获取“新增”的申请
#
#   1) 从OA.cor_summary表中获取新增的申请表
#   2) 通知OA应用服务器上的代理去处理该申请的附属文件，并将识别的txt文本传回
#   3) 用scala去完成材料规则碰撞，并记录结果
#   4）设置deadline为业务线办理总期限
#

import utils
import datetime,time

def do_rec(cur,cur_mysql,in_sql):
    line_id = None
    while 1:
        one = cur.fetchone()
        if one!=None:
            sql = in_sql
            #print(':\n-------------------------------%s' % type(one))
            cnt = len(one)
            #print one
            for i in range(cnt):
                #print i,one[i]
                sql += '"'+str(one[i])+'"'
            sql += ')'
        else:
            break

        # 判断该记录是否已经同步
        #
        cnt = cur_mysql.execute('select id from ctp_affair where id="%s"' % one[0])
        if cnt==0:
            print sql
            # 保存记录
            cur_mysql.execute(sql)

# 2015-12-26 只抽取 12月21日后 的业务数据
#
tables = [dict(
    select=
 "ID,IS_COVER_TIME,MEMBER_ID,SENDER_ID,SUBJECT,APP,OBJECT_ID,SUB_OBJECT_ID,STATE,SUB_STATE,HASTEN_TIMES,REMIND_DATE,DEADLINE_DATE," \
 "CAN_DUE_REMIND,CREATE_DATE,RECEIVE_TIME,COMPLETE_TIME,REMIND_INTERVAL,IS_DELETE,TRACK,ARCHIVE_ID,ADDITION,EXT_PROPS,UPDATE_DATE," \
 "IS_FINISH,BODY_TYPE,IMPORTANT_LEVEL,RESENT_TIME,FORWARD_MEMBER,IDENTIFIER,TRANSACTOR_ID,NODE_POLICY,ACTIVITY_ID,FORM_APP_ID,FORM_ID," \
 "FORM_OPERATION_ID,TEMPLETE_ID,FROM_ID,OVER_WORKTIME,RUN_WORKTIME,OVER_TIME,RUN_TIME,DEAL_TERM_TYPE,DEAL_TERM_USERID,SUB_APP," \
 "EXPECTED_PROCESS_TIME,ORG_ACCOUNT_ID,PROCESS_ID,IS_PROCESS_OVER_TIME,FORM_MULTI_OPERATION_ID,BACK_FROM_ID,FORM_RELATIVE_STATIC_IDS,FORM_RELATIVE_QUERY_IDS",
    table="ctp_affair where create_date>=to_date('2015-11-01 00:00:00','yyyy-mm-dd hh24:mi:ss') order by create_date",
    mysql_table=
 "ctp_affair(ID,IS_COVER_TIME,MEMBER_ID,SENDER_ID,SUBJECT,APP,OBJECT_ID,SUB_OBJECT_ID,STATE,SUB_STATE,HASTEN_TIMES,REMIND_DATE,DEADLINE_DATE," \
 "CAN_DUE_REMIND,CREATE_DATE,RECEIVE_TIME,COMPLETE_TIME,REMIND_INTERVAL,IS_DELETE,TRACK,ARCHIVE_ID,ADDITION,EXT_PROPS,UPDATE_DATE," \
 "IS_FINISH,BODY_TYPE,IMPORTANT_LEVEL,RESENT_TIME,FORWARD_MEMBER,IDENTIFIER,TRANSACTOR_ID,NODE_POLICY,ACTIVITY_ID,FORM_APP_ID,FORM_ID," \
 "FORM_OPERATION_ID,TEMPLETE_ID,FROM_ID,OVER_WORKTIME,RUN_WORKTIME,OVER_TIME,RUN_TIME,DEAL_TERM_TYPE,DEAL_TERM_USERID,SUB_APP," \
 "EXPECTED_PROCESS_TIME,ORG_ACCOUNT_ID,PROCESS_ID,IS_PROCESS_OVER_TIME,FORM_MULTI_OPERATION_ID,BACK_FROM_ID,FORM_RELATIVE_STATIC_IDS," \
 "FORM_RELATIVE_QUERY_IDS values("
    )
 ]

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

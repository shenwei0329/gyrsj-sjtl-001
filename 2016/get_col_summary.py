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
        subject = ''
        start_date = '2000-01-01 00:00:00'
        one = cur.fetchone()
        if one!=None:
            sql = in_sql
            #print(':\n-------------------------------%s' % type(one))
            cnt = len(one)
            #print one
            for i in range(cnt):
                #print i,one[i]
                if i!=0:
                    if i==12:
                        form_appid = one[12]
                        if form_appid == None:
                            #print(">>>form_appid=%s" % str(form_appid))
                            line_id = None
                        else:
                            # 注意：针对优先办理等特权情况，无法用此方法获取line_id，因为这些form可针对所有业务
                            line_id = utils.get_lineid_by_formid(cur_mysql,form_appid)
                            #print(">>>line_id=%s<<<" % line_id)
                    sql += ','
                else:
                    summary_id = one[0]
                if i==3:
                    # 新增记录，设定法定期限为8天
                    sql += '8'
                elif i==13:
                    # for VOUCH
                    sql += '0'
                else:
                    sql += '"'+str(one[i])+'"'
                    if i==2:
                        subject = str(one[i])
                    if i==8:
                        start_member = str(one[i])
                    if i==6:
                        start_date = str(one[i])

        else:
            break

        # 设定岗位期限为8天
        sql += ",8,"
        if utils.is_include(cur_mysql,'col_summary',summary_id)==0:

            print("++++")
            # 2015-12-19: 新加入的summary没有优先办理特权
            if line_id!=None:
                if "分管领导指派优先办理" in subject:
                    sql += "0,5,0)"
                else:
                    # 设置新增的申请单在 业务线的第一个（sn=0）岗位上
                    sql += "%s,1,0)" % line_id
            else:
                sql += "0,1,0)"
            print sql
            # 保存记录
            cur_mysql.execute(sql)
            # 添加流水号
            yw_sn = utils.get_sn(cur_mysql,summary_id)

            print(">>>流水号:%s<<<" % yw_sn)
            if yw_sn!=None:
                rec = utils.build_ServiceObject(cur_mysql,summary_id)
                sql = 'update col_summary set yw_sn="%s",' \
                      'org_code="%s",org_name="%s",org_addr="%s",org_capital="%s",org_reg_number="%s",org_reg_addr="%s",' \
                      'legal_person="%s",legal_person_tel="%s",legal_person_cid="%s" where id="%s"' % \
                      (yw_sn,rec['bar_code'],rec['name'],rec['addr'],rec['registered_capital'],
                       rec['registeration_number'],rec['registered_addr'],
                       rec['legal_representative_name'],rec['legal_representative_tel'],rec['legal_representative_id'],summary_id)
                print sql
                cur_mysql.execute(sql)

# 2015-12-26 只抽取 12月21日后 的业务数据
#
tables = [dict(
    select="ID,STATE,SUBJECT,DEADLINE,RESENT_TIME,CREATE_DATE,START_DATE,FINISH_DATE,START_MEMBER_ID,FORWARD_MEMBER,FORM_RECORDID,FORMID,FORM_APPID,ORG_DEPARTMENT_ID,VOUCH,OVER_WORKTIME,RUN_WORKTIME,OVER_TIME,RUN_TIME,CURRENT_NODES_INFO",
    table="col_summary where create_date>=to_date('2015-11-01 00:00:00','yyyy-mm-dd hh24:mi:ss') and  ((state=3) or (state=0 and case_id is not null )) order by create_date",
    mysql_table='col_summary(ID,STATE,SUBJECT,DEADLINE,RESENT_TIME,CREATE_DATE,START_DATE,FINISH_DATE,START_MEMBER_ID,FORWARD_MEMBER,FORM_RECORDID,FORMID,FORM_APPID,ORG_DEPARTMENT_ID,VOUCH,OVER_WORKTIME,RUN_WORKTIME,OVER_TIME,RUN_TIME,CURRENT_NODES_INFO,cnt,line_id,sn,pri) values(')]

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

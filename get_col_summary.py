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
                sql = 'update col_summary set yw_sn="%s" where id="%s"' % (yw_sn,summary_id)
                #print sql
                cur_mysql.execute(sql)
            else:
                yw_sn = ""

            #--------------------------------------------------
            # ！！！若这是一个“特权”事件，则需执行其特权行为 ！！！
            #
            utils.set_summary_pri(cur_mysql,summary_id)

            # for resent_time，用于放置 受理时间
            if ("人力资源" in subject) or ("劳务派遣" in subject) or ("自动发起" in subject) and line_id is not None:

                nday = utils.get_post_deadline(cur_mysql,line_id,1)
                if nday is not None:
                    sql = 'update col_summary set cnt="%s" where id="%s"' % (nday,summary_id)
                    #print sql
                    cur_mysql.execute(sql)

                acc_time = utils.get_summary_feild_value(cur_mysql,summary_id,"受理时间")
                #print(">>>受理时间:%s" % val )
                if acc_time is not None:
                    sql = 'update col_summary set resent_time="%s" where id="%s"' % (acc_time,summary_id)
                    #print sql
                    cur_mysql.execute(sql)
                else:
                    acc_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                    sql = 'update col_summary set resent_time="%s" where id="%s"' % (acc_time,summary_id)
                    #print sql
                    cur_mysql.execute(sql)

                # 通过业务线line_id，检查申请是否带齐必要的附件
                # 如果未带齐，则发出“风险”警告
                #
                #print(">>>1<<<")
                # 2015-12-27 针对“补正”系统会自动发起新的summary记录，此时，不用判断附件情况
                #
                if ("(自动发起)" not in subject) and (not utils.chk_file(cur_mysql,summary_id,line_id)):
                    #print(">>>Here!<<<")

                    user_name = utils.get_user_name(cur_mysql,start_member)

                    utils.send_alarm(cur_mysql,start_member,summary_id,line_id,"【数据铁笼风险提示】：%s，在受理《%s》<%s>时，提交材料存在缺失项，请知悉。" \
                        % (user_name,subject,yw_sn))

                    # 向上级汇报
                    members = utils.get_leader(cur_mysql,line_id,0,0)
                    members += utils.get_leader(cur_mysql,line_id,0,1)
                    for member in members:
                        leader_name = utils.get_user_name(cur_mysql,member)
                        #send_alarm(cur_mysql1,member,"【数据铁笼提示】：%s，好：%s在办的《%s》%s已超期，请知悉。" % (leader_name,user_name,subject,post_name))            # 负数表示超出的天数
                        utils.send_info(cur_mysql,member,"【数据铁笼风险通报】%s，好：%s在受理《%s》时，提交材料存在缺失项，请知悉。" \
                            % (leader_name,user_name,subject))

                # 检查提交时间start_date与“受理时间”acc_time之间的间隔是否超过一天？
                # 若超过，则报风险
                now_d = datetime.datetime.now()
                if acc_time=="None" or acc_time==None or acc_time=="NONE":
                    acc_time = now_d.strftime("%Y-%m-%d %H:%M:%S")
                acc_d = datetime.datetime.strptime(acc_time,"%Y-%m-%d %H:%M:%S")

                # 时间戳（分钟计）
                now_ts = int(time.mktime(now_d.timetuple()))/60
                acc_ts = int(time.mktime(acc_d.timetuple()))/60

                # 记录 某人 在 该业务线节点上 处理申报所占用时间 now_ts - last_ts
                min_cnt = utils.cal_workdays(cur_mysql,acc_time,now_d.strftime('%Y-%m-%d %H:%M:%S'))

                if "(自动发起)" in subject:
                    sql = 'insert into kpi_001(member,summary_id,line_id,sn,dtime,start_date) values("%s","%s",%s,%s,%d,"%s")' \
                                % (start_member,summary_id,line_id,1,min_cnt,acc_time)
                else:
                    sql = 'insert into kpi_001(member,summary_id,line_id,sn,dtime,start_date) values("%s","%s",%s,%s,%d,"%s")' \
                                % (start_member,summary_id,line_id,0,min_cnt,acc_time)

                #sql = 'insert into kpi_001(member,summary_id,line_id,sn,dtime,start_date) values("%s","%s",%s,%s,%d,"%s")' \
                #            % (start_member,summary_id,line_id,0,now_ts-acc_ts,acc_time)
                cur_mysql.execute(sql)

                if (now_ts>acc_ts) and ((now_ts-acc_ts)>(24*60)):

                    # 提交日期 超过 受理日期 一天以上
                    # 风险提示

                    user_name = utils.get_user_name(cur_mysql,start_member)

                    utils.send_alarm(cur_mysql,start_member,summary_id,line_id,"【数据铁笼风险提示】：%s，在受理《%s》<%s>时超出一天期限，请知悉。" \
                        % (user_name,subject,yw_sn))

                    # 向上级汇报
                    members = utils.get_leader(cur_mysql,line_id,0,0)
                    members += utils.get_leader(cur_mysql,line_id,0,1)
                    for member in members:
                        leader_name = utils.get_user_name(cur_mysql,member)
                        utils.send_info(cur_mysql,member,"【数据铁笼风险通报】%s，好：%s在受理《%s》时，超出岗位工作期限，请知悉。" \
                            % (leader_name,user_name,subject))

                    # 需要根据此情况调整 deadline 的值
                    n = 8 - (now_ts-acc_ts)/(24*60)
                    sql = 'update col_summary set deadline=%d where id="%s"' % (n,summary_id)
                    cur_mysql.execute(sql)

                # 设置第一个时间点
                #
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sql = 'update col_summary set finish_date="%s" where id="%s"' % (now,summary_id)
                cur_mysql.execute(sql)

# 2015-12-26 只抽取 12月21日后 的业务数据
#
tables = [dict(
    select="ID,STATE,SUBJECT,DEADLINE,RESENT_TIME,CREATE_DATE,START_DATE,FINISH_DATE,START_MEMBER_ID,FORWARD_MEMBER,FORM_RECORDID,FORMID,FORM_APPID,ORG_DEPARTMENT_ID,VOUCH,OVER_WORKTIME,RUN_WORKTIME,OVER_TIME,RUN_TIME,CURRENT_NODES_INFO",
    table="col_summary where create_date>=to_date('2015-12-28 00:00:00','yyyy-mm-dd hh24:mi:ss') and  ((state=3) or (state=0 and case_id is not null )) order by create_date",
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

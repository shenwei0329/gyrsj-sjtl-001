#encoding=UTF-8
#
#   2015.12.10 by shenwei @GuiYang
#   ==============================
#   从OA系统更新业务申请单到系统
#
#   1）不更新本地state=3的申请单
#   2）检查current_nodes_info是否有变化，若有：同步，启动岗位期限设置
#   3）检查state是否有变化，若有：同步
#

import utils

import time,datetime

cur_mysql = utils.mysql_conn()
oracle_conn = utils.oracle_conn()
cur_oracle = oracle_conn.cursor()

sql = "SELECT ID,CURRENT_NODES_INFO,state FROM col_summary where create_date>=to_date('2015-12-28 00:00:00','yyyy-mm-dd hh24:mi:ss') and ((state=3) or (state=0 and case_id is not null )) order by create_date"
cur = cur_oracle.execute(sql)
# 扫描col_summary表
while 1:
    one = cur.fetchone()
    if one is None:
        break
    summary_id = str(one[0])

    # 多人竞岗时，该字段有多个ID用';'分开
    multi_users = False
    o_current_nodes_info = str(one[1]).split(';')
    if len(o_current_nodes_info)>0:

        if len(o_current_nodes_info)>1:
            # 如果该节点包含多人“竞争”办理，则需要做一个标记
            #print(">>> multi_user <<<")
            multi_users = True

        # 取第一个人员做为下一节点办理人
        o_current_nodes_info = o_current_nodes_info[0]

    o_state = str(one[2])
    #print(">>>o_state=%s<<<" % o_state)
    if o_state == "None" or o_state == "NONE":
        # 在政务大厅提交后的 申请单，其state好像是None
        continue

    if utils.is_include(cur_mysql,'col_summary',summary_id) != 0:
        # 针对已有的申请单
        sql = 'select current_nodes_info,pri,subject,line_id,sn,finish_date,state,cnt from col_summary where state=0 and id="%s" order by create_date' % summary_id
        cnt = cur_mysql.execute(sql)
        if cnt>0:

            one = cur_mysql.fetchone()
            m_current_nodes_info = str(one[0])
            m_pri = str(one[1])
            m_subject = str(one[2])
            line_id = str(one[3])
            sn = str(one[4])
            finish_date = str(one[5])
            m_state = str(one[6])
            # 剩余天数
            m_cnt = str(one[7])

            # 判断是否有人员变化
            # 针对“多人”竞争办理的节点，因为缺省让第一人作为下一节点办理者，这时也许人员不会变化
            #
            if m_current_nodes_info != o_current_nodes_info:

                # 获得新人员的 岗位ID
                if o_current_nodes_info!="None":
                    # 获得新岗位信息
                    o_line_id,o_sn = utils.get_post_id(cur_mysql,o_current_nodes_info)
                    # 原来岗位
                    m_line_id,m_sn = utils.get_post_id(cur_mysql,m_current_nodes_info)
                    # 新岗位是否存在？
                    #print("orcale->>> %s-%s:%s <<<" % (o_current_nodes_info,o_line_id,o_sn))
                    #print("mysql->>> %s-%s:%s <<<" % (m_current_nodes_info,m_line_id,m_sn))
                    if o_line_id!=None and o_sn!=None:

                        post_name = utils.get_post_name(cur_mysql,line_id,sn)

                        # 判断是否为按序办理业务
                        if int(m_pri) == 0:
                            # 对没有优先办理特权的summary判定是否“未按顺序”办理
                            # 2015-12-22 将该行为作为风险
                            # 遗漏事宜：需要在信息中保留业务的流水号，以便当领导授权优先办理时，可以撤回该风险
                            #
                            flg,current_nodes_info,yw_sn = utils.comp_date(cur_mysql,summary_id)
                            if flg:

                                user_name = utils.get_user_name(cur_mysql,current_nodes_info)
                                #utils.send_message(cur_mysql,current_nodes_info,("【数据铁笼风险提示】：%s,你在办理《%s》%s前，仍有未办理业务！") % (user_name,m_subject,post_name))
                                utils.send_alarm(cur_mysql,current_nodes_info,summary_id,line_id,"【数据铁笼风险提示】：%s,在办理《%s》<%s>%s前，仍有未办理业务！" % (user_name,m_subject,yw_sn,post_name))

                                # 向上级汇报
                                members = utils.get_leader(cur_mysql,line_id,sn,0)
                                members += utils.get_leader(cur_mysql,line_id,sn,1)
                                for member in members:
                                    #leader_name = utils.get_user_name(cur_mysql,member)
                                    #send_alarm(cur_mysql1,member,"【数据铁笼提示】：%s，好：%s在办的《%s》%s已超期，请知悉。" % (leader_name,user_name,subject,post_name))            # 负数表示超出的天数
                                    utils.send_info(cur_mysql,member,"【数据铁笼风险通报】：%s在办理《%s》%s前，仍有未办理业务，请知悉。" % (user_name,m_subject,post_name))

                        if (m_sn=="None") or (m_sn==None):
                            m_sn = o_sn
                        elif int(o_sn) <= int(m_sn):
                            # 第一种情况：主管领导签字同意后，由科员办结
                            # 第二种情况：处长签字同意后，由科员现场踏勘，有可能是处长去

                            if utils.is_wait(cur_oracle,cur_mysql,summary_id):
                                # 针对劳动派遣的补正情况，领导同意后，回到“初审”节点
                                if int(m_line_id)==2 and int(m_sn)==4:
                                    # 针对“劳务派遣”，并分管领导已同意“补正”时
                                    # 状态应该回到“初审”节点
                                    o_sn = '1'
                            else:
                                # 如果不需要“补正”，则流程往下走
                                o_sn = str(int(m_sn)+1)

                        # 设置岗位期限
                        post_deadline = utils.get_post_deadline(cur_mysql,o_line_id,o_sn)
                        if post_deadline!=None:

                            if utils.is_wait(cur_oracle,cur_mysql,summary_id):
                                # 针对劳动派遣的补正情况，领导同意后，回到“初审”节点
                                if int(m_line_id)==2 and int(m_sn)==4:
                                    # 补正需要在5天内完成
                                    post_deadline = str(int(post_deadline) + 5)

                            #print type(o_current_nodes_info),o_current_nodes_info
                            sql = 'update col_summary set current_nodes_info=%s,cnt=%s where id="%s"' % (o_current_nodes_info,post_deadline,summary_id)
                            #print sql
                            cur_mysql.execute(sql)
                            # 更新状态
                            sql = 'update col_summary set sn=%s,state=%s where id="%s"' % (o_sn,o_state,summary_id)
                            #print sql
                            cur_mysql.execute(sql)
                            # 根据岗位变化设定定时器
                            #utils.set_timer(cur_mysql,id)

                            # 计算 上一节点操作时间
                            now_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            min_cnt = utils.cal_workdays(cur_mysql,finish_date,now_datetime)

                            # 记录 某人 在 该业务线节点上 处理申报所占用时间 now_ts - last_ts
                            sql = 'insert into kpi_001(member,summary_id,line_id,sn,dtime,start_date) values("%s","%s",%s,%s,%d,"%s")' \
                                % (m_current_nodes_info,summary_id,line_id,sn,min_cnt,finish_date)
                            cur_mysql.execute(sql)

                            sql = 'update col_summary set finish_date="%s" where id="%s"' % (now_datetime,summary_id)
                            cur_mysql.execute(sql)

                            # 添加 业务日志
                            utils.yw_log(cur_mysql,summary_id,m_current_nodes_info,sn,finish_date,now_datetime,min_cnt)

                else:
                    # 置为最后的岗位
                    # 2015-12-25：针对撤销协同行为的处理？
                    new_sn = '5'
                    # 原来岗位
                    if (o_current_nodes_info is None) or (o_current_nodes_info=="None"):
                        o_current_nodes_info = 0
                    sql = 'update col_summary set sn=%s,state=%s,current_nodes_info="%s" where id="%s"' \
                        % (new_sn,o_state,o_current_nodes_info,summary_id)
                    print sql
                    cur_mysql.execute(sql)

                    # 计算 上一节点操作时间
                    now_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    min_cnt = utils.cal_workdays(cur_mysql,finish_date,now_datetime)

                    # 记录 某人 在 该业务线节点上 处理申报所占用时间 now_ts - last_ts
                    sql = 'insert into kpi_001(member,summary_id,line_id,sn,dtime,start_date) values("%s","%s",%s,%s,%d,"%s")' \
                            % (m_current_nodes_info,summary_id,line_id,new_sn,min_cnt,finish_date)
                    cur_mysql.execute(sql)

                    sql = 'update col_summary set finish_date="%s" where id="%s"' % (now_datetime,summary_id)
                    cur_mysql.execute(sql)

                    # 添加 业务日志
                    utils.yw_log(cur_mysql,summary_id,m_current_nodes_info,sn,finish_date,now_datetime,min_cnt)

            else:
                # 如果人员未发生变化
                if multi_users==True and int(sn)==2:
                    # 允许多人竞争办理，且当前节点为（复审）时
                    # 下一节点“强置为”3“，即现场环节
                    new_sn = '3'
                    sql = 'update col_summary set sn=%s where id="%s"' \
                        % (new_sn,summary_id)
                    print sql
                    cur_mysql.execute(sql)

                    # 计算 上一节点操作时间
                    now_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    min_cnt = utils.cal_workdays(cur_mysql,finish_date,now_datetime)

                    # 记录 某人 在 该业务线节点上 处理申报所占用时间 now_ts - last_ts
                    sql = 'insert into kpi_001(member,summary_id,line_id,sn,dtime,start_date) values("%s","%s",%s,%s,%d,"%s")' \
                            % (m_current_nodes_info,summary_id,line_id,sn,min_cnt,finish_date)
                    cur_mysql.execute(sql)

                    sql = 'update col_summary set finish_date="%s" where id="%s"' % (now_datetime,summary_id)
                    cur_mysql.execute(sql)

                    # 添加 业务日志
                    utils.yw_log(cur_mysql,summary_id,m_current_nodes_info,sn,finish_date,now_datetime,min_cnt)

cur_oracle.close()
cur_mysql.close()
oracle_conn.close()

#
# Eof
#

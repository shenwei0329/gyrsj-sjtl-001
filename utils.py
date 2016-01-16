#encoding=UTF-8
#
#   2015.12.10 by shenwei @GuiYang
#   ==============================
#   公共模块定义
#
#   2015.12.17：整理注释 @贵阳
#
#   2015.12.19：这里的应用程序是针对OA（版本G6）数据库定制化的，用于从OA采集业务数据分析。
#

# 引入数据库连接器
import cx_Oracle
import MySQLdb

import uuid

# 引入系统模块
import os,sys,time,datetime

# 连接MySQL数据库
def mysql_conn():
    # !!!关键!!!
    # 设定环境字符串编码为utf-8
    reload(sys)
    sys.setdefaultencoding('utf-8')

    mysql_conn = MySQLdb.connect(
        host='master',
        port=3306,
        user='root',
        passwd='123456',
        db='gyrsj',
        charset="utf8")
    cur = mysql_conn.cursor()
    return cur

# 连接Oracle数据库
def oracle_conn():
    os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
    tns_name = cx_Oracle.makedsn('10.169.8.59','1521','orcl')
    db = cx_Oracle.connect('v3xuser','Www123456',tns_name)
    return db

# 判断本地某库是否已包含某记录ID
def is_include(cur,table,id):
        sql = "select id from %s where id=%s" % (table,id)
        cnt = cur.execute(sql)
        if cnt>0:
                return 1
        return 0

# 获取近三个月的申请单ID和主题
def get_summary(cur):
    sql = 'select id,subject from col_summary WHERE start_date >= DATE_SUB( CURRENT_DATE() , INTERVAL 3 MONTH )'
    cnt = cur.execute(sql)
    rec = []
    if cnt>0:
        for i in range(cnt):
            one = cur.fetchone()
            r = {}
            r['id'] = str(one[0])
            r['subject'] = one[1]
            rec.append(r)
    return rec

# 利用MySQL语句获取本月份
def get_month(cur):
    # 获取当前月份
    cnt = cur.execute('select month(now())')
    if cnt>0:
        m = cur.fetchone()
        #print(">>> month=%s <<<" % m)
        return m[0]
    return '0'

# 生成与业务线相关联的SQL条件语句部分
def get_line(cur,line_id):
    # 获取业务线的表单ID
    cnt = cur.execute('select form_def_id from line_def where id=%s' % line_id)
    form_id = ""
    if cnt>0:
        for i in range(cnt):
            # 一个业务线会有多个表单
            v = cur.fetchone()
            if i==0:
                form_id = "( form_appid=%s" % v[0]
            else:
                form_id += " or form_appid=%s" % v[0]
        form_id += ")"
    #print(form_id)
    return form_id

# 按申报表单form_def_id同步line_def表记录
# 输入：
#   cur：mysql数据库光标
#   line_id：业务线（目前，1：表示人力资源，2：表示劳动派遣）
#   id：表单ID
#   name：表单名称
#   field：主表（也称为底表）名称
def sync_line_id(cur,line_id,id,name,field):
    # 同步业务线定义
    # 2015-12-22 修改：增加 and id=%s 条件，相同的表单ID可以在不同的line_id存在，例如“特权”表单
    cnt = cur.execute('select id from line_def where form_def_id="%s" and id=%s' % (id,line_id))
    if cnt==0:
        #print(">>> %d-%s.%s.%s <<<" % (line_id,id,name,field))
        cur.execute('insert into line_def(id,form_def_id,name,formmain_name,deadline) values(%d,%s,"%s","%s",8)' % (line_id,id,name,field))

# 从OA的表单定义表中获取“主表域定义信息”
# 可通过“域”获取表单明细
# 用desc来确定业务线（如：人力资源、劳动派遣）
# 输入：
#   line_id：业务线
#   desc：关键词
#
def get_form(cur_oracle,cur_mysql,line_id,desc):
    # 浏览表单定义，通过关键词来获取业务线的表单
    cur = cur_oracle.execute('SELECT id,name,field_info FROM FORM_DEFINITION order by name')
    while 1:
        one = cur.fetchone()
        if one is not None:
            id = str(one[0])
            name = str(one[1])
            field_info = str(one[2])
            # field_info是一个xml定义表单，须从中找出关心的信息
            idx = field_info.find('formmain_')
            if idx>=0:
                # 获取formmain的名称，每一个表单都有对应的formmain表
                field = 'formmain_'+field_info[idx+9:idx+9+4]
            else:
                field = 'formmain_0000'
            if desc in name:
                #判断表单名称中是否包含关键字，如人力资源、劳动派遣等
                sync_line_id(cur_mysql,line_id,id,name,field)
        else:
            break

# 获取某业务线的formmain表名列表
def get_formmain(cur,line_id):
    cnt = cur.execute('select formmain_name from line_def where id=%s' % line_id)
    rec = []
    if cnt>0:
        for i in range(cnt):
            one = cur.fetchone()
            rec.append(one[0])
    return rec

# 同步formmain表记录
def sync_formmain(cur_oracle,cur_mysql,formmain_name):
    # 按formmain_name名称获取表记录
    cur = cur_oracle.execute('select * from %s order by start_date' % formmain_name)
    while 1:
        one = cur.fetchone()
        if one is not None:
            # 判断该记录是否已经被同步
            id = str(one[0])
            if is_include(cur_mysql,'formmain',id)>0:
                # 2015-12-27 因情况复杂，所以执行强行同步：已有的表删除，重新加入新记录
                cur_mysql.execute('delete from formmain where id="%s"' % id)

            # 对新纪录，构建SQL语句
            sql = 'insert into formmain'
            cnt = len(one)
            #print('>>> cnt=%d<<<' % cnt)
            if cnt>13:
                # 动态生成FIELD域
                sql += '(formmain_name,ID,STATE,START_MEMBER_ID,START_DATE,APPROVE_MEMBER_ID,APPROVE_DATE,'
                sql += 'FINISHEDFLAG,RATIFYFLAG,RATIFY_MEMBER_ID,RATIFY_DATE,SORT,MODIFY_MEMBER_ID,MODIFY_DATE,'
                for i in range(cnt-13):
                    if i==0:
                        sql += 'FIELD0001'
                    else:
                        sql += ',FIELD%04d' % (i+1)
            sql += ') values("%s"' % formmain_name
            for i in range(cnt):
                if i==3 or i==5 or i==9 or i==12:
                    sql += ',"' + str(one[i]) + '"'
                elif i<13:
                    sql += ',' + str(one[i])
                else:
                    #print(type(one[i]))
                    sql += ',"' + str(one[i]) + '"'
                #print(">>>%d-%s" % (i,sql))
            sql += ')'
            #print sql
            # 同步该记录
            cur_mysql.execute(sql)
        else:
            break

# 获取某申请单的附件文件列表
def get_file_list(cur_mysql,req_id):
    # req_id是申请单col_summary.ID
    rec = {}
    cnt = cur_mysql.execute('select form_appid,form_recordid from col_summary where id = %s' % req_id)
    if cnt>0:
        one = cur_mysql.fetchone()
        id = str(one[0])
        rec['form_def_id'] = id
        recordid = str(one[1])
        sql = 'select id,formmain_name from line_def where form_def_id = %s' % id
        cnt = cur_mysql.execute(sql)
        if cnt>0:
            one = cur_mysql.fetchone()
            id = str(one[0])
            rec['line_id'] = id
            rec['fields'] = []
            formmain_name = one[1]
            # 只判断前16个域
            for i in range(16):
                sql = 'select field%04d from %s where id = %s' % (i,formmain_name,recordid)
                #print sql
                cnt = cur_mysql.execute(sql)
                if cnt>0:
                    one = cur_mysql.fetchone()
                    f_id = one[0]
                    # 从ctp_attachment中查找，判断是否是附件文件
                    cnt = cur_mysql.execute('select filename,file_url,createdate from ctp_attachment where sub_reference = %s' % f_id)
                    if cnt>0:
                        one = cur_mysql.fetchone()
                        rec['field'].append({'field':'field%04d'%i,'finename':one[0],'file_url':one[1],'createdate':str(one[2])})
    #print rec
    return rec

# 根据 当前办理人员 查找岗位
def get_post_id(cur_mysql,current_nodes_info):
    sql = 'select org_department_id,org_post_id from org_member where id="%s"' % current_nodes_info
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        department_id = str(one[0])
        post_id = str(one[1])
        sql = 'select line_id,sn from post_rec where unit_id="%s" and post_id="%s"' % (department_id,post_id)
        #print sql
        cnt = cur_mysql.execute(sql)
        if cnt>0:
            one = cur_mysql.fetchone()
            return str(one[0]),str(one[1])
    return None,None

# 获取指定业务线某岗位的办理期限
# 输入：
#   line_id：业务线
#   sn：岗位编号
#
def get_post_deadline(cur_mysql,line_id,sn):
    sql = 'select deadline from post_deadline where line_id = %s and post_sn = %s' % (line_id,sn)
    #print("get_post_dealine")
    #print sql
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        return str(one[0])
    return None

# 通过表单ID获取OA底表各个域的说明
# 输入：
#   id：表单ID
# 输出：
#   该表单的各个域说明列表
#
def get_formmain_field_desc(cur_oracle,id):
    sql = 'select field_info,name from form_definition where id = %s' %id
    cur = cur_oracle.execute(sql)
    if cur is None:
        return None
    ret = {}
    while 1:
        one = cur.fetchone()
        if one is not None:
            ret['form_name'] = str(one[1])
            s = str(one[0]).split('\r')
            #print s
            for v in s:
                mm = v.split(' ')
                i = 0
                for m in mm:
                    if 'name="formmain' in m:
                        ret['formmain'] = m[5:].replace('"','')
                        #print(">>>Field：%s" % m)
                    if 'name="field0' in m:
                        #print(">>>%s:%s<<<" % (m[5:],mm[i+1][8:]))
                        ret[m[5:].replace('"','')] = mm[i+1][8:].replace('"','')
                    i += 1
        else:
            break
    return ret

# 通过formmain中的field获取附件文件列表
# 因在一个field中可以上传多个文件
# 输入：
#   field_id：主表中，域的内容，对于附件文件而言，它是系统附属文件ctp_attachment表的ID
# 输出：
#   文件名称
#
def get_file(cur_oracle,field_id):
    sql = 'select filename,file_url from ctp_attachment where sub_reference=%s' % id
    cur = cur_oracle.execute(sql)
    files = []
    while 1:
        one = cur.fetchone()
        if one is not None:
            f = {}
            f['filename'] = str(one[0])
            f['file_url'] = str(one[1])
        else:
            break
    return files

# 通过表单ID获取业务线ID
# 输入：
#   form_appid：是summary表的项
# 输出：
#   业务线ID
#
def get_lineid_by_formid(cur_mysql,form_appid):
    #print("---> %s" % form_appid)
    if form_appid is None:
        return None

    sql = 'select id from line_def where form_def_id = "%s"' % form_appid
    #print sql
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        #print one[0]
        return str(one[0])
    return None

# 根据申请表ID，设置定时器
# ！暂不使用！
def set_timer(cur_mysql,summary_id):
    print(">>> set_timer()")
    sql = 'select state,current_nodes_info from col_summary where id="%s" order by create_date' % summary_id
    print sql
    cnt = cur_mysql.execute(sql)
    print(">>> cnt=%d <<<" % cnt)
    # 针对已有的申请单
    if cnt>0:
        one = cur_mysql.fetchone()
        m_state = str(one[0])
        m_current_nodes_info = str(one[1])
        # 获得该记录的岗位ID、业务线ID和岗位序号
        line_id,sn = get_post_id(cur_mysql,m_current_nodes_info)
        print(">>> %s:%s <<<" % (line_id,sn))
        if line_id is not None and sn is not None:
            # 获取岗位期限
            post_deadline = get_post_deadline(cur_mysql,line_id,sn)
            if post_deadline is not None:
                sql = 'update timer set d=%s,summary_id=%s,member_id=%s where line_id=%s' % \
                        (post_deadline,summary_id,m_current_nodes_info,line_id)
                #print sql
                cur_mysql.execute(sql)

# 从form_field_def表中查找某表单具有指定字符特征的域
# 输入：
#   formmain_name：主表名称
#   s_name：需要查找的域的关键词
# 输出：
#   域名，域说明
#
def find_field_name(cur_mysql,formmain_name,s_name):

    sql = 'select field_name,name from form_field_def where formmain="%s"' % formmain_name
    cnt = cur_mysql.execute(sql)
    if cnt>0:

        for i in range(cnt):

            one = cur_mysql.fetchone()
            field_name = str(one[0])
            name = str(one[1])

            #print field_name,name

            if s_name == name:

                #print field_name, name
                return field_name, name

    return None,None

# 该方法是获取表单明细的手段
# 根据summary.form_recordid从formmain表获取指定域的值
# 输入：
#   form_recordid：是summary表中的项
#   field_name：主表域名
# 输出：
#   从主表中获取指定域的值
#
def get_field_value(cur_mysql,form_recordid,field_name):
    sql = 'select %s from formmain where id="%s"' % (field_name,form_recordid)
    #print sql
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        return str(one[0])
    return None

# 通过summary_id获取其流水号
def get_sn(cur_mysql,summary_id):

    val = get_summary_feild_value(cur_mysql,summary_id,"流水号")
    return val

# 向OA发信息
def send_message(cur_mysql,user_id,message):

    #print(">>>send_message[%s]" % message)
    sql = 'select value from sys_info where name="oa_appserver_ip"'
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        ip = str(one[0])
    else:
        ip = '127.0.0.1'

    #
    # 针对该人员增加岗位告警计数
    #
    line_id,sn = get_post_id(cur_mysql,user_id)
    if line_id is not None and sn is not None:
        sql = 'select warn_cnt from post where line_id=%s and sn=%s' % (line_id,sn)
        cnt = cur_mysql.execute(sql)
        if cnt>0:
            sql = 'insert into warn_alarm_table(flg,line_id,sn,create_date,message,member) values(2,%s,%s,now(),"%s","%s")' % (line_id,sn,message,user_id)
            cur_mysql.execute(sql)

            sql = 'select warn_cnt from post where line_id=%s and sn=%s' % (line_id,sn)
            cnt = cur_mysql.execute(sql)
            if cnt>0:
                # 针对业务线的岗位计数
                one = cur_mysql.fetchone()
                warn_cnt = int(str(one[0]))+1
                sql = 'update post set warn_cnt=%d where line_id=%s and sn=%s' % (warn_cnt,line_id,sn)
                cur_mysql.execute(sql)

                sql = 'select name from org_member where id="%s"' % user_id
                cnt = cur_mysql.execute(sql)
                if cnt>0:
                    one = cur_mysql.fetchone()
                    user = str(one[0])
                    send_message_to_oa(ip,user,message)
    return

# 因“特权许可”而撤销对指定流水号业务的“风险”告警
#
def redo_alarm(cur_mysql,line_id,yw_sn,desc):

    cur_mysql1 = mysql_conn()

    sql = 'select flg,sn,message,member from warn_alarm_table where line_id=%s and flg=3' % line_id
    cnt = cur_mysql.execute(sql)
    for i in range(cnt):

        one = cur_mysql.fetchone()
        flg = int(one[0])
        sn = str(one[1])
        message = str(one[2])
        member = str(one[3])

        s = '<%s>' % str(yw_sn)
        if (s in message) and (desc in message):

            send_info(cur_mysql1,member,'【数据铁笼提示】：领导授权撤回“%s”的风险记录，请知悉。' % message)

            # 向纪检汇报
            members = get_leader(cur_mysql1,0,0,1)
            for m in members:
                send_info(cur_mysql1,m,'【数据铁笼提示】：领导授权撤回“%s”的风险记录，请知悉。' % message)

            sql = 'select alarm_cnt,warn_cnt from post where line_id=%s and sn=%s' % (line_id,sn)
            cnt = cur_mysql1.execute(sql)
            if cnt>0:
                one = cur_mysql1.fetchone()
                alarm_cnt = int(one[0])
                warn_cnt = int(one[1])
                if flg==2 and warn_cnt>0:
                    warn_cnt -= 1
                if flg==3 and alarm_cnt>0:
                    alarm_cnt -= 1
                sql = 'update post set alarm_cnt=%d,warn_cnt=%d where line_id=%s and sn=%s' % (alarm_cnt,warn_cnt,line_id,sn)
                cur_mysql1.execute(sql)

    cur_mysql1.close()

    return

# 向OA发风险告警信息
def send_alarm(cur_mysql,user_id,summary_id,line_id,message):

    print(">>>send_alarm:%s,%s,%s,%s<<<" % (user_id,summary_id,line_id,message))

    sql = 'select value from sys_info where name="oa_appserver_ip"'
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        ip = str(one[0])
    else:
        ip = '127.0.0.1'

    #
    # 针对该人员增加岗位告警计数
    #
    oline_id,sn = get_post_id(cur_mysql,user_id)

    print(">>>%s,%s<<<" % (oline_id,sn))

    if line_id is not None and sn is not None:
        sql = 'select warn_cnt from post where line_id=%s and sn=%s' % (line_id,sn)
        cnt = cur_mysql.execute(sql)
        if cnt>0:

            sql = 'insert into warn_alarm_table(flg,line_id,sn,create_date,message,member,summary_id) values(3,%s,%s,now(),"%s","%s","%s")' % (line_id,sn,message,user_id,summary_id)
            cur_mysql.execute(sql)

            sql = 'select alarm_cnt from post where line_id=%s and sn=%s' % (line_id,sn)
            cnt = cur_mysql.execute(sql)
            if cnt>0:
                # 针对业务线的岗位计数
                one = cur_mysql.fetchone()
                warn_cnt = int(str(one[0]))+1
                sql = 'update post set alarm_cnt=%d where line_id=%s and sn=%s' % (warn_cnt,line_id,sn)
                cur_mysql.execute(sql)

    sql = 'select name from org_member where id="%s"' % user_id
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        user = str(one[0])
        send_message_to_oa(ip,user,message)
    return

# 向上级汇报信息
def send_info(cur_mysql,user_id,message):

    sql = 'select value from sys_info where name="oa_appserver_ip"'
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        ip = str(one[0])
    else:
        ip = '127.0.0.1'

    sql = 'select name from org_member where id="%s"' % user_id
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        user = str(one[0])
        send_message_to_oa(ip,user,message)

    return

def send_message_to_oa(ip,user,message):

    token = "0"

    cmd = 'curl http://%s/seeyon/rest/token ' % ip
    cmd += '-X POST -i -H "Content-Type:application/json" -H "Accept:application/json" '
    cmd += '-d \'{"userName":"sjtl","password":"123456"}\''
    #print cmd
    r = os.popen(cmd)
    s = r.read().split('\r\n')
    for v in s:
        if '"id" : "' in v:
            ss = v.split(' ')
            token = ss[4].replace('"','')

    cmd = 'curl http://%s/seeyon/rest/message/loginName ' % ip
    cmd += '-X POST -i -H "Content-Type:application/json" -H "Accept:application/json" -H "token:%s" ' % token
    cmd += '-d \'{"loginNames": ["%s"],"sendUserId" : "8764456166134006930","content" : "%s"}\'' % (user,message)
    #print cmd
    r = os.popen(cmd)
    s = r.read().split('\r\n')
    #print s

# 2015-12-23
# 用于接收向铁笼系统的信息反馈
#
def receive_message_from_oa(cur_mysql):

    sql = 'select value from sys_info where name="oa_appserver_ip"'
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        ip = str(one[0])
    else:
        ip = '127.0.0.1'

    token = "0"

    cmd = 'curl http://%s/seeyon/rest/token ' % ip
    cmd += '-X POST -i -H "Content-Type:application/json" -H "Accept:application/json" '
    cmd += '-d \'{"userName":"sjtl","password":"123456"}\''
    #cmd += '-d \'{"userName":"汪杰","password":"123456"}\''
    #print cmd
    r = os.popen(cmd)
    s = r.read().split('\r\n')
    for v in s:
        #print v
        if '"id" : "' in v:
            ss = v.split(' ')
            token = ss[4].replace('"','')

    cmd = 'curl http://%s/seeyon/rest/message/unread/8764456166134006930 ' % ip
    #cmd = 'curl http://%s/seeyon/rest/message/unread/-2438837490383764854 ' % ip
    cmd += '-X GET -i -H "Content-Type:application/json" -H "Accept:application/json" -H "token:%s" ' % token
    #print cmd
    r = os.popen(cmd)
    message = r.read().split('\r\n')

    return message

# 通过人员ID获取其姓名
#
def get_user_name(cur_mysql,member):
    sql = 'select name from org_member where id="%s"' % member
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        return str(one[0])
    return ""

# lvl：类型，0：预警，1：风险
def get_leader(cur_mysql,line_id,sn,lvl):

    # 预警，告知领导
    members = []

    # 获取 该业务线节点 的领导
    if lvl==0:
        sql = 'select member from leader where line_id=%s and sn=%s' % (line_id,sn)
        print sql
        cnt = cur_mysql.execute(sql)
        for i in range(cnt):
            one = cur_mysql.fetchone()
            member = str(one[0])
            members.append(member)

    # 获取 纪检部门 的人员
    elif lvl==1:
        # 风险，要推送给纪检
        sql = 'select member from leader where line_id=0 and sn=0'
        cnt = cur_mysql.execute(sql)
        for i in range(cnt):
            one = cur_mysql.fetchone()
            member = str(one[0])
            members.append(member)

    return members

# 通过业务线和节点序号获取节点名称
#
def get_post_name(cur_mysql,line_id,sn):
    post_name = ''
    sql = 'select name from post where line_id=%s and sn=%s' % (line_id,sn)
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        post_name = str(one[0])
    return post_name

# 处理日切
#   负责把summary中的deadline和cnt计数减一(天数)
#
def new_day(cur_mysql,cur_mysql1):

    '''
    sql = 'SELECT dayofweek(NOW())'
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        week = int(one[0])
        if week==1 or week==7:
            # 周日、周六非工作日
            return
    '''

    sql = 'select * from special_day where year=year(curdate()) and month=month(curdate()) and day=dayofmonth(curdate())'
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        # 今天是法定非工作日
        return

    values = []

    sql = 'select deadline,cnt,subject,id from col_summary where state=0 order by create_date'
    cnt = cur_mysql.execute(sql)
    if cnt>0:

        for i in range(cnt):

            one = cur_mysql.fetchone()

            summary_deadline = int(one[0])
            summary_cnt = int(one[1])
            subject = str(one[2])
            summary_id = str(one[3])

            if ("人力资源服务许可" in subject) or ("劳务派遣" in subject) or ("自动发起" in subject):

                summary_cnt -= 1
                summary_deadline -= 1
                value = {}
                value['id'] = summary_id
                value['deadline'] = summary_deadline
                value['cnt'] = summary_cnt
                values.append(value)

        for v in values:
            sql = 'update col_summary set deadline=%s,cnt=%s where id="%s"' % (v['deadline'],v['cnt'],v['id'])
            cur_mysql.execute(sql)

    # 事后监督，提取2天预警
    supervision(cur_mysql,cur_mysql1,2)

    return

# 每小时处理
# 根据工作时间明细，判断是否发出必要的“提前”预警信息
#
def one_hour(cur_mysql,cur_mysql1,cur_mysql2):

    """
    sql = 'SELECT dayofweek(NOW())'
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        week = int(one[0])
        if week==1 or week==7:
            # 周日、周六非工作日
            return
    """

    sql = 'select * from special_day where year=year(curdate()) and month=month(curdate()) and day=dayofmonth(curdate())'
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        # 今天是法定非工作日
        return

    # 当前时间
    now = datetime.datetime.now()

    # 工作时间内
    if now.hour>=9 and now.hour<=17:

        # 根据当前时间的“小时”数，获取明细
        sql = 'select s_h,e_h,nday,lvl,cnt,flg from worktime_mx where cur=%d' % now.hour
        cnt = cur_mysql.execute(sql)
        for i in range(cnt):

            one = cur_mysql.fetchone()
            d_s_h = int(one[0])
            d_e_h = int(one[1])
            d_nday = int(one[2])
            d_lvl = int(one[3])
            d_cnt = int(one[4])
            d_flg = int(one[5])

            # 接下来是一项非常复杂的操作过程
            # 用d_nday去获取满足条件的节点sn，期限为1天的sn，和其行为2天的sn
            # 用d_cnt、sn、state=0、line_id=1or2去查找summary记录
            # 比较summary.resent_time的小时数是否在d_s_h和d_e_h之间。
            #   注：1）若flg=1，表示区域包含换天，例如今日17点到明日10点之间
            #   (cnt=d_cnt-1 and resent_time.hour>=17) or (cnt=d_cnt and resent_time<=10)
            #      2）若flg=0，则表示该时段在同天，例如今日11点至今日14点之间
            #   (cnt=d_cnt and resend_time.hour>=11) or (cnt=d_cnt and resent_time<=14)
            #
            # 若满足条件，则需根据lvl发出“时限”预警

            sns = []
            sql = 'select line_id,post_sn from post_deadline where deadline=%d' % d_nday
            #print sql
            cnt1 = cur_mysql1.execute(sql)
            for i in range(cnt1):
                one = cur_mysql1.fetchone()
                v = {}
                v['line_id'] = int(one[0])
                v['sn'] = int(one[1])
                sns.append(v)

            for s in sns:

                # 获取满足条件的summary记录
                sql = 'select current_nodes_info,subject,resent_time from col_summary where cnt=%d and sn=%d and line_id=%d and state=0' \
                      % (d_cnt,s['sn'],s['line_id'])
                cnt1 = cur_mysql1.execute(sql)
                for i in range(cnt1):
                    one = cur_mysql1.fetchone()

                    current_nodes_info = str(one[0])
                    subject = str(one[1])
                    resent_time = str(one[2])

                    if resent_time=="None" or resent_time=="NONE":
                        continue

                    if ("人力资源服务许可" in subject) or ("劳务派遣" in subject) or ("自动发起" in subject):

                        # 时间间隔在同一天
                        d = datetime.datetime.strptime(resent_time,"%Y-%m-%d %H:%M:%S")
                        if (d.hour>=d_s_h) and (d.hour<d_e_h):
                            # 满足预警要求

                            #print(">>>Here 2!,%d:%d:%d<<<" % (d.hour,d_s_h,d_e_h))

                            # 获取节点名称
                            post_name = get_post_name(cur_mysql2,s['line_id'],s['sn'])

                            # 获取人员名称
                            user_name = get_user_name(cur_mysql2,current_nodes_info)
                            if d_lvl==0:
                                #print(">>>alarm<<<")
                                send_info(cur_mysql2,current_nodes_info,"【数据铁笼预警】：%s，在办的《%s》%s即将超期，请尽快办理，谢谢！" \
                                    % (user_name,subject,post_name))
                            else:
                                user_name = get_user_name(cur_mysql2,current_nodes_info)
                                send_message(cur_mysql2,current_nodes_info,"【数据铁笼预警】：%s，在办的《%s》%s即将超期，请加快办理。" \
                                    % (user_name,subject,post_name))
                                # 向上级汇报
                                members = get_leader(cur_mysql2,s['line_id'],s['sn'],0)
                                for member in members:
                                    leader_name = get_user_name(cur_mysql2,member)
                                    send_info(cur_mysql2,member,"【数据铁笼预警】%s，好：%s在办的《%s》%s即将超期，请知悉。" \
                                        % (leader_name,user_name,subject,post_name))

    # 放置“超时”判断，及“风险”告警
    # 检索col_summary表（state=0,cnt=0或deadline=0,line_id>0），看其当前时间（小时）-受理时间（resent_time）小时=1，则该业务超时
    #
    sql = 'select current_nodes_info,subject,resent_time,id,line_id,sn from col_summary where cnt=0 and state=0 and line_id>0 order by start_date'
    cnt = cur_mysql.execute(sql)
    for i in range(cnt):

        one = cur_mysql.fetchone()
        current_nodes_info = str(one[0])
        subject = str(one[1])
        resent_time = str(one[2])
        summary_id = str(one[3])
        line_id = str(one[4])
        sn = str(one[5])

        if (("人力资源服务许可" in subject) or ("劳务派遣" in subject) or ("自动发起" in subject)) and resent_time!="None":

            d = datetime.datetime.strptime(resent_time,"%Y-%m-%d %H:%M:%S")
            if (now.hour-d.hour)==1:

                # 该申请节点办理超期
                user_name = get_user_name(cur_mysql1,current_nodes_info)
                send_alarm(cur_mysql1,current_nodes_info,summary_id,line_id,"【数据铁笼风险提示】：%s，在办的《%s》%s已超期，请加快办理。" \
                    % (user_name,subject,post_name))

                # 向上级汇报
                members = get_leader(cur_mysql1,line_id,sn,0)
                members += get_leader(cur_mysql1,line_id,sn,1)
                for member in members:
                    leader_name = get_user_name(cur_mysql1,member)
                    send_info(cur_mysql1,member,"【数据铁笼风险通报】%s，好：%s在办的《%s》%s已超期，请知悉。" \
                        % (leader_name,user_name,subject,post_name))

                sql = 'update col_summary set cnt=-1 where id="%s"' % summary_id
                cur_mysql1.execute(sql)

    # 业务总期限（8天）提前2天预警
    sql = 'select subject,resent_time,line_id from col_summary where deadline=2 and state=0 and line_id>0 order by start_date'
    cnt = cur_mysql.execute(sql)
    for i in range(cnt):

        one = cur_mysql.fetchone()
        subject = str(one[0])
        resent_time = str(one[1])
        line_id = str(one[2])

        if ("人力资源服务许可" in subject) or ("劳务派遣" in subject) or ("自动发起" in subject):

            d = datetime.datetime.strptime(resent_time,"%Y-%m-%d %H:%M:%S")
            if (now.hour-d.hour)==0:

                # 告知科室处长
                members = get_leader(cur_mysql1,line_id,1,0)
                for member in members:
                    send_info(cur_mysql1,member,"【数据铁笼风险提示】：处室在办理《%s》时，离总期限还有一天时间，请知悉。" \
                        % (subject))

    sql = 'select subject,resent_time,id,line_id from col_summary where deadline=0 and state=0 and line_id>0 order by start_date'
    cnt = cur_mysql.execute(sql)
    for i in range(cnt):

        one = cur_mysql.fetchone()
        subject = str(one[0])
        resent_time = str(one[1])
        summary_id = str(one[2])
        line_id = str(one[3])

        if ("人力资源服务许可" in subject) or ("劳务派遣" in subject) or ("自动发起" in subject):

            d = datetime.datetime.strptime(resent_time,"%Y-%m-%d %H:%M:%S")
            if (now.hour-d.hour)==1:

                # 通知处室处长
                members = get_leader(cur_mysql1,line_id,1,0)
                for member in members:
                    send_alarm(cur_mysql1,member,summary_id,line_id,"【数据铁笼风险提示】：处室在办理《%s》时，总期限已超期，请知悉。" \
                        % (subject))

                # 向上级汇报
                members = get_leader(cur_mysql1,line_id,1,1)
                for member in members:
                    leader_name = get_user_name(cur_mysql1,member)
                    send_info(cur_mysql1,member,"【数据铁笼风险通报】%s，好：处室在办的《%s》已超出总期限要求，请知悉。" \
                        % (leader_name,subject))

                sql = 'update col_summary set deadline=-1 where id="%s"' % summary_id
                cur_mysql1.execute(sql)

    return

# 处理日切
#   每天12点预警
#   不再使用 -2015-12-25-
def half_day(cur_mysql,cur_mysql1):

    sql = 'SELECT dayofweek(NOW())'
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        week = int(one[0])
        if week==1 or week==7:
            # 周日、周六非工作日
            return

    sql = 'select * from special_day where year=year(curdate()) and month=month(curdate()) and day=dayofmonth(curdate())'
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        # 今天是法定非工作日
        return

    sql = 'select cnt,current_nodes_info,subject,line_id,sn from col_summary where state=0 order by create_date'
    cnt = cur_mysql.execute(sql)
    values = []
    if cnt>0:

        for i in range(cnt):

            one = cur_mysql.fetchone()
            summary_cnt = int(one[0])
            current_nodes_info = str(one[1])
            subject = str(one[2])
            line_id = str(one[3])
            sn = str(one[4])

            if ("人力资源服务许可" in subject) or ("劳务派遣" in subject) or ("自动发起" in subject):

                if summary_cnt==0:
                    # 该业务快要超期了

                    # 获取节点名称
                    post_name = get_post_name(cur_mysql1,line_id,sn)
                    # 获取人员名称
                    user_name = get_user_name(cur_mysql1,current_nodes_info)
                    send_message(cur_mysql1,current_nodes_info,"【数据铁笼预警】：%s，在办的《%s》%s即将超期，请尽快办理，谢谢！" % (user_name,subject,post_name))

                    # 向上级汇报
                    members = get_leader(cur_mysql1,line_id,sn,0)
                    for member in members:
                        leader_name = get_user_name(cur_mysql1,member)
                        #send_alarm(cur_mysql1,member,"【数据铁笼提示】：%s，好：%s在办的《%s》%s已超期，请知悉。" % (leader_name,user_name,subject,post_name))            # 负数表示超出的天数
                        send_info(cur_mysql1,member,"【数据铁笼风险提示】%s，好：%s在办的《%s》%s即将超期，请知悉。" % (leader_name,user_name,subject,post_name))

    return

# 比较summary记录是否未按时序办理，即在该申请前是否还有早于它的申请未办
# 存在“卡队”办理风险
#
def comp_date(cur_mysql,summary_id):

    # 2015-12-22 增加获取 业务流水号
    sql = 'select create_date,current_nodes_info,yw_sn from col_summary where id="%s"' % summary_id
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        create_date = str(one[0])
        current_nodes_info = str(one[1])
        yw_sn = str(one[2])
        # 得到办理人的岗位信息
        line_id,sn = get_post_id(cur_mysql,current_nodes_info)
        if line_id is not None and sn is not None:
            sql = 'select * from col_summary where state=0 and line_id=%s and sn=%s and unix_timestamp(create_date)<unix_timestamp("%s")' % \
                  (line_id,sn,create_date)
            #print sql
            cnt = cur_mysql.execute(sql)
            if cnt>0:
                return True,current_nodes_info,yw_sn
    return False,None,None

# 计算业绩
# 采用summary扫描方式处理
def sum_summary(cur_mysql,line_id):
    # 计算已完成业绩
    sql = 'select * from col_summary where state=3 and line_id=%s' % line_id
    total_cnt = cur_mysql.execute(sql)
    #print total_cnt
    sql = 'select sn from post where line_id = %s' % line_id
    cnt = cur_mysql.execute(sql)
    sns = []
    for i in range(cnt):
        sn = cur_mysql.fetchone()
        sns.append(str(sn[0]))
    #print sns
    val = []
    for sn in sns:
        if int(sn)==0:
            cnt = 0
        else:
            sql = 'select * from col_summary where state=0 and sn=%s and line_id=%s' % (sn,line_id)
            cnt = cur_mysql.execute(sql)
        sql = 'update post set curr=%d where sn=%s and line_id=%s' % (cnt,sn,line_id)
        cur_mysql.execute(sql)
        val.append(cnt)
    #print val
    # 以下是一段天书，不是思考出来的，是试验得到的
    vvv = 0
    vv = []
    i = -1
    for j in range(len(val)-1):
        vvv += val[i]
        vv.append(vvv)
        i -= 1
    #print vv
    i = -1
    for j in range(len(sns)-1):
        cnt = vv[i]
        sql = 'update post set total=%d where sn=%s and line_id=%s' % (cnt+total_cnt,sns[j],line_id)
        cur_mysql.execute(sql)
        i -= 1
    return

# 获取申请单“许可证状态”
# 用于判断业务审批是否正常，若许可证状态=未通过，则说明本次申请被退回
# 要求：summary中必须设置此域；对不设置该域的，视同批准
def get_summary_ctp_state(cur_oracle,cur_mysql,summary_id):

    sql = 'select form_appid,form_recordid from col_summary where id="%s"' % summary_id
    #print sql
    cnt = cur_mysql.execute(sql)
    if cnt>0:

        one = cur_mysql.fetchone()
        form_appid = str(one[0])
        form_recordid = str(one[1])

        sql = 'select formmain_name from line_def where form_def_id="%s"' % form_appid
        # print sql
        cnt = cur_mysql.execute(sql)
        if cnt>0:

            one = cur_mysql.fetchone()
            formmain_name = str(one[0])

            # print(">>>formmain_name=%s<<<" % formmain_name)

            # 获取许可证状态
            field_name,name = find_field_name(cur_mysql,formmain_name,"许可证状态")
            if field_name is not None:

                # 通过域名称查找summary的主表记录
                val = get_field_value(cur_mysql,form_recordid,field_name)
                if ":" in val:
                    # 旧的记录，该域为日期
                    return None

                if val is not None and val != 'NONE' and val != 'None':

                    # sql = 'select showvalue,enumvalue from ctp_enum_item where id=%s' % str(val)
                    sql = 'select showvalue from ctp_enum_item where id=%s' % str(val)
                    # print sql
                    cur = cur_oracle.execute(sql)
                    if cur == None:
                        return None

                    showvalue = None
                    while 1:
                        one = cur.fetchone()
                        if one is not None:
                            # 获得该域枚举的名称和值
                            showvalue = str(one[0])
                            # enumvalue = str(one[1])
                            # print showvalue, enumvalue
                        else:
                            break
                    return showvalue
    return None

# 分析state=3的summary记录的状态，若是批准办证，则置其state=3且vouch=2015（否则vouch=2000），并置start_date为6个月后
# start_date作为事后监督的回访期限用
def set_summary_state(cur_oracle,cur_mysql):

    # 系统在添加summary时，将vouch置为 0
    sql = 'select id from col_summary where state=3 and vouch=0'
    # print sql
    cnt = cur_mysql.execute(sql)
    summarys = []
    for i in range(cnt):
        one = cur_mysql.fetchone()
        summary_id = str(one[0])
        summarys.append(summary_id)

    vouch = 2015
    for summary_id in summarys:
        ctp_state = get_summary_ctp_state(cur_oracle,cur_mysql,summary_id)
        if ctp_state is not None:
            if "未通过" in ctp_state:
                vouch = 2000
        sql = 'update col_summary set vouch=%s,start_date=DATE_ADD(current_timestamp,INTERVAL 6 MONTH) where id="%s"' % (vouch,summary_id)
        #print sql
        cur_mysql.execute(sql)
    return

# 要从summary中解析出“分管领导指派优先办理”的行为，并通过流水号与相关的summary表单关联
# 1）根据该事件的subject可以判断业务线line_id，例如subject为“劳务派遣行政许可申请”
# 2）根据summary.form_appid从form_definition表中获取其名称为“分管领导指派优先办理”，并获得主表名称（如：field0067）
# 3）从主表中查找“流水号”域名称，如：field0001
# 4）根据summary.form_recordid从主表中获取“流水号”域的值（即，流水号）
# 5）从summary表中查找到该“流水号”的表记录，并置上“优先通过”标记
# 6）从warn_alarm_table表中查找匹配的记录，若有，则需撤回该人员、节点的“风险”提示 -2015-12-25
#
def set_summary_pri(cur_mysql,summary_id):

    cur_mysql1 = mysql_conn()

    sql = 'select subject,form_recordid,form_appid from col_summary where id="%s"' % summary_id
    cnt = cur_mysql.execute(sql)
    if cnt>0:

        one = cur_mysql.fetchone()
        subject = str(one[0])
        form_recordid = str(one[1])
        form_appid = str(one[2])

        # 查找“特权”报文
        if "分管领导指派优先办理" in subject:

            sql = 'select formmain_name,name from line_def where form_def_id="%s"' % form_appid
            cnt = cur_mysql.execute(sql)
            if cnt>0:

                # 查找”特权“的主表名称
                one = cur_mysql.fetchone()
                formmain_name = str(one[0])
                name = str(one[1])

                #print name
                if "分管领导指派优先办理" in name:

                    # 查找“特权”针对的业务流水号
                    field_name,name = find_field_name(cur_mysql,formmain_name,"流水号")

                    #print(">>>field_name=%s,name=%s<<<" % (field_name,name))
                    if field_name is not None:

                        val = get_field_value(cur_mysql,form_recordid,field_name)
                        if val is not None:

                            # 查找具有该流水号的summary记录
                            sql = 'select id,line_id from col_summary where yw_sn="%s"' % val
                            cnt = cur_mysql.execute(sql)
                            if cnt > 0:

                                one = cur_mysql.fetchone()
                                o_summary_id = str(one[0])
                                line_id = str(one[1])

                                # 设置特权
                                sql = 'update col_summary set pri=1 where id="%s"' % o_summary_id
                                cur_mysql.execute(sql)

                                # 撤销已发生的“风险”告警
                                redo_alarm(cur_mysql,line_id,val,'仍有未办理业务')
                                # 撤销受理缺失资料的“风险”告警
                                redo_alarm(cur_mysql,line_id,val,'提交材料存在缺失项')

    cur_mysql1.close()

    return

# 获取 业务线 上人员列表
#
def get_line_member(cur_mysql,line_id):

    members = []

    if line_id==1:
        # 针对“人力资源”
        sql = 'select a.id from org_member a, org_unit b where b.name="人力资源市场处" and a.org_department_id=b.id'
    elif line_id==2:
        # 针对“劳动派遣”
        sql = 'select a.id from org_member a, org_unit b where b.name="劳动关系处" and a.org_department_id=b.id'
    else:
        # 其它处室暂无支撑
        return members

    cnt = cur_mysql.execute(sql)
    for i in range(cnt):
        one = cur_mysql.fetchone()
        members.append(str(one[0]))

    return members

# 事后监督期限处理，放到“日切”处理里面
# 针对 state=3 and vouch=2015 的summary记录，其期限为 start_date
# 提前n_days天发出预警；超期发出风险提示
def supervision(cur_mysql,cur_mysql1,n_days):

    # 预警
    sql = 'select subject,line_id from col_summary where state=3 and vouch=2015 and to_days(start_date)-to_days(now())=%d' % n_days
    cnt = cur_mysql.execute(sql)
    for i in range(cnt):

        one = cur_mysql.fetchone()
        subject = str(one[0])
        line_id = str(one[1])

        # 向业务线处室发出预警
        # 获取人员名称
        members = get_line_member(cur_mysql1,line_id)
        for member in members:
            send_message(cur_mysql1,member,"【数据铁笼预警】：你处室办理的《%s》事后监督期限即将超期，请尽快办理，谢谢！" % subject)

    # 风险
    sql = 'select subject,line_id,id from col_summary where state=3 and vouch=2015 and to_days(start_date)-to_days(now())=0'
    cnt = cur_mysql.execute(sql)
    for i in range(cnt):

        one = cur_mysql.fetchone()
        subject = str(one[0])
        line_id = str(one[1])
        summary_id = str(one[2])

        # 向业务线处室发出风险提示，向上级发出风险汇报
        # 获取人员名称
        members = get_line_member(cur_mysql1,line_id)
        for member in members:
            send_alarm(cur_mysql1,member,summary_id,line_id,"【数据铁笼风险提示】：你处室办理的《%s》事后监督已超期，请加快办理。" % subject)

    return

# 获取指定summary表记录的主表单域值
def get_summary_feild_value(cur_mysql,summary_id,field_desc):

    value = None

    sql = 'select form_appid,form_recordid from col_summary where id="%s"' % summary_id
    cnt = cur_mysql.execute(sql)
    if cnt>0:

        one = cur_mysql.fetchone()
        form_appid = str(one[0])
        form_recordid = str(one[1])
        sql = 'select formmain_name from line_def where form_def_id="%s"' % form_appid
        cnt = cur_mysql.execute(sql)
        if cnt>0:

            one = cur_mysql.fetchone()
            formmain_name = str(one[0])
            print(">>>formmain_name=%s<<<" % formmain_name)
            field_name,name = find_field_name(cur_mysql,formmain_name,field_desc)
            print(">>>field_name:%s,name:%s,form_recordid=%s<<<" % (field_name,name,form_recordid))
            if field_name is not None:
                value = get_field_value(cur_mysql,form_recordid,field_name)

    return value

# 获取指定summary的受理时间
#
def get_summary_submit_date(cur_mysql,summary_id):

    submit_date = get_summary_feild_value(cur_mysql,summary_id,"受理时间")
    return submit_date

# 判断是否为非工作日
#
def is_holiday(str_date):
    return True

# 验证该业务线的申请是否带齐必要的附件
# 若未带齐，则发出“风险”警告
#
def chk_file(cur_mysql,summary_id,line_id):

    #print(">>>chk_file: id=%s,line_id=%s" % (summary_id,line_id))

    if int(line_id)==2:
        # 劳务派遣
        fn_line=[]
        fn_line.append("劳务派遣经营许可申请书")
        fn_line.append("申请报告")
        fn_line.append("营业执照副本")
        fn_line.append("公司章程复印件")
        fn_line.append("验资机构出具的验资报告或者财务审计报告")
        fn_line.append("法定代表人第二代居民身份证复印件")
        fn_line.append("经营场所的使用证明")
        fn_line.append("与开展派遣业务相适应的办公设施设备清单")
        fn_line.append("信息管理系统的清单及功能说明")
        fn_line.append("劳务派遣管理制度")
        fn_line.append("拟与用工单位签订的劳务派遣协议文本")

        for field in fn_line:
            val = get_summary_feild_value(cur_mysql,summary_id,field)
            #print(">>>val=%s<<<" % val)
            if val==None or val=="None" or val=="NONE":
                return False

    if int(line_id)==1:
        # 人力资源
        fn_line=[]
        fn_line.append("贵阳市申请设立人力资源服务机构审批表")
        fn_line.append("诚信守法经营的承诺书")
        fn_line.append("工商营业执照副本")
        fn_line.append("开办资金证明")
        fn_line.append("与服务内容相适应的场所证明材料")
        fn_line.append("拟设立人力资源服务机构的工作章程")
        fn_line.append("与申请业务范围")
        fn_line.append("名以上具备国家承认的大专以上学历")
        fn_line.append("拟任负责人法定代表人的基本情况身份证明")
        fn_line.append("工作人员的彩色照片")

        for field in fn_line:
            #print(">>>field:%s<<<" % field)
            val = get_summary_feild_value(cur_mysql,summary_id,field)
            #print(">>>val=%s<<<" % val)
            if val==None or val=="None" or val=="NONE":
                return False

    return True

# 判读是否“补正”
#
def is_wait(cur_oracle,cur_mysql,summary_id):

    # 获取是否需要补正选项值
    val = get_summary_feild_value(cur_mysql,summary_id,"是否需要补正")
    if val!=None and val!="None" and val!="NONE":

        sql = 'select showvalue from ctp_enum_item where id=%s' % val
        cur = cur_oracle.execute(sql)

        while 1:

            one = cur.fetchone()
            if one==None:
                break

            showvalue = str(one[0])
            if "是" in showvalue:
                # 如果是，则返回 True
                return True

    # 不需要
    return False

# 判断是否为工作日
#
def is_workday(cur_mysql,year,month,day):

    sql = 'select * from special_day where year=%d and month=%d and day=%d' % (year,month,day)
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        return False
    return True

# 对齐到工作日
# 若该时间点是在非工作日内，则需要向前推至工作日的16:59:59
#
def to_workday(cur_mysql,date_d):

    # 防止“死锁”的计数器
    n = 31
    while 1:
        if not is_workday(cur_mysql,date_d.year,date_d.month,date_d.day):

            # 设定为 工作日 的最后 时间
            date_d.hour = 16
            date_d.minute = 59
            date_d.second = 59

            # 若，这天不是工作日，则，需要往前推一天
            date_d += datetime.timedelta(days=-1)
        else:
            return date_d
        n -= 1
        if n<=0:
            break
    return date_d

# 计算时间段内有效的工作时间
# 需要抛开 非工作日 和 非工作时段，工作时段（9~12,13~17）
#
def cal_workdays(cur_mysql,start_date,end_date):

    dlt_time = 0

    # 调整 时间点，规整到 工作范围内
    start_d = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
    if start_d.hour<9:
        # 对于 0~9点之间的时间，视同前一天16:59:59
        start_d += datetime.timedelta(days=-1)
        cur_d = datetime.datetime(start_d.year,start_d.month,start_d.day,16,59,59,0)
        start_d = cur_d
    elif start_d.hour>17:
        # 对于 17~24点之间的时间，视同当天16:59:59
        cur_d = datetime.datetime(start_d.year,start_d.month,start_d.day,16,59,59,0)
        start_d = cur_d
    elif start_d.hour==12:
        # 去掉 12点（1小时）的午餐时间
        cur_d = datetime.datetime(start_d.year,start_d.month,start_d.day,13,0,0,0)
        end_d = cur_d

    end_d = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
    if end_d.hour<9:
        # 对于 0~9点之间的时间，视同前一天16:59:59
        end_d += datetime.timedelta(days=-1)
        cur_d = datetime.datetime(end_d.year,end_d.month,end_d.day,16,59,59,0)
        end_d = cur_d
    elif end_d.hour>17:
        # 对于 17~24点之间的时间，视同当天16:59:59
        cur_d = datetime.datetime(end_d.year,end_d.month,end_d.day,16,59,59,0)
        end_d = cur_d
    elif end_d.hour==12:
        # 去掉 12点（1小时）的午餐时间
        cur_d = datetime.datetime(end_d.year,end_d.month,end_d.day,13,0,0,0)
        end_d = cur_d

    if start_d>=end_d:
        return dlt_time

    ''' 暂不考虑这种异常
    if start_d>end_d:
        # 错误的时间段
        return 365*24*60
    '''

    # 将时间点规整到 有效的工作日 上
    # 原则：
    #   若时间点属于非工作日，则往前推，直到最后一个非工作日，并把时间定为该日的16:59:59
    #
    start_d = to_workday(cur_mysql,start_d)
    end_d = to_workday(cur_mysql,end_d)

    if start_d==end_d:
        return dlt_time

    nd = 0
    cur_d = datetime.datetime(start_d.year,start_d.month,start_d.day,23,59,59,0)
    while end_d>(cur_d+datetime.timedelta(days=1)):
        cur_d += datetime.timedelta(days=1)
        if is_workday(cur_mysql,cur_d.year,cur_d.month,cur_d.day):
            nd += 1
        if nd>30:
            break

    # 计算当天起始时间段的花费时间（秒），此时的 hour 肯定在[9,12]和[13,17]范围内
    if start_d.hour<12:
        dlt_t1 = 4*3600 + (datetime.datetime(end_d.year,end_d.month,end_d.day,12,0,0,0) - start_d).seconds
    else:
        dlt_t1 = (datetime.datetime(end_d.year,end_d.month,end_d.day,17,0,0,0) - start_d).seconds

    # 计算当天终止时间段的花费时间（秒）
    if end_d.hour<12:
        dlt_t2 = (end_d - datetime.datetime(end_d.year,end_d.month,end_d.day,9,0,0,0)).seconds
    else:
        dlt_t2 = 3*3600 + (end_d - datetime.datetime(end_d.year,end_d.month,end_d.day,13,0,0,0)).seconds

    # 计算总花费时间（分钟），每天按7.5小时计
    dlt_time = (dlt_t1 + dlt_t2)/60 + nd*75*6

    return dlt_time

# 业务日志
# yw_sn：业务流水号
# summary_id：申请摘要ID
# member_id：办理人ID
# sn：节点ID
# start_date：起始时间
# end_date：结束时间
# dlt_time：用时（分钟）
#
def yw_log(cur_mysql,summary_id,member_id,sn,start_date,end_date,dlt_time):

    # 获取关联ID
    _uuid = create_UUID()

    # 根据协同摘要 获取 业务主题、业务线、业务流水号
    sql = 'select subject,line_id,yw_sn from col_summary where id="%s"' % summary_id
    cnt = cur_mysql.execute(sql)
    if cnt>0:
        one = cur_mysql.fetchone()
        subject = str(one[0])
        line_id = str(one[1])
        yw_sn = str(one[2])

        # 获取 人员名称、岗位名称
        sql = 'select a.name,b.name from org_member a, org_post b where a.id="%s" and b.id=a.org_postid' % member_id
        cnt = cur_mysql.execute(sql)
        if cnt>0:
            one = cur_mysql.fetchone()
            member = str(one[0])
            post = str(one[1])

            # 获取 业务线节点 名称
            sql = 'select info from sn_desc where line_id=%s and id=%s' % (line_id,str(sn))
            cnt = cur_mysql.execute(sql)
            if cnt>0:
                one = cur_mysql.fetchone()
                sn_info = str(one[0])

                # 获取 业务线节点 时限
                sql = 'select deadline from post_deadline where line_id=%s and post_sn=%s' % \
                      (line_id,str(sn))
                cnt = cur_mysql.execute(sql)
                if cnt>0:
                    one = cur_mysql.fetchone()
                    dl = int(one[0])
                    dlt_rate = dlt_time*100/(dl*75*6)
                    # 添加 工作流日志记录
                    sql = 'insert into wf_log(uuid,sn,member,post,subject,start_date,end_date,dlt_time,dlt_rate) ' \
                          'value ("%s","%s","%s","%s","%s","%s","%s",%s,%s)' % \
                            (_uuid,sn_info,member,post,subject,start_date,end_date,dlt_time,dlt_rate)
                    cur_mysql.execute(sql)

                    # 加入到 业务流水日志
                    sql = 'insert into sn_log(yw_sn,uuid,flg) value("%s","%s",%d)' % (yw_sn,_uuid,0)
                    # 加入到 人员日志
                    sql = 'insert into member_log(member_id,uuid,flg) value("%s","%s",%d)' % (member_id,_uuid,0)
    return

# 风险预警、告警日志
#
def warn_log():

    _uuid = create_UUID()

    return

# 特权日志
#
def pri_log():

    _uuid = create_UUID()

    return

def create_UUID():
    return str(uuid.uuid4())

#
# Eof
#

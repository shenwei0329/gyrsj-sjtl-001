#encoding=UTF-8
#
#   2016.3.5 by shenwei @GuiYang
#   ==============================
#   贵州市人社局“数据铁笼”应用
#
#   运行系统：创造一个模拟的市人事局生态。这是一个实现有生命的实体的程序
#

__author__ = 'shenwei'

import utils
import datetime

_debug_level = 0

def _debug(lvl,info):
    if lvl >= _debug_level:
        print(">>>%s %s\t%s") % (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "INFO" if lvl==0 else "WARN" if lvl==1 else "ERROR",
            info
        )

class k_value(object):

    def __init__(self,name,value=0):
        self.name = name
        self.value = value
        super(k_value,self).__init__()

    def add(self,value):
        self.value += value

    def minus(self,value):
        if self.value>=value:
            self.value -= value
        else:
            _debug(1,"k_value minus invalid value[%d,%d]" % (self.value,value))

    def get(self):
        return self.value

    def set(self,value):
        if value>=0:
            self.value = value
        else:
            _debug(1,"k_value set invalid value[%d]" % value)

class k_db(object):
    """
    数据库操作类
    """

    def __init__(self,metadata,values=None,writeable=False,create=False,hasid=False):

        self.table = metadata['table']
        self.id = metadata['id']
        self.field = metadata['field']

        self.writeable = writeable
        self.sql = ""
        if create:
            self._create(values,hasid=hasid)
        super(k_db,self).__init__()

    def _create(self,values,hasid=False):
        _field = ""
        _i = 0
        for f in self.field:
            if _i == 0:
                _field = f
                _i = 1
            else:
                _field += ",%s" % f

        _value = ""
        _i = 0
        for v in values:
            if _i == 0:
                _value = "%d" % v if type(v) is int else '"%s"' % v
                _i = 1
            else:
                _value += ",%d" % v if type(v) is int else ',"%s"' % v

        self.sql = "insert into %s(%s) values(%s)" % (self.table,_field,_value)
        _debug(1,self.sql)
        self.id = self.db_insert(hasid=hasid)
        _debug(1,"k_object _get insert it[%s]" % self.id)

    def db_update(self,field,data):
        if self.writeable:
            _cur = utils.mysql_conn()
            self.sql = 'update %s set %s=%s where id=%s' % \
                       (self.table,
                        field,'%d' % data if type(data) is int else '"%s"' % data,
                        str(self.id))
            _cur.execute(self.sql)
            _cur.close()

            _debug(0,"k_object db_update [%s]" % self.sql)
        else:
            _debug(1,"k_object db_update [%s] be not writeable" % self.sql)

    def db_select(self):
        _cur = utils.mysql_conn()
        _cnt = _cur.execute(self.sql)
        _entry = []
        if _cnt>0:
            for _ in range(_cnt):
                one = _cur.fetchone()
                _entry.append(one)
        _cur.close()
        _debug(0,"k_object db_select [%s]" % self.sql)
        return _entry

    def db_insert(self,hasid=False):
        _id = None
        if self.writeable:
            _cur = utils.mysql_conn()
            _cur.execute(self.sql)
            if not hasid:
                _id = int(_cur.lastrowid)
            else:
                _id = self.id
            _cur.close()
            _debug(1,"k_object db_insert [%s]" % self.sql)
        return _id

class k_db_scan(object):
    """
    数据库操 扫描处理 类
    """

    def __init__(self,metadata,scan_hdr):
        """
        :parameter
            metadata: 元数据
            scan_hdr: 处理扫描记录的方法
        """
        self.table = metadata['table']
        self.field = metadata['field']

        _field = ""
        _i = 0
        for f in self.field:
            if _i == 0:
                _field = f
                _i = 1
            else:
                _field += ",%s" % f

        self.sql = "select %s from %s" % (_field,self.table)
        self.scan_hdr = scan_hdr
        super(k_db_scan,self).__init__()

    def scan(self,where=None):
        _cur = utils.mysql_conn()
        if where is not None:
            _sql = self.sql + " where " + where
        else:
            _sql = self.sql

        _debug(0,"k_db_scan scan[%s]" % _sql)

        _cnt = _cur.execute(_sql)
        if _cnt>0:
            for _ in range(_cnt):
                one = _cur.fetchone()
                self.scan_hdr(one)
        _cur.close()
        _debug(0,"k_db_scan [%s]" % _sql)

class k_object(k_db):
    """
    对象基础类
    """

    def __init__(self,metadata,values=None,writeable=False,create=False,hasid=False):
        """
        :parameter
            metadata:元数据
                { 'table':表名，'id':标识，'field':[,]域名 }
            values:初始值
            writeable:允许修改数据库表项
            create:初始化数据库表项
        """
        super(k_object,self).__init__(metadata,values=values,writeable=writeable,create=create,hasid=hasid)
        _debug(0,"k_object created [%s,%s]" % (str(metadata),str(writeable)))

    def set(self,field,data):
        """
        指定值域赋值
        """
        if field in self.field:
            self.db_update(field,data)
            return
        _debug(1,"k_object set invalid field[%s,%s]" % (field,str(self.field)))

    def get(self,field):
        """
        获取指定值域的值
        """
        if field in self.field:
            if type(self.id) is int:
                self.sql = 'select %s from %s where id=%s' % (field,self.table,str(self.id))
            else:
                self.sql = 'select %s from %s where id="%s"' % (field,self.table,str(self.id))
            _rec = self.db_select()
            if len(_rec)>0:
                return _rec[0][0]
            else:
                return None
        _debug(1,"k_object get invalid field[%s,%s]" % (field,str(self.field)))

    def get_all(self):
        """
        获取所有域值
        """
        _str = ""
        _i = 0
        for _f in self.field:
            if _i==0:
                _str = _f
                _i = 1
            else:
                _str += ",%s" % _f
        self.sql = 'select %s from %s where id=%s' % (_str,self.table,str(self.id))
        return self.db_select()[0]

    def get_id(self):
        """
        获取对象的标识
        """
        return self.id

class c_record(k_db):
    """
    记录类
    """

    def __init__(self,metadata,values=None,writeable=False,create=False):
        """
        :parameter
            metadata:元数据
                { 'table':表名，'id':标识，'field':[,]域名 }
                注：记录类的id无实际意义，因为记录是流水日志
            values:初始值
            writeable:允许修改数据库表项
            create:初始化数据库表项
        """
        super(c_record,self).__init__(metadata,values=values,writeable=writeable,create=create)
        _debug(0,"c_recode __init__ %s" % metadata)

    def insert(self,values):
        """
        添加一条记录
        :parameter
            values:记录数据
        """
        _field = ""
        _i = 0
        for f in self.field:
            if _i == 0:
                _field = f
                _i = 1
            else:
                _field += ",%s" % f

        _value = ""
        _i = 0
        for v in values:
            if _i == 0:
                _value = "%d" % v if type(v) is int else '"%s"' % v
                _i = 1
            else:
                _value += ",%d" % v if type(v) is int else ',"%s"' % v

        self.sql = "insert into %s(%s) values(%s)" % (self.table,_field,_value)
        _debug(0,self.sql)
        self.db_insert(hasid=True)
        _debug(0,"c_record insert [%s]" % str(values))

    def search(self,where):
        """
        搜索满足条件的记录
        :parameter
            where:搜索条件（字符串）
        :returns
            满足条件的记录组
        """
        _field = ""
        _i = 0
        for f in self.field:
            if _i == 0:
                _field = f
                _i = 1
            else:
                _field += ",%s" % f
        self.sql = 'select %s from %s where %s' % (_field,self.table,where)
        return self.db_select()

class c_scope(k_object):
    """
    趋势类
    """

    def __init__(self,id=0,values=None,writeable=False,create=False):
        self._metadata = {
            'table':'scope',
            'id':id,
            'field':[
                'id','name'
                ,'m1_min','m2_min','m3_min','m4_min','m5_min','m6_min','m7_min','m8_min','m9_min','m10_min','m11_min','m12_min'
                ,'m1_avg','m2_avg','m3_avg','m4_avg','m5_avg','m6_avg','m7_avg','m8_avg','m9_avg','m10_avg','m11_avg','m12_avg'
                ,'m1_max','m2_max','m3_max','m4_max','m5_max','m6_max','m7_max','m8_max','m9_max','m10_max','m11_max','m12_max'
            ]
        }
        super(c_scope,self).__init__(self._metadata,values=values,writeable=writeable,create=create)

class c_quota(k_object):
    """
    计量类
    """

    def __init__(self,id=0,values=None,writeable=False,create=False):
        self._metadata = {'table':'quota','id':id,'field':['pid','name','mass','trend']}
        super(c_quota,self).__init__(self._metadata,values=values,writeable=writeable,create=create)

        if create:
            _v = [
                self.get_id()
                ,self.get('name')
                ,0,0,0,0,0,0,0,0,0,0,0,0
                ,0,0,0,0,0,0,0,0,0,0,0,0
                ,0,0,0,0,0,0,0,0,0,0,0,0
            ]
        else:
            _v = None
        # 获取与其相关联的趋势对象
        self.scope = c_scope(self.get_id(),values=_v,writeable=writeable,create=create)

    def add(self,value):
        _v = int(self.get('mass')) + int(value)
        self.set('mass',_v)
        return _v

    def setScope(self,index,type,value):
        if index in range(1,13) and type in ['min','avg','max']:
            _field = "m%d_%s" % (index,type)
            self.scope.set(_field,int(value))
        else:
            _debug(1,'c_quota setScope invalid[%d,%s,%d]' % (index,type,int(value)))

    def setAllScope(self,index,value):
        if index in range(1,13):
            _field = "m%d_min" % index
            self.scope.set(_field,int(value))
            _field = "m%d_avg" % index
            self.scope.set(_field,int(value))
            _field = "m%d_max" % index
            self.scope.set(_field,int(value))
        else:
            _debug(1,'c_quota setScope invalid[%d,%s,%d]' % (index,type,int(value)))

class c_member(k_object):
    """
    人员类
    """

    def __init__(self,id="",values=None,writeable=False,create=False,hasid=False):
        self._metadata = {
            'table':'member',
            'id':id,
             'field':[
                'id','name','cid','tel','credit_quota_id','load_quota_id','eff_quota_id','risk_quota_id'
                ]
            }
        if create:
            self.credit_quota = c_quota(values=[0,'个人信用评估',0,0],writeable=True,create=True)
            self.load_quota = c_quota(values=[self.credit_quota.get_id(),'工作量指标',0,0],writeable=True,create=True)
            self.eff_quota = c_quota(values=[self.credit_quota.get_id(),'效率指标',0,0],writeable=True,create=True)
            self.risk_quota = c_quota(values=[self.credit_quota.get_id(),'风险指标',0,0],writeable=True,create=True)
            values.append(self.credit_quota.get_id())
            values.append(self.load_quota.get_id())
            values.append(self.eff_quota.get_id())
            values.append(self.risk_quota.get_id())
        super(c_member,self).__init__(self._metadata,values=values,writeable=writeable,create=create,hasid=hasid)
        if not create:
            self.credit_quota = c_quota(id=self.get('credit_quota_id'),writeable=True)
            self.load_quota = c_quota(id=self.get('load_quota_id'),writeable=True)
            self.eff_quota = c_quota(id=self.get('eff_quota_id'),writeable=True)
            self.risk_quota = c_quota(id=self.get('risk_quota_id'),writeable=True)
        self._affair_rec_metadata = {'table':'affair_rec',
                                     'id':self.get_id(),
                                     'field':[
                                        'member_id'
                                        ,'start_date'
                                        ,'end_date'
                                        ,'subject'
                                        ,'sn'
                                        ,'node'
                                        ,'take'
                                        ,'comment'
                                     ]}
        self.affair_rec = c_record(self._affair_rec_metadata,writeable=True)

    def addAffair(self,affair):
        """
        处理本人的事务
        :param affair: 事务记录
            {'create_date':,'sn':,'subject':,'node':,'start_time':,'end_time':,''}
        :return:
        """
        # 从 affair 中解析出需要的参数，如月份、耗时、环节、评语、流水号、主题、时间戳...
        _index = 1  # 月份
        _load = 1   # 难度系数
        _v = self.load_quota.add(_load)
        self.load_quota.setAllScope(_index,_v)
        _max = 100
        _avg = 50
        _min = 20
        self.eff_quota.set('mass',_v)
        self.eff_quota.setScope(_index,"max",_max)
        self.eff_quota.setScope(_index,"avg",_avg)
        self.eff_quota.setScope(_index,"min",_min)
        self.risk_quota.set('mass',_v)
        self.risk_quota.setScope(_index,"max",_max) # 风险数
        self.risk_quota.setScope(_index,"avg",_avg) # 三级预警数
        self.risk_quota.setScope(_index,"min",_min) # 三级以下预警数
        # 增加 affair_rec 记录
        _rec = [self.get_id(),'2016-03-08 00:00:00','2016-03-08 00:00:00','测试记录-%s' % affair,'TST001','初审',5,'不符合要求']
        self.affair_rec.insert(_rec)

    def addAlarm(self,alarm):
        """
        处理本人的预警事件
        :param alarm: 预警记录
            {}
        :return:
        """
        pass

    def addRisk(self,risk):
        """
        处理本人的风险事故
        :param risk: 风险记录
            {}
        :return:
        """
        pass

class c_org(k_object):

    def __init__(self,id=0,values=None,writeable=False,create=False):
        self._metadata = {
            'table':'org',
            'id':id,
             'field':[
                'org_code','name','addr','sphere','legalperson_id','credit_quota_id','declare_quota_id',
                 'annual_quota_id','case_quota_id','social_quota_id'
                ]
            }
        if create:
            self.credit_quota = c_quota(values=[0,'机构信用评估',0,0],writeable=True,create=True)
            self.declare_quota = c_quota(values=[self.credit_quota.get_id(),'申办指标',0,0],writeable=True,create=True)
            self.annual_quota = c_quota(values=[self.credit_quota.get_id(),'年审指标',0,0],writeable=True,create=True)
            self.case_quota = c_quota(values=[self.credit_quota.get_id(),'案件指标',0,0],writeable=True,create=True)
            self.social_quota = c_quota(values=[self.credit_quota.get_id(),'社保指标',0,0],writeable=True,create=True)
            values.append(self.credit_quota.get_id())
            values.append(self.declare_quota.get_id())
            values.append(self.annual_quota.get_id())
            values.append(self.case_quota.get_id())
            values.append(self.social_quota.get_id())
        super(c_org,self).__init__(self._metadata,values=values,writeable=writeable,create=create)
        if not create:
            self.credit_quota = c_quota(id=self.get('credit_quota_id'),writeable=True)
            self.declare_quota = c_quota(id=self.get('declare_quota_id'),writeable=True)
            self.annual_quota = c_quota(id=self.get('annual_quota_id'),writeable=True)
            self.case_quota = c_quota(id=self.get('case_quota_id'),writeable=True)
            self.social_quota = c_quota(id=self.get('social_quota_id'),writeable=True)

class c_legalperson(k_object):

    def __init__(self,id=0,values=None,writeable=False,create=False):
        self._metadata = {
            'table':'legal_person',
            'id':id,
             'field':[
                'name','cid','tel','credit_quota_id','declare_quota_id','social_quota_id'
                ]
            }
        if create:
            self.credit_quota = c_quota(values=[0,'法人信用评估',0,0],writeable=True,create=True)
            self.declare_quota = c_quota(values=[self.credit_quota.get_id(),'申办指标',0,0],writeable=True,create=True)
            self.social_quota = c_quota(values=[self.credit_quota.get_id(),'社保指标',0,0],writeable=True,create=True)
            values.append(self.credit_quota.get_id())
            values.append(self.declare_quota.get_id())
            values.append(self.social_quota.get_id())
        super(c_legalperson,self).__init__(self._metadata,values=values,writeable=writeable,create=create)
        if not create:
            self.credit_quota = c_quota(id=self.get('credit_quota_id'),writeable=True)
            self.declare_quota = c_quota(id=self.get('declare_quota_id'),writeable=True)
            self.social_quota = c_quota(id=self.get('social_quota_id'),writeable=True)

class System():

    def __init__(self):
        self.org_name = '贵阳市人力资源和社会保障局'
        self.app_name = '数据铁笼'
        self.scan_affair = k_db_scan()
        self.scan_affair_alarm = k_db_scan()

    def _sleep(self):
        pass

    def hasAffair(self):
        """
        判断是否有新的事务
            若有，则：
                1）
        :return:
        """
        pass

    def hasAlarm(self):
        """
        判断是否需要发送预警！
            若发现 预警：
                1）查看 message_rec 中是否已经存在 该预警记录，sn、member和level相同
                2）若不存在，则发送消息，修改计量 risk_quota 下 scope 的min（1级）和avg（1级以上）
        :return:
        """
        pass

    def hasRisk(self):
        """
        判断是否需要发送风险事件！
            若发现 风险：
                1）查看 message_rec 中是否已经存在 该预警记录，sn、member和level相同
                2）若不存在，则发送消息，修改计量 risk_quota 下 scope 的max
        :return:
        """
        pass

    def run(self):
        """
        处理机：一个运行的进程实体
            while Ture:

                if hasAffair():
                    判读是否有 新的事务 要处理
                if hasAlarm():
                    判读是否有 新的预警事件 要处理
                if hasRisk():
                    判断是否有 新的风险事故 要处理

                self._sleep()

        :return:
        """
        pass

def my_scan_hdr(one):
    affair_trace = c_record({'table':'affair_trace','id':0,
                             'field':['affair_id','sn','node','state','start_time','end_time','member','subject','take','comment']},
                            writeable=True)
    if str(one[4])!='None' and str(one[5])!='None':
        _take = utils.cal_workdays(utils.mysql_conn(),str(one[4]),str(one[5]))
    else:
        _take = 0

    _node = str(one[2])
    if _node in ['collaboration','inform','vouch']:
        _node = '政务大厅'

    affair_trace.insert([str(one[0]),str(one[1]),_node,int(str(one[3])),
                         str(one[4]),str(one[5]),str(one[6]),str(one[7]),
                         _take,"-"])
    print("----------")
    for v in one:
        print("\t%s" % str(v))

def build_member():
    """
    从 org_member 表同步 member 个人信息
    注：缺失信息包括个人联系电话、身份证
    """
    cur = utils.mysql_conn()
    sql = 'select id,name from org_member'
    cnt = cur.execute(sql)
    if cnt>0:
        for _i in range(cnt):
            one = cur.fetchone()
            c_member(id=str(one[0]),values=[str(one[0]),str(one[1]),'-','-'],writeable=True,create=True,hasid=True)

if __name__ == '__main__':

    _sql = 'select a.member_id,b.yw_sn,a.node_policy,a.subject,a.COMPLETE_TIME from ctp_affair a,col_summary b ' \
           'where a.create_date=b.create_date and a.subject=b.subject and b.yw_sn!="NULL" ' \
           'and COMPLETE_TIME is NULL and b.state=0 and a.node_policy!="collaboration" ' \
           'order by a.receive_time;'

    # 初始化 member 对象数据
    # 2016-3-6 完成
    #build_member()

    scan = k_db_scan({'table':'ctp_affair a,col_summary b',
                      'field':['a.id','b.yw_sn','a.node_policy','b.state',
                               'a.receive_time','a.complete_time',
                               'a.member_id','a.subject']},my_scan_hdr)

    # 已完成事务
    where_0='a.create_date=b.create_date and a.subject=b.subject and b.yw_sn!="NULL" and b.state=3 and ' \
            'COMPLETE_TIME is not NULL order by a.receive_time'
    # 未完成事务
    where_1='a.create_date=b.create_date and a.subject=b.subject and b.yw_sn!="NULL" and COMPLETE_TIME is NULL ' \
          'and b.state=0 and a.node_policy!="collaboration" ' \
          'order by a.receive_time'
    # 扫描已完成事务
    scan.scan(where=where_0)
    # 扫描未完成事务
    scan.scan(where=where_1)

    """
    member = c_member(id="-10030045",values=['-10030045','shenwei','01234567890','13880575001'],writeable=True,create=True,hasid=True)
    legal = c_legalperson(values=['legal_person shenwei','01234567890','13880575001'],writeable=True,create=True)
    legal1 = c_legalperson(id=legal.get_id())
    org = c_org(values=['org_code','org_001','chengdu','sphere-None',legal.get_id()],writeable=True,create=True)
    org1 = c_org(id=org.get_id())
    affair_trace = c_record({'table':'affair_trace','id':0,
                             'field':['sn','node','state','start_time','end_time','member','subject','take','comment']},
                            writeable=True)
    affair_trace.insert(['sn-001','复审',3,'2016-03-06 12:00:00','2016-03-06 12:12:00',member.get_id(),'测试事务-001',12,'通过'])
    print str(affair_trace.search('member="shenwei"'))

    message_rec = c_record({'table':'message_rec','id':0,
                             'field':['start_date','end_date',
                                      'fr_member_id','to_member_id','sn','node','level','info','type','readed']},
                            writeable=True)
    message_rec.insert(['2016-03-06 12:00:00','2016-03-06 12:12:00',member.get_id(),member.get_id(),'sn-001','复审',1,'测试1级预警',1,0])
    print str(affair_trace.search('sn="sn-001"'))

    member.addAffair("member")
    print("member.id = %s" % member.get_id())
    member1 = c_member(id="-10030045",writeable=True)
    member1.addAffair("member1")
    """
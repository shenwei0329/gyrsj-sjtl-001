#encoding=UTF-8
#
#   2016.3.5 by shenwei @GuiYang
#   ==============================
#   贵州市人社局“数据铁笼”应用
#
#   运行系统：创造一个模拟的市人事局生态。这是一个实现有生命的实体的程序
#
#   待考虑事项：（注：在一期工程考虑）
#   1）引用 k-v 模式建立 对象的标量，实现动态、弹性关联
#

__author__ = 'shenwei'

import utils
import datetime,time,random

_debug_level = 10

def _debug(lvl,info):
    if lvl >= _debug_level:
        print(">>>%s %s\t%s") % (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "INFO" if lvl==0 else "WARN" if lvl==1 else "ERROR" if lvl==2 else "DEBUG",
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
        if create and values is not None:
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
                _value = '%d' % v if type(v) is int or type(v) is long else '"%s"' % v
                _i = 1
            else:
                _value += ",%d" % v if type(v) is int or type(v) is long else ',"%s"' % v

        self.sql = "insert into %s(%s) values(%s)" % (self.table,_field,_value)
        _debug(1,self.sql)
        self.id = self.db_insert(hasid=hasid)
        _debug(1,"k_object _get insert it[%s]" % self.id)

    def db_update(self,field,data):
        if self.writeable:
            _debug(0,"k_object db_update [%s]" % self.sql)
            try:
                _cur = utils.mysql_conn()
                self.sql = 'update %s set %s=%s where id=%s' % \
                           (self.table,
                            field,'%d' % data if type(data) is int or type(data) is long else '"%s"' % data,
                            str(self.id))

                _debug(5,"k_object db_update [%s]" % self.sql)

                _cur.execute(self.sql)
                _cur.close()
            except Exception as e:
                _debug(2,"k_object db_update error[%s]" % (e))
        else:
            _debug(1,"k_object db_update [%s] be not writeable" % self.sql)

    def db_select(self):
        _debug(3,"k_object db_select [%s]" % self.sql)
        _entry = []
        try:
            _cur = utils.mysql_conn()
            _cnt = _cur.execute(self.sql)
            if _cnt>0:
                for _ in range(_cnt):
                    one = _cur.fetchone()
                    _entry.append(one)
            _cur.close()
        except Exception as e:
            _debug(2,"k_object db_select error[%s]" % (e))
        finally:
            return _entry

    def db_insert(self,hasid=False):
        _id = None
        if self.writeable:
            _debug(1,"k_object db_insert [%s]" % self.sql)
            try:
                _cur = utils.mysql_conn()
                _cur.execute(self.sql)
                if not hasid:
                    _id = int(_cur.lastrowid)
                else:
                    _id = self.id
                _cur.close()
            except Exception as e:
                _debug(2,"k_object db_insert error[%s]" % (e))
            finally:
                return _id
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

    def scan(self,where=None,record=None,node=1,record_rec=None):
        _ret = []
        try:
            _cur = utils.mysql_conn()
            if where is not None:
                _sql = self.sql + " where " + where
            else:
                _sql = self.sql

            _cnt = _cur.execute(_sql)
            if _cnt>0:
                for _ in range(_cnt):
                    one = _cur.fetchone()
                    if record is not None:
                        _v = self.scan_hdr(one,record=record,node=node,record_rec=record_rec)
                    else:
                        _v = self.scan_hdr(one,node=node)
                    _ret.append(_v)
            _cur.close()
        except Exception as e:
            _debug(2,"k_db_scan scan error[%s]" % (e))
        finally:
            return _ret

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

            _debug(5,">>> k_object get self.id.type = %s" % type(self.id))
            if type(self.id) is int or type(self.id) is long:
                self.sql = 'select %s from %s where id=%s' % (field,self.table,str(self.id))
            else:
                self.sql = 'select %s from %s where id="%s"' % (field,self.table,str(self.id))
            _debug(5,">>> k_object get sql = %s" % self.sql)
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
        if type(self.id) is int or type(self.id) is long:
            self.sql = 'select %s from %s where id=%s' % (_str,self.table,str(self.id))
        else:
            self.sql = 'select %s from %s where id="%s"' % (_str,self.table,str(self.id))
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
                _value = "%d" % v if type(v) is int or type(v) is long else '"%s"' % v
                _i = 1
            else:
                _value += ",%d" % v if type(v) is int or type(v) is long else ',"%s"' % v

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
        super(c_scope,self).__init__(self._metadata,values=values,writeable=writeable,create=create,hasid=True)

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
            self.id = id
            _v = None
        # 获取与其相关联的趋势对象
        self.scope = c_scope(id=self.get_id(),values=_v,writeable=writeable,create=create)

    def add(self,value):
        _v = self.get('mass')
        if _v is not None:
            _v = int(_v) + int(value)
            self.set('mass',_v)
        return _v

    def addScope(self,index,type,value):
        if index in range(1,13) and type in ['min','avg','max']:
            _field = "m%d_%s" % (index,type)
            _value = int(self.scope.get(_field)) + 1
            self.scope.set(_field,_value)
        else:
            _debug(1,'c_quota setScope invalid[%d,%s,%d]' % (index,type,int(value)))

    def addAllScope(self,index,value):
        if index in range(1,13):
            self.addScope(index,'min',int(value))
            self.addScope(index,'avg',int(value))
            self.addScope(index,'max',int(value))
        else:
            _debug(1,'c_quota addAllScope invalid[%d,%d]' % (index,int(value)))

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
            self.credit_quota = c_quota(values=[0,'个人信用评估',80,0],writeable=True,create=True)
            self.load_quota = c_quota(values=[self.credit_quota.get_id(),'工作量指标',0,0],writeable=True,create=True)
            self.eff_quota = c_quota(values=[self.credit_quota.get_id(),'效率指标',0,0],writeable=True,create=True)
            self.risk_quota = c_quota(values=[self.credit_quota.get_id(),'风险指标',0,0],writeable=True,create=True)
            values.append(self.credit_quota.get_id())
            values.append(self.load_quota.get_id())
            values.append(self.eff_quota.get_id())
            values.append(self.risk_quota.get_id())
        super(c_member,self).__init__(self._metadata,values=values,writeable=writeable,create=create,hasid=hasid)
        if not create:
            self.credit_quota = c_quota(id=self.get('credit_quota_id'),writeable=True,)
            self.load_quota = c_quota(id=self.get('load_quota_id'),writeable=True)
            self.eff_quota = c_quota(id=self.get('eff_quota_id'),writeable=True)
            self.risk_quota = c_quota(id=self.get('risk_quota_id'),writeable=True)

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
            self.credit_quota = c_quota(values=[0,'机构信用评估',80,0],writeable=True,create=True)
            #
            # 申报指标 的趋势记录中 max=申报总数，avg=未批准总数，min=待定
            #
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
            self.credit_quota = c_quota(values=[0,'法人信用评估',80,0],writeable=True,create=True)
            self.declare_quota = c_quota(values=[self.credit_quota.get_id(),'申办指标',0,0],writeable=True,create=True)
            self.social_quota = c_quota(values=[self.credit_quota.get_id(),'社保指标',0,0],writeable=True,create=True)
            values.append(self.credit_quota.get_id())
            values.append(self.declare_quota.get_id())
            values.append(self.social_quota.get_id())
        super(c_legalperson,self).__init__(self._metadata,values=values,writeable=writeable,create=create)
        if not create:
            _id = self.get('credit_quota_id')
            _debug(3,">>> c_legalperson __init__ _id.type = %s" % type(_id))
            if _id is not None:
                _id = int(_id)
            self.credit_quota = c_quota(id=_id,writeable=True)
            self.declare_quota = c_quota(id=self.get('declare_quota_id'),writeable=True)
            self.social_quota = c_quota(id=self.get('social_quota_id'),writeable=True)

class c_affair_post(c_record):
    """
    定义 事务流水线的 环节
    """
    def __init__(self,id=None,values=None,writeable=False,create=False):
        _metadata = {
            'table':'affair_post',
            'id':id,
            'field':['line_id','name','t_limit']
        }
        super(c_affair_post,self).__init__(_metadata,values=values,writeable=writeable,create=create)

class c_affair_line(k_object):
    """
    定义 事务流水线（针对行政审批等业务）
    """
    def __init__(self,id=None,values=None,posts=None,writeable=False,create=False):
        _metadata = {
            'table':'affair_line',
            'id':id,
            'field':['name','sn','department','leader']
        }
        super(c_affair_line,self).__init__(_metadata,values=values,writeable=writeable,create=create)
        # 环节的 K-V
        self.post = {}
        if create:
            if posts is not None:
                for _post in posts:
                    _obj = c_affair_post(writeable=True)
                    _obj.insert(values=[self.get_id(),_post['name'],_post['value']])
                    self.post[_post['name']] = int(_post['value'])
        else:
            self.post = {}
            _obj = c_affair_post()
            _rec = _obj.search(where='line_id=%d' % self.get_id())
            for _r in _rec:
                self.post[str(_r[0])] = int(str(_r[1]))

    def get(self,field=None,where=None):
        if where is not None:
            if field is not None:
                self.sql = 'select %s from %s where %s' % (field,self.table,where)
            else:
                self.sql = 'select * from %s where %s' % (self.table,where)
        else:
            if field is not None:
                self.sql = 'select %s from %s' % (field,self.table)
            else:
                self.sql = 'select * from %s' % (self.table)
        return self.db_select()

    def getPost(self,post):
        return self.post[post]

def scan_one_hdr(one,record=None,node=1,record_rec=None):
    _ret = []
    for _o in one:
        _ret.append(str(_o))
    return _ret

class System(object):
    """
    系统定义【处理机】
    """
    def __init__(self):
        self.org_name = '贵阳市人力资源和社会保障局'
        self.app_name = '数据铁笼'
        # 创建一个 扫描类，其元数据的 源 指向一个 ctp_affair 和 col_summary 的联合
        # 属性：事务ID、业务流水号、环节、状态（0：待办中，3：完成）、接收时间、完成时间、待办人、主题
        self.affair_scan = k_db_scan({'table':'ctp_affair a,col_summary b',
                      'field':['a.id','b.yw_sn','a.node_policy','b.state',
                               'a.receive_time','a.complete_time','a.member_id','a.subject',
                               'b.id',
                               'b.org_code','b.org_name','b.org_addr','b.org_capital','b.org_reg_number','b.org_reg_addr',
                               'b.legal_person','b.legal_person_tel','b.legal_person_cid',
                               'b.create_date'
                               ]},my_scan_hdr)
        # 扫描 affair_rec，以统计 某月份的 min,avg,max
        self.affair_rec_scan = k_db_scan({'table':'affair_rec',
                      'field':['member','take']},scan_scope_hdr)
        # 创建一个 记录类，用于管理 affair_trace 记录
        self.affair_trace = c_record({'table':'affair_trace','id':0,
                                      'field':['affair_id','sn','node','state','start_time','end_time','member',
                                               'subject','org_code','take','comment']},
                                     writeable=True)
        # 创建一个 记录类，用于管理 affair_rec 记录
        self.affair_rec = c_record({'table':'affair_rec','id':0,
                                      'field':['sn','node','start_time','end_time','member',
                                               'subject','org_code','take','comment']},
                                     writeable=True)
        self.message_rec = c_record({'table':'message_rec','id':0,
                                     'field':['fr_member_id','to_member_id','sn','subject','node','level',
                                              'info','type','readed']},
                                    writeable=True)
        # 选择 已完成 事务
        self.where_0='a.create_date=b.create_date and a.subject=b.subject and b.yw_sn!="NULL" and b.state=3 and ' \
                     'a.COMPLETE_TIME is not NULL order by a.receive_time'
        # 选择 未完成 事务
        # 过滤掉 collaboration[协作] 发起环节
        self.where_1='a.create_date=b.create_date and a.subject=b.subject and b.yw_sn!="NULL" and COMPLETE_TIME is NULL ' \
                     'and b.state=0 and a.node_policy!="collaboration" ' \
                     'order by a.receive_time'
        # 筛选出 受理环节
        self.where_2='a.create_date=b.create_date and a.subject=b.subject and b.yw_sn!="NULL" and b.state=3 ' \
                     'and a.node_policy="collaboration"' \
                     'order by a.receive_time'
        self._exit = False
        super(System,self).__init__()
        #
        # 构建 事务处理线
        #
        # 事务处理线定义：
        #   {'id','name','sn','department','leader','post':[{post_name:post_t_limit}]}
        #
        self.affair_line = []
        _line = k_db_scan({'table':'affair_line','field':['id','name','sn','department','leader']},scan_one_hdr)
        _rec = _line.scan()
        for _r in _rec:
            _line_rec = {
                    'id':int(_r[0]),
                    'name':str(_r[1]),
                    'sn':str(_r[2]),
                    'department':str(_r[3]),
                    'leader':str(_r[4])
            }
            _post = k_db_scan({'table':'affair_post','field':['name','t_limit']},scan_one_hdr)
            _post_rec = _post.scan(where='line_id=%s' % _r[0])
            _post = {}
            for _p in _post_rec:
                _post[str(_p[0])] = int(_p[1])
            _line_rec['post'] = _post
            self.affair_line.append(_line_rec)
        # 测试通过，2016.3.8
        #_debug(5,">>> System __init__ affair_line[%s]" % str(self.affair_line))
        # 全局计量指标
        #
        _rec = c_record({'table':'quota','id':0,'field':['id','pid','name','mass','trend']})
        _r = _rec.search(where='pid=-1')
        if len(_r)==0:
            self.total_quota = c_quota(values=[-1,'全局指标评估',0,0],writeable=True,create=True)
            self.load_quota = c_quota(values=[self.total_quota.get_id(),'工作量指标',0,0],writeable=True,create=True)
            self.risk_quota = c_quota(values=[self.total_quota.get_id(),'风险指标',0,0],writeable=True,create=True)
            self.org_quota = c_quota(values=[self.total_quota.get_id(),'机构总数',0,0],writeable=True,create=True)
            self.legalperson_quota = c_quota(values=[self.total_quota.get_id(),'法人总数',0,0],writeable=True,create=True)
        else:
            _id = int(str(_r[0][0]))
            self.total_quota = c_quota(id=_id,writeable=True)
            self.total_quota.set('mass',98)
            _rr = _rec.search('pid=%s' % str(_id))
            for _rrr in _rr:
                if str(_rrr[2]) in ['工作量指标']:
                    self.load_quota = c_quota(id=int(str(_rrr[0])),writeable=True)
                elif str(_rrr[2]) in ['风险指标']:
                    self.risk_quota = c_quota(id=int(str(_rrr[0])),writeable=True)
                elif str(_rrr[2]) in ['机构总数']:
                    self.org_quota = c_quota(id=int(str(_rrr[0])),writeable=True)
                elif str(_rrr[2]) in ['法人总数']:
                    self.legalperson_quota = c_quota(id=int(str(_rrr[0])),writeable=True)
        #
        # 定义风险责任规则
        # 2016.3.9 - 针对 行政审批 业务
        self.RiskRule = {
                            'RLZY':{
                                2:['4876746049514849965'],
                                3:['4876746049514849965','-913621547074565894'],
                                4:['4876746049514849965','-913621547074565894','-7221668022947721994','7523849018428050552','1329013287631799142'],
                                5:['4876746049514849965','-913621547074565894','-7221668022947721994','7523849018428050552','1329013287631799142']},
                            'LWPQ':{
                                2:['1620419065382521819'],
                                3:['1620419065382521819','-7174564612394366732'],
                                4:['1620419065382521819','-7174564612394366732','-7221668022947721994','7523849018428050552','1329013287631799142'],
                                5:['1620419065382521819','-7174564612394366732','-7221668022947721994','7523849018428050552','1329013287631799142']},
                            'TSGS':{
                                2:['1620419065382521819'],
                                3:['1620419065382521819','-7174564612394366732'],
                                4:['1620419065382521819','-7174564612394366732','-7221668022947721994','7523849018428050552','1329013287631799142'],
                                5:['1620419065382521819','-7174564612394366732','-7221668022947721994','7523849018428050552','1329013287631799142']},
                            'JYZS':{
                                2:['-7561711767366450865'],
                                3:['-7561711767366450865','3449282702262554049'],
                                4:['-7561711767366450865','3449282702262554049','-7221668022947721994','7523849018428050552','1329013287631799142'],
                                5:['-7561711767366450865','3449282702262554049','-7221668022947721994','7523849018428050552','1329013287631799142']},
                            'MBZY':{
                                2:['309589157653594281'],
                                3:['309589157653594281','3449282702262554049'],
                                4:['309589157653594281','3449282702262554049','-7221668022947721994','7523849018428050552','1329013287631799142'],
                                5:['309589157653594281','3449282702262554049','-7221668022947721994','7523849018428050552','1329013287631799142']},
                            'JGXX':{
                                2:['309589157653594281'],
                                3:['309589157653594281','3449282702262554049'],
                                4:['309589157653594281','3449282702262554049','-7221668022947721994','7523849018428050552','1329013287631799142'],
                                5:['309589157653594281','3449282702262554049','-7221668022947721994','7523849018428050552','1329013287631799142']}
        }

    def _toMember(self,member,sn,level):
        if sn[0:4] in self.RiskRule:
            if level in self.RiskRule[sn[0:4]]:
                if str(member) in self.RiskRule[sn[0:4]][level]:
                    _idx = self.RiskRule[sn[0:4]][level].index(str(member))
                    #_debug(10,">>> _idx = %d" % _idx)
                    return self.RiskRule[sn[0:4]][level][_idx+1:]
                else:
                    return self.RiskRule[sn[0:4]][level]
        #_debug(10,">>> sn=[%s]" % sn)
        return []

    def _sleep(self):
        """
        循环周期：
            休眠 60 秒
        :return:
        """
        time.sleep(60)

    def _RiskHdr(self,evt_rec,type=0):
        """
        风险处理程序
        :param evt_rec: 事务记录
        :param type: =0 已完成事务，=1 未完成事件
        :return:
        """
        if type==0:
            # 已完成
            for _r in evt_rec:
                if _r.has_key('member') and _r.has_key('sn') and _r.has_key('node') and \
                        _r.has_key('take') and _r.has_key('subject'):
                    _debug(5,">>> System doChkRisk [%s,%s,%s,%s,%s]" % (
                        _r['member'],
                        _r['sn'],
                        _r['node'],
                        _r['take'],
                        _r['subject']
                    ))
                    _v = int(str(_r['take']))
                    # 是否办理过快！
                    _limit = self._get_post_limit(_r['sn'],_r['node']) * 15
                    # 当 _limit=0 时，表示该环节不存在 环节 时限
                    if _limit>0:
                        if _v < _limit:
                            _debug(5,">>> !!! RISK too fast! %s-%s-%s" % (str(_r['member']),str(_r['sn']),str(_r['node'])))
                            self.sendMessage(_r['member'],_r['member'],_r['sn'],_r['subject'],_r['node'],4,
                                             '风险事故：岗位在办理该事务时过快，无法保证审核质量。')
                # 处理审批未通过的事务
                _month = time.localtime().tm_mon
                if _r.has_key('org_code'):
                    _scan = k_db_scan({'table':'org','field':['id']},scan_one_hdr)
                    _rr = _scan.scan(where='org_code=%s' % _r['org_code'])
                    if len(_rr)>0:
                        _org = c_org(id=int(str(_rr[0][0])))
                        _org.declare_quota.addScope(_month,'avg',1)

                if _r.has_key('legal_person'):
                    _scan = k_db_scan({'table':'legal_person','field':['id']},scan_one_hdr)
                    _rr = _scan.scan(where='name=%s' % _r['legal_person'])
                    if len(_rr)>0:
                        _person = c_legalperson(id=int(str(_rr[0][0])))
                        _person.declare_quota.addScope(_month,'avg',1)
        else:
            # 未完成
            for _r in evt_rec:
                if len(_r)==6:
                    _debug(5,">>> System doChkRisk [%s,%s,%s,%s,%s,%s]" % (
                        _r['member'],
                        _r['sn'],
                        _r['node'],
                        _r['take'],
                        _r['subject'],
                        _r['create_date']
                    ))
                    # 计算总共 已用时
                    _v = utils.cal_workdays(_r['create_date'],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    # 是否超出 8 天总时限
                    if _v>3600:
                        _debug(5,">>> !!! RISK %s-%s-%s" % (str(_r['member']),str(_r['sn']),str(_r['node'])))
                        self.sendMessage(_r['member'],_r['member'],_r['sn'],_r['subject'],_r['node'],5,
                                         '风险事故：办理事务的总时限超期！')
                    elif _v>(3600-255):
                        _debug(5,">>> !!! ALARM 3 %s-%s-%s" % (str(_r['member']),str(_r['sn']),str(_r['node'])))
                        self.sendMessage(_r['member'],_r['member'],_r['sn'],_r['subject'],_r['node'],3,
                                         '风险预测预警：办理事务即将超期，请立刻办理！')
                    elif _v>(3600-450):
                        _debug(5,">>> !!! ALARM 2 %s-%s-%s" % (str(_r['member']),str(_r['sn']),str(_r['node'])))
                        self.sendMessage(_r['member'],_r['member'],_r['sn'],_r['subject'],_r['node'],2,
                                         '风险预测预警：办理事务即将超期，请尽快办理！')
                    elif _v>(3600-900):
                        _debug(5,">>> !!! ALARM 2 %s-%s-%s" % (str(_r['member']),str(_r['sn']),str(_r['node'])))
                        self.sendMessage(_r['member'],_r['member'],_r['sn'],_r['subject'],_r['node'],1,
                                         '风险预测预警：办理事务即将超期，请办理！')

                    _v = int(str(_r['take']))
                    _limit = self._get_post_limit(_r['sn'],_r['node']) * 450
                    _l1_limit = _limit/2
                    _l2_limit = _l1_limit + _l1_limit/3
                    _l3_limit = _l2_limit + _l1_limit/3
                    # 当 _limit=0 时，表示该环节不存在 环节 时限
                    if _limit>0:
                        if _v > _limit:
                            _debug(5,">>> !!! RISK %s-%s-%s" % (str(_r['member']),str(_r['sn']),str(_r['node'])))
                            self.sendMessage(_r['member'],_r['member'],_r['sn'],_r['subject'],_r['node'],4,
                                            '风险事故：办理事务的岗位时限超期！')
                        elif _v > _l3_limit:
                            _debug(5,">>> !!! ALARM 3 %s-%s-%s" % (str(_r['member']),str(_r['sn']),str(_r['node'])))
                            self.sendMessage(_r['member'],_r['member'],_r['sn'],_r['subject'],_r['node'],3,
                                            '风险预测预警：办理事务即将超期！，请立刻办理！')
                        elif _v > _l2_limit:
                            _debug(5,">>> !!! ALARM 2 %s-%s-%s" % (str(_r['member']),str(_r['sn']),str(_r['node'])))
                            self.sendMessage(_r['member'],_r['member'],_r['sn'],_r['subject'],_r['node'],2,
                                            '风险预测预警：办理事务即将超期！，请尽快办理')
                        elif _v > _l1_limit:
                            _debug(5,">>> !!! ALARM 1 %s-%s-%s" % (str(_r['member']),str(_r['sn']),str(_r['node'])))
                            self.sendMessage(_r['member'],_r['member'],_r['sn'],_r['subject'],_r['node'],1,
                                            '风险预测预警：办理事务即将超期！，请办理')

    def doChkAffair(self):
        """
        判断是否有新的事务
            若有，则：
                1）
        :return:
        """
        # 扫描受理环节事务
        _rec = self.affair_scan.scan(where=self.where_2,record=self.affair_trace,node=0,record_rec=self.affair_rec)
        # 扫描已完成事务
        _rec = self.affair_scan.scan(where=self.where_0,record=self.affair_trace,record_rec=self.affair_rec)
        self._RiskHdr(_rec)
        # 扫描未完成事务
        _rec = self.affair_scan.scan(where=self.where_1,record=self.affair_trace,record_rec=self.affair_rec)
        self._RiskHdr(_rec,type=1)

    def syncTotal(self):
        """
        计算 总指标
        :return:
        """
        # 扫描 人员的 工作量 和 风险 指标
        _scan = k_db_scan({'table':'member','field':['load_quota_id','risk_quota_id']},scan_one_hdr)
        _rec = _scan.scan()
        for _r in _rec:
            _load_q = c_quota(id=int(str(_r[0])))
            _risk_q = c_quota(id=int(str(_r[1])))
            self.load_quota.add(int(_load_q.get('mass')))
            self.risk_quota.add(int(_risk_q.get('mass')))
        # 扫描 机构的 工作量 和 风险 指标
        _scan = k_db_scan({'table':'org','field':['count(*)']},scan_one_hdr)
        _rec = _scan.scan()
        self.org_quota.set('mass',int(_rec[0][0]))
        # 扫描 机构的 工作量 和 风险 指标
        _scan = k_db_scan({'table':'legal_person','field':['count(*)']},scan_one_hdr)
        _rec = _scan.scan()
        self.legalperson_quota.set('mass',int(_rec[0][0]))

    def syncEff(self):
        """
        扫描 获取 人员的 趋势数据
        :return:
        """
        _month = time.localtime().tm_mon
        _rec = self.affair_rec_scan.scan(where='month(start_time)=%d' % _month) #time.localtime().tm_mon)
        self.calEff(_rec,_month)

    def calEff(self,_rec,_month):
        """
        计算并设置 人员的 趋势数据
        :param _rec: 人员表[]
        :param _month: 当前月份
        :return:
        """
        _member_cal = {}
        for _r in _rec:
            _debug(4,">>> _r[%s]" % str(_r))
            _member = _r['member']
            _val = _r['value']
            # 用 map/reduce 方式统计
            if _member in _member_cal:
                _min = _member_cal[_member][0]
                _max = _member_cal[_member][1]
                _member_cal[_member][2] += _val
                _member_cal[_member][3] += 1
                if _val < _min:
                    _member_cal[_member][0] = _val
                if _val > _max:
                    _member_cal[_member][1] = _val
            else:
                _member_cal[_member] = [_r['value'],_r['value'],_r['value'],1]

        for _k in _member_cal.keys():
            #
            # 计算 人员 效率趋向
            #
            _v = _member_cal[_k]
            _member = c_member(id=int(_k))
            _member.eff_quota.setScope(_month,'min',_v[0]*10)
            _member.eff_quota.setScope(_month,'max',_v[1]*10)
            _member.eff_quota.setScope(_month,'avg',(_v[2]*10)/_v[3])
            #
            # 计算 效率
            # 需要一个计算模型
            #
            _member.eff_quota.set('mass',(_v[2]*10)/_v[3])
            _member.eff_quota.set('trend',1)

    def _get_post_limit(self,sn,post):
        """
        获取 事务处理线 某环节的 时限
        :param name: 事务处理线名称
        :param post: 环节名称
        :return: 时限
        """
        _debug(5,">>> _get_post_limit %s[%s]" % (sn,post))

        for _r in self.affair_line:
            if str(_r['sn']) in str(sn):
                if post in _r['post']:
                    return int(str(_r['post'][str(post)]))
        return 0

    def sendMessage(self,fr_member,to_member,sn,subject,node,level,info):
        """
        发送风险类事件
        :param fr_member: 当事人
        :param to_member: 接收人
        :param sn: 事务标识
        :param subject: 事务主题
        :param node: 处理环节
        :param level: 等级，1，2，3预警，4，5风险事件
        :param info: 消息内容
        :return:
        """
        _scan = k_db_scan({'table':'message_rec','field':['count(*)']},scan_one_hdr)
        _rec = _scan.scan(where='fr_member_id="%s" and to_member_id="%s" and sn="%s" and node="%s" and level=%s' %
                         (str(fr_member),str(to_member),str(sn),str(node),str(level)))

        if int(str(_rec[0][0]))==0:
            self.message_rec.insert([fr_member,to_member,sn,subject,node,level,info,0,0])
            if level>1:
                # 把信息 按照风险责任规则定义 分发给相关人员
                _to_members = self._toMember(fr_member,sn,level)
                for _m in _to_members:
                    _scan = k_db_scan({'table':'message_rec','field':['count(*)']},scan_one_hdr)
                    _rec = _scan.scan(where='fr_member_id="%s" and to_member_id="%s" and sn="%s" and node="%s" and level=%s' %
                                     (str(fr_member),_m,str(sn),str(node),str(level)))
                    if int(str(_rec[0][0]))==0:
                        self.message_rec.insert([fr_member,_m,sn,subject,node,level,info,0,0])

            _member = c_member(id=str(fr_member))
            if level>3:
                _member.risk_quota.add(1)
            _month = time.localtime().tm_mon
            if level>3:
                _member.risk_quota.addScope(_month,'max',1)
            elif level>1:
                _member.risk_quota.addScope(_month,'avg',1)
            else:
                _member.risk_quota.addScope(_month,'min',1)

    def run(self):
        """
        处理机：一个运行的进程实体
        :return:
        """
        _5min = 5
        _hour = 60
        _day = 1440

        while not self._exit:

            self.doChkAffair()

            # 时间间隔 处理
            _5min -= 1
            if 0>=_5min:
                _5min = 5
                self.syncTotal()
            _hour -= 1
            if 0>=_hour:
                _hour = 60
                self.syncEff()
            _day -= 1
            if 0>= _day:
                _day = 1440
                sync_member()

            _debug(5,"System run _sleep()")
            self._sleep()

def scan_scope_hdr(one,record=None,node=1,record_rec=None):
    """
    处理针对 人员scope 的扫描，类似与 map 操作
    :param one: 记录数据
    :param record:
    :param node:
    :param record_rec:
    :return:
    """
    _debug(3,">>> scan_scope_hdr [%s]" % str(one))
    _member = str(one[0])
    _val = int(str(one[1]))
    return {'member':_member,'value':_val}

def my_scan_hdr(one,record=None,node=1,record_rec=None):
    """
    事务扫描过程处理器
    :param one:
        事务记录
        注：目前仅针对 OA 业务系统
    :return:
    """
    # one 元数据
    #
    # 'field':[
    #      0     1           2         3          4              5             6           7
    #    'id','yw_sn','node_policy','state','receive_time','complete_time','member_id','subject',
    #      8
    #    'summary_id'
    #      9               10          11             12              13                14
    #    'b.org_code','b.org_name','b.org_addr','b.org_capital','b.org_reg_number','b.org_reg_addr',
    #      15              16                  17                  18
    #    'legal_person','legal_person_tel','legal_person_cid','b.create_date
    #         ]
    _ret = {}

    # 判断是否是新记录
    _new = True
    if record is not None:
        _where = 'affair_id=%s' % str(one[0])
        _rec = record.search(_where)
        if len(_rec)>0:
            _new = False

    # 不是新记录，且已办理完成的，不需要考虑风险
    if (not _new) and (int(str(one[3]))>0):
        return _ret

    # 事务办理结束的月份
    # 01234567
    # xxxx-mm-dd hh:mm:ss
    #
    _month = time.localtime().tm_mon
    _str = str(one[5])
    if len(_str)>7 and '-' in _str and ':' in _str:
        _m_str = str(one[5])[5:7]
        _debug(10,'>>> _m_str = %s:%s' % (str(one[5]),_m_str))
        if _m_str.isdigit():
            _month = int(_m_str)
    _debug(10,'>>> _month = %d' % _month)

    _start_time = str(one[4])
    _end_time = str(one[5])

    # 清洗 环节node 数据
    # 清洗 OA的ctp_affair记录数据，统一流程环节名词
    _node = str(one[2])
    if _node in ['collaboration','vouch']:
        if node==0:
            # 表示为 受理环节
            #
            _node = '受理'
            _end_time = _start_time
            # 获取该申请的受理时间
            _cur = utils.mysql_conn()
            _time = utils.get_summary_feild_value(_cur,str(one[8]),"受理时间")
            _cur.close()
            _debug(0,">>> _time = %s" % str(_time))
            if _time is not None and _time not in ["None","NONE","NULL","Null",""] and ":" in _time and "-" in _time:
                _start_time = _time
        else:
            _node = '政务大厅'
    if _node in ['inform']:
        _node = '办结'
    if _node in ['领导审批意见']:
        _node = '审批'
    if _node in ['现场审查']:
        _node = '现场'

    # 清洗 OA的col_summary记录中的 机构代码
    _org_code = str(one[9])
    if _org_code in ['None','NONE','NULL','Null',""]:
        _org_code = "测试-机构代码"
    # 清洗 OA的col_summary记录中的 法人名称
    _person_name = str(one[15])
    if _person_name in ['None','NONE','NULL','Null',""]:
        _person_name = "测试-法人"

    if _node is '受理' and _new:

        _debug(3,">>> _person_name = %s" % _person_name)

        # 创建 obj 和 legal_person 对象
        #
        # 创建 legal_person 对象
        _person = c_legalperson()
        _person.sql = 'select id from %s where name="%s"' % (_person.table,_person_name)
        _id = _person.db_select()
        if len(_id)>0:
            _id = int(str(_id[0][0]))

            _debug(3,">>> _id = %d" % _id )
            _person = c_legalperson(id=_id)
        else:
            _person = c_legalperson(values=[_person_name,str(one[17]),str(one[16])],writeable=True,create=True)

        _debug(3,">>> _person.id = %d" % _person.get_id())

        #
        # 计算 法人 申报指标
        #
        # 总量+1
        #
        _person.declare_quota.add(1)
        #
        # 当月总量+1
        _person.declare_quota.addScope(_month,'max',1)

        _org = c_org()
        _org.sql = 'select id from %s where org_code="%s"' % (_org.table,_org_code)
        _id = _org.db_select()
        if len(_id)>0:
            _id = str(_id[0][0])
            _org = c_org(id=int(_id))
        else:
            # 用 测试样本数据
            _org = c_org(values=[_org_code,'贵阳市“世海游”旅游公司','贵州省贵阳市云岩区市府街007号',
                                 '注册资金：%s^工商注册码：%s^工商注册地址：%s' % ('50万元','TST0001','贵州省贵阳市云岩区市府街007号'),
                                 _person.get_id()],writeable=True,create=True)
            """
            _org = c_org(values=[_org_code,str(one[10]),str(one[11]),
                                 '注册资金：%s^工商注册码：%s^工商注册地址：%s' % (str(one[12]),str(one[13]),str(one[14])),
                                 _person.get_id()],writeable=True,create=True)
            """
        #
        # 计算 机构 申报指标
        # 申报总量+1
        _org.declare_quota.add(1)
        #
        # 当月申报总量+1
        _org.declare_quota.addScope(_month,'max',1)

    # 针对一个已完成的 环节node，应该同时具有 接收时间 和 完成时间
    _take = 0
    if _start_time!='None' and _end_time!='None':
        # 计算这两个时间的间隔，此值就是该环节花费的时间
        _cur = utils.mysql_conn()
        _take = utils.cal_workdays(_cur,_start_time,_end_time)
        _cur.close()
        if _new:
            # 是 审批 完成？
            if '审批' in _node:
                try:
                    _oracle_conn = utils.oracle_conn()
                    _oracle = _oracle_conn.cursor()
                    _mysql = utils.mysql_conn()
                    _ctp_state = utils.get_summary_ctp_state(_oracle,_mysql,str(one[8]))
                    if _ctp_state is not None:
                        if "未通过" in _ctp_state:
                            _ret['org_code'] = _org_code
                            _ret['legal_person'] = _person_name
                            _debug(5,">>> my_scan_hdr ctp_state=未通过!")
                    _mysql.close()
                    _oracle.close()
                    _oracle_conn.close()
                except Exception as e:
                    _debug(2,"my_scan_hdr oracle hdr err[%s]" % e)

            # 判断是否 办理过程 过快
            _ret['member'] = str(one[6])
            _ret['sn'] = str(one[1])
            _ret['node'] = str(_node)
            _ret['take'] = _take
            _ret['subject'] = str(one[7])
            _ret['create_date'] = str(one[18])
    else:
        # 若只有一个时间，则表示该事务可能还停留在此 环节node 上
        # 当用于风险扫描时，应该看看是否有超时限的可能，现在距离 接收时间 的时间间隔？
        if int(str(one[3]))==0 and record is None:
            # 当前时间
            _now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _cur = utils.mysql_conn()
            _take = utils.cal_workdays(_cur,_start_time,_now)
            _cur.close()

            _ret['member'] = str(one[6])
            _ret['sn'] = str(one[1])
            _ret['node'] = str(_node)
            _ret['take'] = _take
            _ret['subject'] = str(one[7])
            _ret['create_date'] = str(one[18])

    # 判断(自动发起)的"受理"环节，此环节OA会出现两个相同的记录
    #
    _sn = str(one[1])
    # 对sn的数据清洗
    #
    if _node is '政务大厅':
        _sn = '-1'
    if _sn[0:5] not in ['RLZYF','LWPQX','TSGSG','JYZSP','MBZYP','JGXXC','JGXXS']:
        # 对无效的流水号，统一赋值为"-1"
        _sn = '-1'

    if _node in ['受理'] and '(' in str(one[7]) and '-' in str(one[7]) and ':' in str(one[7]):
        _sn = '-1'

    if _node in ['受理'] and '自动' in str(one[7]) and '补正' in str(one[7]):
        # 过滤掉 由OA自动为补正发起的 事务
        _rec = record.search(where='sn="%s" and node="受理" and subject="%s" and end_time="%s"' %
                                   (_sn,str(one[7]),_end_time))
        if len(_rec)>0:
            _sn = '-1'

    if (_sn is not '-1') and ('*' not in _sn):
        # 人员工作量计量
        _member = c_member(id=str(one[6]))

        _debug(0,">>> _member.id = %s" % _member.get_id())

        _member.load_quota.add(1)
        _member.eff_quota.setScope(_month,'min',1)
        _member.eff_quota.setScope(_month,'avg',1)
        _member.eff_quota.setScope(_month,'max',1)

    # 若不是新纪录 或 不需要记录，则可退出
    if not _new or record is None:
        return _ret

    # 记录该事务过程到 affair_trace 中
    record.insert([str(one[0]),_sn,_node,int(str(one[3])),
                         _start_time,_end_time,str(one[6]),
                         str(one[7]),str(one[9]),_take,"-"])
                         #str(one[7]).replace('(自动发起)','').replace('（补正）',''),_take,"-"])

    if record_rec is None:
        return _ret

    # 记录该事务过程到 affair_rec 中
    # 'field':['sn','node','start_time','end_time','member','subject','take','comment']
    record_rec.insert(
        [_sn,_node,_start_time,_end_time,str(one[6]),
         str(one[7]),str(one[9]),_take,"-"]
         #str(one[7]).replace('(自动发起)','').replace('（补正）',''),_take,"-"]
    )
    return _ret

def build_affair_line():
    """
    构建 系统的 事务处理线 数据模型

        注：只在系统初始化时运行 ！

    :return:
    """
    _rec = ['人力资源服务许可','RLZYFWXK','人力资源市场处','路林']
    _posts = [
        {'name':'受理','value':1},
        {'name':'初审','value':2},
        {'name':'复审','value':2},
        {'name':'审批','value':2},
        {'name':'制证','value':1},
        {'name':'办结','value':0},
    ]
    _obj = c_affair_line(values=_rec,posts=_posts,writeable=True,create=True)

    _rec = ['劳务派遣许可','LWPQXK','劳动关系处','卢祝新']
    _posts = [
        {'name':'受理','value':1},
        {'name':'初审','value':2},
        {'name':'复审','value':1},
        {'name':'现场','value':2},
        {'name':'审批','value':1},
        {'name':'制证','value':1},
        {'name':'办结','value':0},
    ]
    _obj = c_affair_line(values=_rec,posts=_posts,writeable=True,create=True)

    _rec = ['台湾、香港、澳门人员就业证办理就业','JYZSP','就业促进处','潘红霞']
    _posts = [
        {'name':'受理','value':1},
        {'name':'初审','value':2},
        {'name':'复审','value':1},
        {'name':'现场','value':2},
        {'name':'审批','value':1},
        {'name':'制证','value':1},
        {'name':'办结','value':0},
    ]
    _obj = c_affair_line(values=_rec,posts=_posts,writeable=True,create=True)

    _rec = ['特殊工时工作制','TSGSGZZ','劳动关系处','卢祝新']
    _posts = [
        {'name':'受理','value':1},
        {'name':'初审','value':2},
        {'name':'复审','value':2},
        {'name':'审批','value':2},
        {'name':'制证','value':1},
        {'name':'办结','value':0},
    ]
    _obj = c_affair_line(values=_rec,posts=_posts,writeable=True,create=True)

    _rec = ['贵阳市民办职业培训学校','MBZYPXXX','职业能力建设处','潘红霞']
    _posts = [
        {'name':'受理','value':1},
        {'name':'初审','value':2},
        {'name':'复审','value':1},
        {'name':'现场','value':2},
        {'name':'审批','value':1},
        {'name':'制证','value':1},
        {'name':'办结','value':0},
    ]
    _obj = c_affair_line(values=_rec,posts=_posts,writeable=True,create=True)

    _rec = ['技工学校筹设行政许可','JGXXCS','职业能力建设处','潘红霞']
    _posts = [
        {'name':'受理','value':1},
        {'name':'初审','value':2},
        {'name':'复审','value':1},
        {'name':'现场','value':2},
        {'name':'审批','value':1},
        {'name':'制证','value':1},
        {'name':'办结','value':0},
    ]
    _obj = c_affair_line(values=_rec,posts=_posts,writeable=True,create=True)

    _rec = ['技工学校设立行政许可','JGXXSL','职业能力建设处','潘红霞']
    _posts = [
        {'name':'受理','value':1},
        {'name':'初审','value':2},
        {'name':'复审','value':1},
        {'name':'现场','value':2},
        {'name':'审批','value':1},
        {'name':'制证','value':1},
        {'name':'办结','value':0},
    ]
    _obj = c_affair_line(values=_rec,posts=_posts,writeable=True,create=True)

def sync_member():
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
            #
            # 判断是否是 新增加的 人员
            #
            curr = utils.mysql_conn()
            cnt = curr.execute('select id from member where id=%s' % str(one[0]))
            curr.close()
            if cnt==0:
                # 新增 人员！
                c_member(id=str(one[0]),values=[str(one[0]),str(one[1]),'-','-'],writeable=True,create=True,hasid=True)
                _debug(4,">>> build_member %s" % str(one[1]))
    cur.close()

def g_samples():
    """
    生成 测试样本数据
    :return:
    """
    #
    # 随机产生 趋势数据
    _scan = k_db_scan(metadata={'table':'scope','field':['id']},scan_hdr=scan_one_hdr)
    _cur = utils.mysql_conn()
    _ids = _scan.scan()
    for _id in _ids:
        for _m in range(1,13):
            _min = random.uniform(10,500)
            _avg = _min + random.uniform(10,500)
            _max = _avg + random.uniform(10,500)
            _set_min = 'm%d_min = %d' % (_m,int(_min))
            _set_avg = 'm%d_avg = %d' % (_m,int(_avg))
            _set_max = 'm%d_max = %d' % (_m,int(_max))
            _sql = 'update scope set %s,%s,%s where id=%s' % (_set_min,_set_avg,_set_max,str(_id[0]))
            _cur.execute(_sql)

if __name__ == '__main__':

    # 生成 测试样本数据
    g_samples()

    # 同步 member 对象数据
    sync_member()

    # 创建 事务办理业务线
    # ！！！ 创建类 ！！！
    # 2016.3.8 完成
    #build_affair_line()

    system = System()
    system.run()

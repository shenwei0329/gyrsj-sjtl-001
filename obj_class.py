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

    def __init__(self,metadata,values=None,writeable=False,create=False):

        self.table = metadata['table']
        self.id = metadata['id']
        self.field = metadata['field']

        self.writeable = writeable
        self.sql = ""
        if create:
            self._create(values)
        super(k_db,self).__init__()

        _debug(0,"k_object created [%s,%s]" % (str(metadata),str(writeable)))

    def _create(self,values):
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
        self.id = self.db_insert()

        _debug(0,"k_object _get insert it[%s]" % self.id)

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

    def db_insert(self,hasid=True):
        _id = None
        if self.writeable:
            _cur = utils.mysql_conn()
            _cur.execute(self.sql)
            if hasid:
                _id = int(_cur.lastrowid)
            _cur.close()
            _debug(0,"k_object db_insert [%s]" % self.sql)
        return _id

class k_object(k_db):
    """
    对象基础类
    """

    def __init__(self,metadata,values=None,writeable=False,create=False):
        """
        :parameter
            metadata:元数据
                { 'table':表名，'id':标识，'field':[,]域名 }
            values:初始值
            writeable:允许修改数据库表项
            create:初始化数据库表项
        """
        super(k_object,self).__init__(metadata,values=values,writeable=writeable,create=create)
        _debug(0,"k_object created [%s,%s]" % (str(metadata),str(writeable)))

    def set(self,field,data):
        """
        指定值域赋值
        """
        _i = 0
        for _f in self.field:
            if _f is field:
                self.db_update(field,data)
                return
            _i += 1
        _debug(1,"k_object set invalid field[%s]" % field)

    def get(self,field):
        """
        获取指定值域的值
        """
        for _f in self.field:
            if _f is field:
                self.sql = 'select %s from %s where id=%s' % (field,self.table,str(self.id))
                return self.db_select()[0][0]
        _debug(1,"k_object get invalid field[%s]" % field)

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
        self.db_insert(hasid=False)
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

    def __init__(self,id=0,values=None,writeable=False,create=False):
        self._metadata = {
            'table':'member',
            'id':id,
             'field':[
                'name','cid','pic_filename','credit_quota_id','load_quota_id','eff_quota_id','risk_quota_id'
                ]
            }
        if create:
            self.credit_quota = c_quota(values=[self.get_id(),'个人信用评价',0,0],writeable=True,create=True)
            self.load_quota = c_quota(values=[self.credit_quota.get_id(),'工作量指标',0,0],writeable=True,create=True)
            self.eff_quota = c_quota(values=[self.credit_quota.get_id(),'效率指标',0,0],writeable=True,create=True)
            self.risk_quota = c_quota(values=[self.credit_quota.get_id(),'风险指标',0,0],writeable=True,create=True)
            values.append(self.credit_quota.get_id())
            values.append(self.load_quota.get_id())
            values.append(self.eff_quota.get_id())
            values.append(self.risk_quota.get_id())
        super(c_member,self).__init__(self._metadata,values=values,writeable=writeable,create=create)
        if not create:
            self.credit_quota = c_quota(id=self.get('credit_quota_id'))
            self.load_quota = c_quota(id=self.get('load_quota_id'))
            self.eff_quota = c_quota(id=self.get('eff_quota_id'))
            self.risk_quota = c_quota(id=self.get('risk_quota_id'))
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
        :param affair:
        :return:
        """
        # 从 affair 中解析出需要的参数，如月份、耗时、环节、评语、流水号、主题、时间戳...
        _index = 1  # 月份
        _load = 1   # 难度系数
        _v = self.load_quota.add(_load)
        self.load_quota.setAllScope(_index,_v)
        _max = 0
        _avg = 0
        _min = 0
        self.eff_quota.set('mass',_v)
        self.eff_quota.setScope(_index,"max",_max)
        self.eff_quota.setScope(_index,"avg",_avg)
        self.eff_quota.setScope(_index,"min",_min)
        self.risk_quota.set('mass',_v)
        self.risk_quota.setScope(_index,"max",_max) # 风险数
        self.risk_quota.setScope(_index,"avg",_avg) # 三级预警数
        self.risk_quota.setScope(_index,"min",_min) # 三级以下预警数
        # 增加 affair_rec 记录
        _rec = [1,'2016-03-08 00:00:00','2016-03-08 00:00:00','测试记录','TST001','初审',5,'不符合要求']
        self.affair_rec.insert(_rec)

    def addAlarm(self,alarm):
        """
        处理本人的预警事件
        :param alarm:
        :return:
        """
        pass

    def addRisk(self,risk):
        """
        处理本人的风险事故
        :param risk:
        :return:
        """
        pass

class c_affair(c_record):

    def __init__(self,info,writeable=False,read=False,create=False):
        """
        构建事务实体
        :param info:
         事务数据模型【表名、唯一标识、域值[]】
        :return:
        """
        self._metadata = [
            'subject','complexity','alarm1','alarm2','alarm3','risk','start_datetime',
            'end_datetime','state','node','result','mass'
            ]
        if not self._validate(info):
            self._error = True
        else:
            self._error = False
            super(c_affair,self).__init__(info,writeable=writeable,read=read,create=create)

    def _validate(self,info):
        _field = []
        for _f in info['field']:
            _field.append(_f['name'])
        if _field != self._metadata:
            _debug(1,"c_affair _validate not match [%s]" % _field)
            return False
        return True

    def save(self):
        return

    def load(self):
        return

class c_org(k_object):

    def __init__(self,info):
        super(c_org,self).__init__(info)

class c_legalperson(k_object):

    def __init__(self,info):
        super(c_legalperson,self).__init__(info)

if __name__ == '__main__':

    q1 = c_quota(values=[0,'shenwei',0,0],writeable=True,create=True)
    q2 = c_quota(values=[0,'liangwanrong',0,0],writeable=True,create=True)
    q3 = c_quota(id=q1.get_id())

    q1.set('mass',15)
    q2.set('mass',200)

    print q1.get('mass')
    print q2.get('mass')
    print q3.get('mass')

    print q1.get_all()
    print q2.get_all()
    print q3.get_all()

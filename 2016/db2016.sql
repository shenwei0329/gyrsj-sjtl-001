#encoding=UTF-8

-- 指标级别
create TABLE q_level (
  q_id INT NOT NULL,  -- 给对应指标进行定级
  -- 取值范围 [min,max)
  -- min <= V < max
  --
  min INT NOT NULL,
  max INT NOT NULL,
  level VARCHAR (16) NOT NULL
) default charset=utf8;

-- 对象-指标 映射表
-- 注：在 一期工程 考虑
create TABLE member_quota (
  key VARCHAR (24) NOT NULL COMMENT '键值'
  member VARCHAR (64) NOT NULL COMMENT '人员ID',
  quota int NOT NULL COMMENT '指标ID',
  PRIMARY KEY (key)
) default charset=utf8;

create TABLE org_quota (
  key VARCHAR (24) NOT NULL COMMENT '键值'
  org INT NOT NULL COMMENT '机构ID',
  quota int NOT NULL COMMENT '指标ID',
  PRIMARY KEY (key)
) default charset=utf8;

create TABLE legalperson_quota (
  key VARCHAR (24) NOT NULL COMMENT '键值'
  legalperson INT NOT NULL COMMENT '法人ID',
  quota int NOT NULL COMMENT '指标ID',
  PRIMARY KEY (key)
) default charset=utf8;

-- 指标
create TABLE quota (
  id INT NOT NULL AUTO_INCREMENT,
  pid INT NOT NULL COMMENT '=-1 代表 人社局 全局指标',
  name VARCHAR (80) NOT NULL,
  mass INT NOT NULL,
  trend INT NOT NULL COMMENT '1:up；0:normal；-1:down',
  PRIMARY KEY (id)
) default charset=utf8;

-- 趋势
create TABLE trend (
  q_id INT NOT NULL,
  name VARCHAR (80) NOT NULL,
  m1 INT NOT NULL,
  m2 INT NOT NULL,
  m3 INT NOT NULL,
  m4 INT NOT NULL,
  m5 INT NOT NULL,
  m6 INT NOT NULL,
  m7 INT NOT NULL,
  m8 INT NOT NULL,
  m9 INT NOT NULL,
  m10 INT NOT NULL,
  m11 INT NOT NULL,
  m12 INT NOT NULL,
  PRIMARY KEY (q_id)
) default charset=utf8;

-- 范围
create TABLE scope (
  id INT NOT NULL COMMENT 'quota的ID',
  name VARCHAR (80) NOT NULL,

  m1_min INT NOT NULL,
  m2_min INT NOT NULL,
  m3_min INT NOT NULL,
  m4_min INT NOT NULL,
  m5_min INT NOT NULL,
  m6_min INT NOT NULL,
  m7_min INT NOT NULL,
  m8_min INT NOT NULL,
  m9_min INT NOT NULL,
  m10_min INT NOT NULL,
  m11_min INT NOT NULL,
  m12_min INT NOT NULL,

  m1_avg INT NOT NULL,
  m2_avg INT NOT NULL,
  m3_avg INT NOT NULL,
  m4_avg INT NOT NULL,
  m5_avg INT NOT NULL,
  m6_avg INT NOT NULL,
  m7_avg INT NOT NULL,
  m8_avg INT NOT NULL,
  m9_avg INT NOT NULL,
  m10_avg INT NOT NULL,
  m11_avg INT NOT NULL,
  m12_avg INT NOT NULL,

  m1_max INT NOT NULL,
  m2_max INT NOT NULL,
  m3_max INT NOT NULL,
  m4_max INT NOT NULL,
  m5_max INT NOT NULL,
  m6_max INT NOT NULL,
  m7_max INT NOT NULL,
  m8_max INT NOT NULL,
  m9_max INT NOT NULL,
  m10_max INT NOT NULL,
  m11_max INT NOT NULL,
  m12_max INT NOT NULL,

  PRIMARY KEY (id)
) default charset=utf8;

-- 人员
create TABLE member (
  id VARCHAR (64) NOT NULL COMMENT '人员ID，与OA系统同步',
  name VARCHAR (24) NOT NULL COMMENT '姓名',
  cid VARCHAR (24) NOT NULL COMMENT '身份证',
  tel VARCHAR (24) COMMENT '联系电话',
  credit_quota_id INT NOT NULL COMMENT '个人信用评价',
  load_quota_id INT NOT NULL COMMENT '工作量',
  eff_quota_id INT NOT NULL COMMENT '效率',
  risk_quota_id INT NOT NULL COMMENT '风险',
  PRIMARY KEY (id)
) default charset=utf8;

-- 机构
create TABLE org (
  id INT NOT NULL AUTO_INCREMENT,
  org_code VARCHAR (255) NOT NULL COMMENT '机构代码',
  name VARCHAR (255) NOT NULL COMMENT '名称',
  addr VARCHAR (255) NOT NULL COMMENT '地址',
  sphere VARCHAR (255) NOT NULL COMMENT '业务范围',
  legalperson_id INT NOT NULL COMMENT '法人ID',
  credit_quota_id INT NOT NULL COMMENT '机构信用评价',
  declare_quota_id INT NOT NULL COMMENT '申报情况',
  annual_quota_id INT NOT NULL COMMENT '年审情况',
  case_quota_id INT NOT NULL COMMENT '案件情况',
  social_quota_id INT NOT NULL COMMENT '社保情况',
  PRIMARY KEY (id)
) default charset=utf8;

-- 法人
create TABLE legal_person (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR (24) NOT NULL COMMENT '姓名',
  cid VARCHAR (24) NOT NULL COMMENT '身份证',
  tel VARCHAR (24) COMMENT '联系电话',
  credit_quota_id INT NOT NULL COMMENT '法人信用评价',
  declare_quota_id INT NOT NULL COMMENT '申报情况',
  social_quota_id INT NOT NULL COMMENT '社保情况',
  PRIMARY KEY (id)
) default charset=utf8;

-- 针对人员的事务记录
create TABLE affair_rec (
  member VARCHAR (64) NOT NULL COMMENT '人员ID',
  start_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '起始时间',
  end_time datetime NOT NULL COMMENT '结束时间',
  subject VARCHAR (255) NOT NULL COMMENT '主题',
  org_code VARCHAR (80) NOT NULL COMMENT '机构代码',
  sn VARCHAR (80) NOT NULL COMMENT '业务流水标识，如流水号',
  node VARCHAR (80) NOT NULL COMMENT '业务环节',
  take INT NOT NULL COMMENT '耗时（分钟）',
  comment VARCHAR (255) NOT NULL COMMENT '办理时给出的评语'
) default charset=utf8;

-- 事务跟踪记录
create TABLE affair_trace (
  affair_id VARCHAR (64) NOT NULL COMMENT '事务ID，例如ctp_affair的ID',
  sn VARCHAR (80) NOT NULL COMMENT '业务标识，如流水号',
  node VARCHAR (80) NOT NULL COMMENT '环节',
  state INT NOT NULL COMMENT '本环节的状态，1：办理完成；0：正在办理',
  start_time datetime NOT NULL COMMENT '办理的起始时间',
  end_time datetime NOT NULL COMMENT '办理的结束时间',
  member VARCHAR (64) NOT NULL COMMENT '人员ID，注：当state=1时有效',
  subject VARCHAR (255) NOT NULL COMMENT '主题',
  org_code VARCHAR (80) NOT NULL COMMENT '机构代码',
  take INT NOT NULL COMMENT '耗时（分钟）',
  comment VARCHAR (255) NOT NULL COMMENT '办理时给出的评语',
  PRIMARY KEY (affair_id)
) default charset=utf8;

-- 对象与指标的关联表
create TABLE object_quota (
  type INT NOT NULL COMMENT '对象类型，0：人员；1：机构；2：法人',
  object_id INT NOT NULL COMMENT '对象ID',
  q_id INT NOT NULL COMMENT '指标ID'
) default charset=utf8;

-- 风险记录
create TABLE message_rec (
  id INT NOT NULL AUTO_INCREMENT,
  start_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '发起时间',
  end_date datetime COMMENT '标志readed=1时的时间',
  fr_member_id VARCHAR (64)NOT NULL COMMENT '发起人ID',
  to_member_id VARCHAR (64) NOT NULL COMMENT '接收人ID',
  sn VARCHAR (80) NOT NULL COMMENT '业务标识，如流水号',
  subject VARCHAR (255) NOT NULL COMMENT '主题',
  node VARCHAR (80) NOT NULL COMMENT '环节',
  level INT NOT NULL COMMENT '等级，预警：1,2,3；风险：4,5；信息：0',
  info VARCHAR (255) NOT NULL COMMENT '说明',
  type INT NOT NULL COMMENT '0：发起；1：回复；2：处治',
  readed INT NOT NULL COMMENT '0：未读；1：已读',
  PRIMARY KEY (id)
) default charset=utf8;

-- 事务办理业务线
create TABLE affair_line (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR (255) NOT NULL COMMENT '业务线名称',
  sn VARCHAR (80) NOT NULL COMMENT '业务标识，如流水号标识',
  department VARCHAR (255) NOT NULL COMMENT '办理部门名称',
  leader VARCHAR (255) NOT NULL COMMENT '分管领导',
  ti_limit INT DEFAULT 8 COMMENT '业务线总时限，缺省8天'
  PRIMARY KEY (id)
) default charset=utf8;

-- 业务线环节
create TABLE affair_post (
  id INT NOT NULL AUTO_INCREMENT COMMENT '用于排序',
  line_id INT NOT NULL COMMENT '事务办理业务线ID',
  line_name VARCHAR (255) NOT NULL COMMENT '事务办理业务线名称',
  name VARCHAR (255) NOT NULL COMMENT '环节名称',
  t_limit INT NOT NULL COMMENT '时限',
  PRIMARY KEY (line_id,name)
) default charset=utf8;

-- 与OA同步
CREATE TABLE ctp_affair (
  ID VARCHAR (64) NOT NULL COMMENT '用于唯一性标识',
  IS_COVER_TIME int(11) DEFAULT NULL,
  MEMBER_ID VARCHAR (64) DEFAULT NULL,
  SENDER_ID VARCHAR (64) DEFAULT NULL,
  SUBJECT VARCHAR (255) NOT NULL COMMENT '事务主题',
  APP int(11) DEFAULT NULL,
  OBJECT_ID VARCHAR (64) DEFAULT NULL,
  SUB_OBJECT_ID VARCHAR (64) DEFAULT NULL,
  STATE int(11) DEFAULT NULL,
  SUB_STATE int(11) DEFAULT NULL,
  HASTEN_TIMES int(11) DEFAULT NULL,
  REMIND_DATE VARCHAR (64) DEFAULT NULL,
  DEADLINE_DATE VARCHAR (64) DEFAULT NULL,
  CAN_DUE_REMIND int(11) DEFAULT NULL,
  CREATE_DATE datetime DEFAULT NULL,
  RECEIVE_TIME datetime DEFAULT NULL,
  COMPLETE_TIME datetime DEFAULT NULL,
  REMIND_INTERVAL int(11) DEFAULT NULL,
  IS_DELETE int(11) DEFAULT NULL,
  TRACK int(11) DEFAULT NULL,
  ARCHIVE_ID VARCHAR (64) DEFAULT NULL,
  ADDITION VARCHAR (255) DEFAULT NULL,
  EXT_PROPS VARCHAR (255) DEFAULT NULL,
  UPDATE_DATE datetime DEFAULT NULL,
  IS_FINISH int(11) DEFAULT NULL,
  BODY_TYPE varchar(255) DEFAULT NULL,
  IMPORTANT_LEVEL int(11) DEFAULT NULL,
  RESENT_TIME int(11) DEFAULT NULL,
  FORWARD_MEMBER varchar(255) DEFAULT NULL,
  IDENTIFIER varchar(255) DEFAULT NULL,
  TRANSACTOR_ID VARCHAR (64) DEFAULT NULL,
  NODE_POLICY varchar(255) DEFAULT NULL,
  ACTIVITY_ID VARCHAR (64) DEFAULT NULL,
  FORM_APP_ID VARCHAR (64) DEFAULT NULL,
  FORM_ID VARCHAR (64) DEFAULT NULL,
  FORM_OPERATION_ID VARCHAR (64) DEFAULT NULL,
  TEMPLETE_ID VARCHAR (64) DEFAULT NULL,
  FROM_ID VARCHAR (64) DEFAULT NULL,
  OVER_WORKTIME VARCHAR (64) DEFAULT NULL,
  RUN_WORKTIME VARCHAR (64) DEFAULT NULL,
  OVER_TIME VARCHAR (64) DEFAULT NULL,
  RUN_TIME VARCHAR (64) DEFAULT NULL,
  DEAL_TERM_TYPE int(11) DEFAULT NULL,
  DEAL_TERM_USERID VARCHAR (64) DEFAULT NULL,
  SUB_APP int(11) DEFAULT NULL,
  EXPECTED_PROCESS_TIME datetime DEFAULT NULL,
  ORG_ACCOUNT_ID VARCHAR (64) DEFAULT NULL,
  PROCESS_ID varchar(255) DEFAULT NULL,
  IS_PROCESS_OVER_TIME int(11) DEFAULT NULL,
  FORM_MULTI_OPERATION_ID text,
  BACK_FROM_ID VARCHAR (64) DEFAULT NULL,
  FORM_RELATIVE_STATIC_IDS varchar(255) DEFAULT NULL,
  FORM_RELATIVE_QUERY_IDS varchar(255) DEFAULT NULL
) DEFAULT CHARSET=utf8

-- 各个环节的各类风险的负责人
create TABLE post_offical (
  id INT NOT NULL AUTO_INCREMENT COMMENT '用于排序',
  line_name VARCHAR (255) NOT NULL COMMENT '事务办理业务线名称',
  risk_lvl INT NOT NULL COMMENT '风险级别',
  member_id VARCHAR (255) NOT NULL COMMENT '人员ID',
  PRIMARY KEY (line_name,risk_lvl,member_id)
) default charset=utf8;

-- 业绩考核项
create TABLE kpi_param (
  id INT NOT NULL AUTO_INCREMENT COMMENT '用于排序',
  name VARCHAR (255) NOT NULL COMMENT '项目名称'
  line_name INT NOT NULL COMMENT '事务办理业务线名称',
  power INT DEFAULT 100 COMMENT '权重',
  desc VARCHAR (255) COMMENT '说明',
  op VARCHAR (16) DEFAULT '1' COMMENT '加分：1，减分：-1',
  PRIMARY KEY (name,line_name)
) default charset=utf8;

-- 风险项
create TABLE risk_def (
  id INT NOT NULL AUTO_INCREMENT COMMENT '用于排序',
  name VARCHAR (255) NOT NULL COMMENT '项目名称',
  line_name INT NOT NULL COMMENT '事务办理业务线名称',
  threshold INT DEFAULT 100 COMMENT '阈值 1~100%',
  type VARCHAR (255) COMMENT '类型，预警：0；警告：9',
  lvl INT DEFAULT 1 COMMENT '级别，当type=0时，1，2，3；当type=9，1-内部，2-外部',
  group_name VARCHAR (255) NOT NULL COMMENT '通报组名称',
  PRIMARY KEY (name,line_name,type,lvl)
) default charset=utf8;

-- 通报组
create TABLE group_def (
  id INT NOT NULL AUTO_INCREMENT COMMENT '通报组号',
  name VARCHAR (255) NOT NULL COMMENT '项目名称',
  PRIMARY KEY (name)
) default charset=utf8;

-- 通报组组员
create TABLE group_def (
  group_id INT NOT NULL COMMENT '组号',
  member_id VARCHAR (255) NOT NULL COMMENT '项目名称',
  PRIMARY KEY (group_id,member_id)
) default charset=utf8;

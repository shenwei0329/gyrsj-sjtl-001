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

-- 指标
create TABLE quota (
  id INT NOT NULL AUTO_INCREMENT,
  pid INT NOT NULL,
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
  id INT NOT NULL AUTO_INCREMENT,
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
  PRIMARY KEY (id)
) default charset=utf8;

-- 法人
create TABLE legal_person (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR (24) NOT NULL COMMENT '姓名',
  cid VARCHAR (24) NOT NULL COMMENT '身份证',
  tel VARCHAR (24) COMMENT '联系电话',
  PRIMARY KEY (id)
) default charset=utf8;

-- 针对人员的事务记录
create TABLE affair_rec (
  member_id INT NOT NULL COMMENT '人员ID',
  start_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '起始时间',
  end_date datetime NOT NULL COMMENT '结束时间',
  subject VARCHAR (255) NOT NULL COMMENT '主题',
  sn VARCHAR (80) NOT NULL COMMENT '业务流水标识，如流水号',
  node VARCHAR (80) NOT NULL COMMENT '业务环节',
  take INT NOT NULL COMMENT '耗时（分钟）',
  comment VARCHAR (255) NOT NULL COMMENT '办理时给出的评语'
) default charset=utf8;

-- 事务跟踪记录
create TABLE affair_trace (
  sn VARCHAR (80) NOT NULL COMMENT '业务标识，如流水号',
  node VARCHAR (80) NOT NULL COMMENT '环节',
  state INT NOT NULL COMMENT '本环节的状态，1：办理完成；0：正在办理',
  start_time datetime NOT NULL COMMENT '办理的起始时间',
  end_time datetime NOT NULL COMMENT '办理的结束时间',
  member VARCHAR (80) NOT NULL COMMENT '人员名称，注：当state=1时有效',
  subject VARCHAR (255) NOT NULL COMMENT '主题',
  take INT NOT NULL COMMENT '耗时（分钟）',
  comment VARCHAR (255) NOT NULL COMMENT '办理时给出的评语'
) default charset=utf8;

-- 对象与指标的关联表
create TABLE object_quota (
  type INT NOT NULL COMMENT '对象类型，0：人员；1：机构；2：法人',
  object_id INT NOT NULL COMMENT '对象ID',
  q_id INT NOT NULL COMMENT '指标ID'
) default charset=utf8;

-- 风险记录
create TABLE message_rec (
  start_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '发起时间',
  end_date datetime COMMENT '标志readed=1时的时间',
  fr_member_id INT NOT NULL COMMENT '发起人ID',
  to_member_id INT NOT NULL COMMENT '接收人ID',
  sn VARCHAR (80) NOT NULL COMMENT '业务标识，如流水号',
  level INT NOT NULL COMMENT '等级，预警：1,2,3；风险：4,5；信息：0',
  info VARCHAR (255) NOT NULL COMMENT '说明',
  type INT NOT NULL COMMENT '0：发起；1：回复；2：处治',
  readed INT NOT NULL COMMENT '0：未读；1：已读'
) default charset=utf8;


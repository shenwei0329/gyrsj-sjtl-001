#encoding=UTF-8

create TABLE sys_info (
	name 	varchar(80) 		NOT NULL,
	value	varchar(255)		NOT NULL
) default charset=utf8;

insert  into sys_info(name,value) values ('oa_appserver_ip','10.169.8.112:9980');

create TABLE leader (
  line_id int,
  sn int,
  member bigint
) default charset=utf8;

-- 业务线、节点上的上级人员
-- 政务大厅 负责人：杨建
insert into leader(line_id,sn,member) values(1,0,"2605449744421242830");
-- 初审、办结环节 负责人：王安安
insert into leader(line_id,sn,member) values(1,1,"4876746049514849965");
insert into leader(line_id,sn,member) values(1,4,"4876746049514849965");
-- 复审环节 负责人：路林
insert into leader(line_id,sn,member) values(1,2,"-913621547074565894");

-- 政务大厅 负责人：杨建
insert into leader(line_id,sn,member) values(2,0,"2605449744421242830");
-- 初审、现场、办结环节 负责人：张文忠
insert into leader(line_id,sn,member) values(2,1,"1620419065382521819");
insert into leader(line_id,sn,member) values(2,3,"1620419065382521819");
insert into leader(line_id,sn,member) values(2,5,"1620419065382521819");
-- 复审环节 负责人：卢祝新
insert into leader(line_id,sn,member) values(2,2,"-7174564612394366732");

-- 纪检监察室
-- 纪检书记
insert into leader(line_id,sn,member) values(0,0,"1329013287631799142");
insert into leader(line_id,sn,member) values(0,0,"-7221668022947721994");
insert into leader(line_id,sn,member) values(0,0,"7523849018428050552");

CREATE TABLE form_file_info (
	form_def_id	bigint		NOT NULL,
	field		bigint		NOT NULL,
	field_name	varchar(255)	NOT NULL
) default charset=utf8;

create TABLE special_day (
  year int NOT NULL,
	month int NOT NULL,
	day int NOT NULL
) default charset=utf8;

create TABLE login_log (
  id bigint NOT NULL,
	member_id bigint NOT NULL,
	login datetime NOT NULL,
	logout datetime NOT NULL,
	ip varchar(20) NOT NULL
) default charset=utf8;

create TABLE requisition (
	id											bigint					NOT NULL,
	form_def_id						bigint					NOT NULL,
	name										varchar(255)		NOT NULL,
	form_appid							bigint					NOT NULL,
	form_recordid					bigint					NOT NULL,
	state										bigint					NOT NULL,
	ovre_time							bigint					NOT NULL,
	total_day							bigint					NOT NULL,
	post_day								bigint					NOT NULL,
	file_compliance_flag	varchar(255)		NOT NULL
) default charset=utf8;

-- 关联一个申请表中包含的附件
create TABLE file_desc (
  req_id  bigint  NOT NULL, -- 申请表col_summary.ID
  line_id int NOT NULL, -- 业务线ID
  form_id bigint  NOT NULL, -- 表单form_def.ID
  field_id int NOT NULL, -- 域index
  file_path varchar(255)  NOT NULL  -- 文件路径
) default charset=utf8;

create TABLE file_rule (
  id  int primary key not null auto_increment,
  line_id bigint  NOT NULL,
  form_def_id bigint  NOT NULL,
  field_id  int NOT NULL,
  field_name  varchar(255)  NOT NULL
) default charset=utf8;

create TABLE file_rule_keyv (
  file_rule_id  bigint  NOT NULL,
	rule  varchar(80) NOT NULL
) default charset=utf8;

create TABLE ctp_user_message (
 id bigint NOT NULL,
 sender_id bigint NOT NULL,
 message varchar(255) NOT NULL,
 create_date datetime NOT NULL,
 flg bigint NOT NULL,
 st int DEFAULT 0,
 summary_id bigint -- 与col_summary表关联申请单，以查询该申请单的轨迹记录
) default charset=utf8;

create TABLE ctp_user_history_message (
 id bigint NOT NULL,
 sender_id bigint NOT NULL,
  receiver_id bigint NOT NULL,
  message varchar(255) NOT NULL,
  create_date	datetime NOT NULL,
  flg bigint NOT NULL,
  summary_id bigint -- 与col_summary表关联申请单，以查询该申请单的轨迹记录
) default charset=utf8;

create TABLE col_user_message (
 id bigint NOT NULL,
 sender_id bigint NOT NULL,
  receiver_id bigint NOT NULL,
  message varchar(255) NOT NULL,
  create_date	datetime NOT NULL
) default charset=utf8;

-- 业务总表
create TABLE col_summary (
 ID bigint NOT NULL,
 STATE int NOT NULL,
 SUBJECT varchar(255) NOT NULL,
 DEADLINE int NOT NULL, -- 办理总期限，一般为8天，从line_def表
 RESENT_TIME	 datetime, -- 用于保存summary的受理时间，来自于主表的“受理时间”域
 CREATE_DATE datetime NOT NULL,
 START_DATE datetime NOT NULL, -- 当state=3时，该时间被用作 事后监督 时间点
 FINISH_DATE	 datetime, -- 用于计算 节点之间花费的时间（分钟）
 START_MEMBER_ID bigint NOT NULL,
 FORWARD_MEMBER bigint NOT NULL,
 FORM_RECORDID	 bigint NOT NULL,
 FORMID	 bigint NOT NULL,
 FORM_APPID bigint NOT NULL,
 ORG_DEPARTMENT_ID bigint NOT NULL,
 VOUCH int NOT NULL, -- 2015审批通过，2000未通过
 OVER_WORKTIME int,
 RUN_WORKTIME int,
 OVER_TIME int,
 RUN_TIME int,
 CURRENT_NODES_INFO bigint NOT NULL,
 cnt int, -- 剩余的天数，初始值来自post_deadline，每个工作日的00:00做减法，0表示超期
 line_id int, -- 业务线ID
 sn int, -- 当前的岗位序号
 yw_sn varchar(80), -- 申请单流水号
 pri int, -- 是否拥有优先办理特权，0:没有；1:有
 org_code varchar(80) COMMENT '机构代码'
 ,org_name varchar(255) COMMENT '机构名称'
 ,org_addr varchar(255) COMMENT '机构地址'
 ,org_capital varchar(80) COMMENT '注册资金'
 ,org_reg_number varchar(255) COMMENT '工商注册号'
 ,org_reg_addr varchar(255) COMMENT '工商注册地址'
 ,legal_person varchar(80) COMMENT '法人名称'
 ,legal_person_tel varchar(80) COMMENT '法人联系电话'
 ,legal_person_cid varchar(80) COMMENT '法人身份证'
) default charset=utf8;

-- 年度业绩统计
create TABLE year_total (
	line_id int,	-- 业务线
	post_id int,	-- 岗位序号
	id int,	-- 月份
	m int	-- 月份的业务累计
) default charset=utf8;

insert into year_total(line_id,id,m) values(1,0,0);
insert into year_total(line_id,id,m) values(1,1,0);
insert into year_total(line_id,id,m) values(1,2,0);
insert into year_total(line_id,id,m) values(1,3,0);
insert into year_total(line_id,id,m) values(1,4,0);
insert into year_total(line_id,id,m) values(1,5,0);
insert into year_total(line_id,id,m) values(1,6,0);
insert into year_total(line_id,id,m) values(1,7,0);
insert into year_total(line_id,id,m) values(1,8,0);
insert into year_total(line_id,id,m) values(1,9,0);
insert into year_total(line_id,id,m) values(1,10,0);
insert into year_total(line_id,id,m) values(1,11,0);
insert into year_total(line_id,id,m) values(1,12,0);

insert into year_total(line_id,id,m) values(2,0,0);
insert into year_total(line_id,id,m) values(2,1,0);
insert into year_total(line_id,id,m) values(2,2,0);
insert into year_total(line_id,id,m) values(2,3,0);
insert into year_total(line_id,id,m) values(2,4,0);
insert into year_total(line_id,id,m) values(2,5,0);
insert into year_total(line_id,id,m) values(2,6,0);
insert into year_total(line_id,id,m) values(2,7,0);
insert into year_total(line_id,id,m) values(2,8,0);
insert into year_total(line_id,id,m) values(2,9,0);
insert into year_total(line_id,id,m) values(2,10,0);
insert into year_total(line_id,id,m) values(2,11,0);
insert into year_total(line_id,id,m) values(2,12,0);

-- 业务线定义
create TABLE line_def (
  id int,
  name varchar(255) NOT NULL,
  form_def_id bigint NOT NULL,	-- 表单定义ID
  formmain_name varchar(80) NOT NULL,	-- 该业务线上主表单名称
  deadline int  -- 业务线办理总期限，一般为8个工作日
) default charset=utf8;

-- 定义业务线各个岗位的办理期限
create TABLE post_deadline (
  line_id int,
  post_sn int, -- 节点序号
  deadline int -- 期限（小时）
) default charset=utf8;

-- 定义每一个业务线节点（环节）的期限
insert into post_deadline(line_id,post_sn,deadline) values(1,0,1);
insert into post_deadline(line_id,post_sn,deadline) values(1,1,2);
insert into post_deadline(line_id,post_sn,deadline) values(1,2,1);
insert into post_deadline(line_id,post_sn,deadline) values(1,3,2);
insert into post_deadline(line_id,post_sn,deadline) values(1,4,2);

insert into post_deadline(line_id,post_sn,deadline) values(2,0,1);
insert into post_deadline(line_id,post_sn,deadline) values(2,1,2);
insert into post_deadline(line_id,post_sn,deadline) values(2,2,1);
insert into post_deadline(line_id,post_sn,deadline) values(2,3,2);
insert into post_deadline(line_id,post_sn,deadline) values(2,4,1);
insert into post_deadline(line_id,post_sn,deadline) values(2,5,1);

-- 岗位明细 2015-12-16
-- 因一个业务线的环节上可以有多人“竞争”办理
create table post_rec ( line_id int, unit_id bigint, post_id bigint, sn int) default charset=utf8;

-- 公勤人员
INSERT INTO post_rec VALUES ('1', '4114528878294287249', '8341470715773930046', '0');
-- 政务大厅窗口
INSERT INTO post_rec VALUES ('1', '4114528878294287249', '4355950963446468199', '0');
-- 人力资源市场处副主任科员
INSERT INTO post_rec VALUES ('1', '4809355253136572482', '-6142181662985010204', '1');
-- 人力资源市场处科员
INSERT INTO post_rec VALUES ('1', '4809355253136572482', '-6257008799918832760', '1');
-- 人力资源市场处处长
INSERT INTO post_rec VALUES ('1', '4809355253136572482', '-5273152026133969439', '2');
-- 机关党委书记、党委委员
INSERT INTO post_rec VALUES ('1', '5745107157522860074', '-1228241534544558833', '3');
-- 人力资源市场处副主任科员
INSERT INTO post_rec VALUES ('1', '4809355253136572482', '-6142181662985010204', '4');
-- 人力资源市场处科员
INSERT INTO post_rec VALUES ('1', '4809355253136572482', '-6257008799918832760', '4');
-- 公勤人员
INSERT INTO post_rec VALUES ('1', '4114528878294287249', '8341470715773930046', '4');
-- 政务大厅窗口
INSERT INTO post_rec VALUES ('1', '4114528878294287249', '4355950963446468199', '4');

-- 公勤人员
INSERT INTO post_rec VALUES ('2', '4114528878294287249', '8341470715773930046', '0');
-- 政务大厅窗口
INSERT INTO post_rec VALUES ('2', '4114528878294287249', '4355950963446468199', '0');
-- 劳动关系处科员
INSERT INTO post_rec VALUES ('2', '9116165337005639259', '-3878161648001595846', '1');
-- 劳动关系处处长
INSERT INTO post_rec VALUES ('2', '9116165337005639259', '1029063431013876529', '2');
-- 劳动关系处科员
INSERT INTO post_rec VALUES ('2', '9116165337005639259', '-3878161648001595846', '3');
-- 劳动关系处处长
INSERT INTO post_rec VALUES ('2', '9116165337005639259', '1029063431013876529', '3');
-- 副局长
INSERT INTO post_rec VALUES ('2', '5745107157522860074', '5650735151785788005', '4');
-- 劳动关系处科员
INSERT INTO post_rec VALUES ('2', '9116165337005639259', '-3878161648001595846', '5');
-- 公勤人员
INSERT INTO post_rec VALUES ('2', '4114528878294287249', '8341470715773930046', '5');
-- 政务大厅窗口
INSERT INTO post_rec VALUES ('2', '4114528878294287249', '4355950963446468199', '5');

-- 定义岗位
-- 将这个表中的line_id,unit_id,post_id,sn关联移到post_rec表
create TABLE post (
	id int primary key not null auto_increment,
  name varchar(255) NOT NULL,
  line_id	bigint,	-- 业务线
  unit_id bigint,	-- 部门
  post_id bigint,	-- 岗位
  sn int NOT NULL,	-- 岗位序号
  total int,	-- 岗位年度业绩累积
  curr int,	-- 岗位月份业绩累积
  wait_cnt int,	-- 等待处理的申请数
  do_cnt int,	-- 正在办理的申请数
  redo_cnt int,	-- 补正中的申请数
  delay_cnt int,	-- 延期的申请数
  warn_cnt int, -- 预警数
  alarm_cnt int -- 告警数
) default charset=utf8;

-- 注意：这些定义与UI显示相关，主要用于定义业务线和节点
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('受理',1,4114528878294287249,8341470715773930046,0,0,0,0,0,0,0,0,0);
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('初审',1,4809355253136572482,-6257008799918832760,1,0,0,0,0,0,0,0,0);
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('复审',1,4809355253136572482,-5273152026133969439,2,0,0,0,0,0,0,0,0);
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('审批',1,5745107157522860074,-1228241534544558833,3,0,0,0,0,0,0,0,0);
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('办结',1,4809355253136572482,-6257008799918832760,4,0,0,0,0,0,0,0,0);
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('事后监督',1,-1286680529020171829,8341470715773930046,5,0,0,0,0,0,0,0,0);

insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('受理',2,4114528878294287249,8341470715773930046,0,0,0,0,0,0,0,0,0);
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('初审',2,9116165337005639259,-3878161648001595846,1,0,0,0,0,0,0,0,0);
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('复审',2,9116165337005639259,1029063431013876529,2,0,0,0,0,0,0,0,0);
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('现场',2,9116165337005639259,1029063431013876529,3,0,0,0,0,0,0,0,0);
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('审批',2,5745107157522860074,5650735151785788005,4,0,0,0,0,0,0,0,0);
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('办结',2,4114528878294287249,4355950963446468199,5,0,0,0,0,0,0,0,0);
insert post(name,line_id,unit_id,post_id,sn,total,curr,wait_cnt,do_cnt,redo_cnt,delay_cnt,warn_cnt,alarm_cnt) values('事后监督',2,9116165337005639259,1029063431013876529,6,0,0,0,0,0,0,0,0);

-- 系统附件总表
create TABLE ctp_attachment (
  ID bigint,
  REFERENCE bigint,
  SUB_REFERENCE bigint, -- 与fommain表中的fieldxxxx域关联，若表单域针对的是文件
  FILENAME varchar(255),
  FILE_URL varchar(255),
  CREATEDATE datetime,
  ATTACHMENT_SIZE int
) default charset=utf8;

-- 主表单
-- 其id与col_summary.form_recordid关联
create TABLE formmain (
  formmain_name   varchar(255),
  ID bigint,
  STATE int,
  START_MEMBER_ID bigint,
  START_DATE datetime,
  APPROVE_MEMBER_ID bigint,
  APPROVE_DATE datetime,
  FINISHEDFLAG int,
  RATIFYFLAG int,
  RATIFY_MEMBER_ID bigint,
  RATIFY_DATE datetime,
  SORT int,
  MODIFY_MEMBER_ID bigint,
  MODIFY_DATE datetime,
  FIELD0001 varchar(80) -- 预置了100个域
, FIELD0002 varchar(80)
, FIELD0003 varchar(80)
, FIELD0004 varchar(80)
, FIELD0005 varchar(80)
, FIELD0006 varchar(80)
, FIELD0007 varchar(80)
, FIELD0008 varchar(80)
, FIELD0009 varchar(80)
, FIELD0010 varchar(80)
, FIELD0011 varchar(80)
, FIELD0012 varchar(80)
, FIELD0013 varchar(80)
, FIELD0014 varchar(80)
, FIELD0015 varchar(80)
, FIELD0016 varchar(80)
, FIELD0017 varchar(80)
, FIELD0018 varchar(80)
, FIELD0019 varchar(80)
, FIELD0020 varchar(80)
, FIELD0021 varchar(80)
, FIELD0022 varchar(80)
, FIELD0023 varchar(80)
, FIELD0024 varchar(80)
, FIELD0025 varchar(80)
, FIELD0026 varchar(80)
, FIELD0027 varchar(80)
, FIELD0028 varchar(80)
, FIELD0029 varchar(80)
, FIELD0030 varchar(80)
, FIELD0031 varchar(80)
, FIELD0032 varchar(80)
, FIELD0033 varchar(80)
, FIELD0034 varchar(80)
, FIELD0035 varchar(80)
, FIELD0036 varchar(80)
, FIELD0037 varchar(80)
, FIELD0038 varchar(80)
, FIELD0039 varchar(80)
, FIELD0040 varchar(80)
, FIELD0041 varchar(80)
, FIELD0042 varchar(80)
, FIELD0043 varchar(80)
, FIELD0044 varchar(80)
, FIELD0045 varchar(80)
, FIELD0046 varchar(80)
, FIELD0047 varchar(80)
, FIELD0048 varchar(80)
, FIELD0049 varchar(80)
, FIELD0050 varchar(80)
, FIELD0051 varchar(80)
, FIELD0052 varchar(80)
, FIELD0053 varchar(80)
, FIELD0054 varchar(80)
, FIELD0055 varchar(80)
, FIELD0056 varchar(80)
, FIELD0057 varchar(80)
, FIELD0058 varchar(80)
, FIELD0059 varchar(80)
, FIELD0060 varchar(80)
, FIELD0061 varchar(80)
, FIELD0062 varchar(80)
, FIELD0063 varchar(80)
, FIELD0064 varchar(80)
, FIELD0065 varchar(80)
, FIELD0066 varchar(80)
, FIELD0067 varchar(80)
, FIELD0068 varchar(80)
, FIELD0069 varchar(80)
, FIELD0070 varchar(80)
, FIELD0071 varchar(80)
, FIELD0072 varchar(80)
, FIELD0073 varchar(80)
, FIELD0074 varchar(80)
, FIELD0075 varchar(80)
, FIELD0076 varchar(80)
, FIELD0077 varchar(80)
, FIELD0078 varchar(80)
, FIELD0079 varchar(80)
, FIELD0080 varchar(80)
, FIELD0081 varchar(80)
, FIELD0082 varchar(80)
, FIELD0083 varchar(80)
, FIELD0084 varchar(80)
, FIELD0085 varchar(80)
, FIELD0086 varchar(80)
, FIELD0087 varchar(80)
, FIELD0088 varchar(80)
, FIELD0089 varchar(80)
, FIELD0090 varchar(80)
, FIELD0091 varchar(80)
, FIELD0092 varchar(80)
, FIELD0093 varchar(80)
, FIELD0094 varchar(80)
, FIELD0095 varchar(80)
, FIELD0096 varchar(80)
, FIELD0097 varchar(80)
, FIELD0098 varchar(80)
, FIELD0099 varchar(80)
, FIELD0100 varchar(80)
) default charset=utf8;

-- 用于定义表单的附件名称
create TABLE form_field_def (
  formmain varchar(80), -- 主表名称，例如formmain_0000
  field_name varchar(16), -- 表项名称，例如field0001
  name varchar(80), -- 域名称
  is_file int -- 是否是附件文件，1：是
) default charset=utf8;

-- 用于浏览申请表明细
create TABLE summary_list (
  col_summary_id bigint, -- 与col_summary表关联
  field_name varchar(80), -- 域名称，来自form_field_def表
  file_path varchar(120), -- 附件文件存放路径
  state_0 int, -- 碰撞状态
  state_1 int -- 是否补正，0：通过，1：补正
) default charset=utf8;

-- 定时器
create TABLE timer (
  line_id int NOT NULL, -- 业务线ID
  summary_id bigint NOT NULL, -- 申请单ID
  member_id bigint NOT NULL, -- 办理人ID，若为None，则表示政务大厅提交的
  d int NOT NULL
) default charset=utf8;

insert into timer(line_id,summary_id,member_id,d) values(1,0,0,0);
insert into timer(line_id,summary_id,member_id,d) values(2,0,0,0);

-- 事后监督记录总表
-- 记录已办结的所有 企业的 信息及其事后回访期限
create TABLE unit_revisit (
  line_id int NOT NULL, -- 归属的业务线
  summary_id bigint NOT NULL, -- 表单ID
  org_name varchar(120) NOT NULL, -- 公司名称
  org_structure_code varchar(80) NOT NULL, -- 企业组织机构代码
  subject varchar(80) NOT NULL, -- 申请主题
  end_date datetime NOT NULL, -- 办结日期
  visit_date datetime -- 回访期限
) default charset=utf8;

-- 预警、告警信息表
-- 用于记录针对每个业务线、环节的异常情况
create TABLE warn_alarm_table (
  flg int, -- 2:预警,3:风险
  line_id int, -- 业务线
  sn int, -- 岗位序号
  create_date datetime, -- 日期
  message varchar(255), -- 信息
  member bigint -- 发给人员id
  -- 针对预警和风险，会有很多扩展的应用要求
) default charset=utf8;

-- 工作时间明细
-- nday：期限1天或2天
-- lvl：等级，0当事人预警；1当事人和其领导预警
-- flg：跨天标志，0当天；1跨天
create TABLE worktime_mx (
  cur int,
  s_h int,
  e_h int,
  nday int,
  lvl int,
  cnt int,
  flg int
) default charset=utf8;

-- 科室 9~12 13~17
-- 期限1天
-- 个人预警 40% 提前6小时
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values( 9,15,16,1,0,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(10,16,17,1,0,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(11,17,24,1,0,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(11, 0,10,1,0,1,1); -- 跨天
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(12,10,11,1,0,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(14,11,12,1,0,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(15,12,14,1,0,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(16,14,15,1,0,1,0);

-- 个人+领导预警 60% 提前3小时
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values( 9,11,12,1,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(10,12,14,1,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(11,14,15,1,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(12,15,16,1,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(14,16,17,1,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(15,17,24,1,1,0,0); -- 跨天
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(15, 0,10,1,1,1,1); -- 跨天
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(16,10,11,1,1,1,0);

-- 期限2天
-- 个人预警 40% 提前10小时
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values( 9,11,12,2,0,1,0); -- 跨1天
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(10,12,14,2,0,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(11,14,15,2,0,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(12,15,16,2,0,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(14,16,17,2,0,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(15,17,24,2,0,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(15, 0,10,2,0,2,1); -- 跨2天
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(16,10,11,2,0,2,0);

-- 个人+领导预警 60% 提前6小时
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values( 9,15,16,2,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(10,16,17,2,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(11,17,24,2,1,0,1);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(11, 0,10,2,1,1,1); -- 跨天
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(12,10,11,2,1,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(14,11,12,2,1,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(15,12,14,2,1,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(16,14,15,2,1,1,0);

-- 政务大厅 9~17
-- 期限1天
-- 个人预警 40% 提前5小时
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values( 9,13,14,1,0,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(10,14,15,1,0,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(11,15,16,1,0,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(12,16,17,1,0,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(13,17,24,1,0,0,1);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(13, 0,10,1,0,1,1); -- 跨天
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(14,10,11,1,0,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(15,11,12,1,0,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(15,11,12,1,0,1,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(16,12,13,1,0,1,0);

-- 个人+科室处长预警 60% 提前3小时
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values( 9,11,12,1,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(10,12,13,1,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(11,13,14,1,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(12,14,15,1,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(13,15,16,1,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(14,16,17,1,1,0,0);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(15,17,24,1,1,0,1);
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(15, 0,10,1,1,1,1); -- 跨天
insert into worktime_mx(cur,s_h,e_h,nday,lvl,cnt,flg) values(16,10,11,1,1,1,0);

create TABLE kpi_001 (
  create_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 结束时间
  member bigint, -- 人员ID
  summary_id bigint, -- 事务ID
  line_id int, -- 业务线
  sn int, -- 节点
  dtime int, -- 用时（分钟）
  start_date datetime -- 起始时间
) default charset=utf8;

create TABLE line_desc (
  id int primary key not null, -- 业务线ID
  info varchar(80) -- 业务线说明
) default charset=utf8;

insert into line_desc(id,info) values(1,'人力资源服务许可'),(2,'劳务派遣行政许可');

create TABLE sn_desc (
 line_id int not null, -- 业务线 节点编号
 id int not null, -- 业务线ID
 info varchar(80), -- 说明
 primary key(id,line_id)
) default charset=utf8;

insert into sn_desc(line_id,id,info) values (1,0,'受理'),(1,1,'初审'),(1,2,'复审'),(1,3,'审批'),(1,4,'办结');
insert into sn_desc(line_id,id,info) values (2,0,'受理'),(2,1,'初审'),(2,2,'复审'),(2,3,'现场'),(2,4,'审批'),(2,5,'办结');

-- 业务流水日志
-- 以“流水号”为基准，按时间轴把过程中出现的每一个事件每都记录起来
--
create TABLE sn_log (
  yw_sn varchar(80) not null, -- 事件对象
  uuid  varchar(80) not null,
  flg int, -- 0：工作流；1：预警；2：风险；3：特权
  t_stamp int, -- 精确到 毫秒 的时间戳
  create_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 事件时间轴
  primary key(yw_sn,uuid)
) default charset=utf8;

-- 人员日志
-- 以“人员”为基准，按时间轴把过程中出现的每一个事件每都记录起来
--
create TABLE member_log (
  member_id bigint not null, -- 人员ID
  uuid  varchar(80) not null,
  flg int, -- 0：工作流；1：预警；2：风险；3：特权
  t_stamp int, -- 精确到 毫秒 的时间戳
  create_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 事件时间轴
  primary key(member_id,uuid)
) default charset=utf8;

-- 服务对象
-- 以“服务对象（单位）”为基准，按时间轴记录
--
create TABLE service_obj_log (
  bar_code varchar(20) not null, -- 组织机构代码
  uuid  varchar(80) not null,
  t_stamp int, -- 精确到 毫秒 的时间戳
  create_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 事件时间轴

  name varchar(80),
  addr varchar(80),
  registered_capital varchar(80),
  registeration_number varchar(80),
  registered_addr varchar(80),
  legal_representative_id varchar(64),
  legal_representative_name varchar(64),
  legal_representative_tel varchar(24),
  operator_id varchar(64),
  operator_name varchar(64),
  operator_tel varchar(24),

  yw_sn varchar(80) not null,  -- 业务流水号

  primary key(bar_code,uuid)

) default charset=utf8;


-- 工作流日志
--
create TABLE wf_log (
  uuid varchar(80),
  sn varchar(80), -- 业务线的节点名称
  member varchar(80), -- 办理人员名称
  post varchar(80), -- 人员岗位名称
  subject varchar(80), -- 主题
  start_date datetime, -- 起始时间
  end_date datetime, -- 完成时间
  dlt_time int, -- 耗时（分钟）
  dlt_rate int -- 与期限要求的比值，dlt_time*100/期限要求（分钟），例如120（2小时）*100/480（8小时）=25
) default charset=utf8;

-- 预警、风险日志
create TABLE warn_log (
  uuid varchar(80),
  message varchar(255) -- 信息
) default charset=utf8;

-- 特权日志
create TABLE pri_log (
  uuid varchar(80),
  member varchar(80), -- 特权人名称
  post varchar(80), -- 特权人岗位名称
  message varchar(255) -- 信息
) default charset=utf8;

-- 数据铁笼应用-信息交换
create TABLE ex_message (
  sender begint NOT NULL,
  reader begint NOT NULL,
  send_message varchar(255) NOT NULL,
  reply_message varchar(255),
  flg int NOT NULL,
  send_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  read_date datetime
) default charset=utf8;

/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50626
 Source Host           : localhost
 Source Database       : gyrsj

 Target Server Type    : MySQL
 Target Server Version : 50626
 File Encoding         : utf-8

 Date: 01/25/2016 10:26:26 AM
*/

-- ----------------------------
--  Table structure for `user_message`
-- ----------------------------
--DROP TABLE IF EXISTS `user_message`;
CREATE TABLE `user_message` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sender_id` bigint(20) DEFAULT NULL COMMENT '发送人',
  `receiver_id` bigint(20) DEFAULT NULL COMMENT '接收人',
  `message` varchar(500) DEFAULT NULL COMMENT '消息',
  `status` int(1) DEFAULT NULL COMMENT '0-未读，1-已读',
  `receipt` varchar(500) DEFAULT NULL COMMENT '回执',
  `send_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '发送时间',
  `receipt_date` datetime DEFAULT NULL COMMENT '阅读时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

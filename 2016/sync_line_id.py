#encoding=UTF-8
#
#	2015.12.10 by shenwei @GuiYang
#	==============================
#	利用判断表单命名是否包含业务线的关键词来确定业务线的表单ID
#

import utils

cur_mysql = utils.mysql_conn()
oracle_conn = utils.oracle_conn()
cur_oracle = oracle_conn.cursor()

# 业务线1的关键词是：人力资源
utils.get_form(cur_oracle,cur_mysql,1,'人力资源服务许可')
# 业务线2的关键词是：劳务派遣
utils.get_form(cur_oracle,cur_mysql,2,'劳务派遣')
# 同步其它类型的表单
utils.get_form(cur_oracle,cur_mysql,1,'分管领导指派优先办理')
utils.get_form(cur_oracle,cur_mysql,2,'分管领导指派优先办理')

#
# 台湾、香港、澳门人员就业证办理就业审批表
# 台湾、香港、澳门人员就业证办理就业审批补正
#
#
utils.get_form(cur_oracle,cur_mysql,3,'台湾、香港、澳门人员就业证办理就业')

#
# 特殊工时工作制审批表
#
utils.get_form(cur_oracle,cur_mysql,4,'特殊工时工作制')

#
# 贵阳市民办职业培训学校审批表
#
utils.get_form(cur_oracle,cur_mysql,5,'贵阳市民办职业培训学校')

#
# 技工学校筹设行政许可审批表
# 技工学校筹设行政许可审批（补正）
#
utils.get_form(cur_oracle,cur_mysql,6,'技工学校筹设行政许可')

#
# 技工学校设立行政许可审批
# 技工学校设立行政许可审批（补正）
#
utils.get_form(cur_oracle,cur_mysql,7,'技工学校设立行政许可')

cur_mysql.close()
cur_oracle.close()
oracle_conn.close()

#
# Eof
#

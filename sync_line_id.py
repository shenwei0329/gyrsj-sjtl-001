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

cur_mysql.close()
cur_oracle.close()
oracle_conn.close()

#
# Eof
#

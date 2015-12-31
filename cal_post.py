#encoding=UTF-8
#
#   created by shenwei @GuiYang 2015.12.13
#
#   计算业务线的工作量
#

import sys
import utils

cur_mysql = utils.mysql_conn()

# 计算人力资源
utils.sum_summary(cur_mysql,1)
# 计算劳动派遣
utils.sum_summary(cur_mysql,2)

cur_mysql.close()

#
# Eof
#

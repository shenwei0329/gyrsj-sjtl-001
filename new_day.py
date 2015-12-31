#encoding=UTF-8
#
#   created by shenwei @GuiYang 2015.12.13
#
#

import utils

cur_mysql = utils.mysql_conn()
cur_mysql1 = utils.mysql_conn()

utils.new_day(cur_mysql,cur_mysql1)

cur_mysql.close()
cur_mysql1.close()

#
# Eof
#

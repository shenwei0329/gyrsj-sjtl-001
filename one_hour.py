#encoding=UTF-8
#
#   created by shenwei @GuiYang 2015.12.13
#
#

import utils

cur_mysql = utils.mysql_conn()
cur_mysql1 = utils.mysql_conn()
cur_mysql2 = utils.mysql_conn()

# 2015-12-22：
# 在正午12点，要对即将超期的业务提出预警。此预警在通知本人的同时，还需要通知其主管领导
#
utils.one_hour(cur_mysql,cur_mysql1,cur_mysql2)

cur_mysql.close()
cur_mysql1.close()
cur_mysql2.close()

#
# Eof
#

#encoding=UTF-8
#
#   created by shenwei @GuiYang 2015.12.13
#
#

import sys
import utils

cur_mysql = utils.mysql_conn()
oracle_conn = utils.oracle_conn()
cur_oracle = oracle_conn.cursor()

summary_id = sys.argv[1]
print utils.is_wait(cur_oracle,cur_mysql,summary_id)

cur_mysql.close()
cur_oracle.close()
oracle_conn.close()

#
# Eof
#

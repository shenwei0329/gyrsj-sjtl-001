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

utils.set_summary_state(cur_oracle,cur_mysql)

cur_mysql.close()
cur_oracle.close()
oracle_conn.close()

#
# Eof
#

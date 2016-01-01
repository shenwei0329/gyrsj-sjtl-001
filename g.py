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

utils.send_alarm(cur_mysql,"3467559369048346189","5106973534933246911",2,"【数据铁笼风险提示】：政务大厅，在受理《测试-006》<受理>时，提交材料存在缺失项，请知悉。")

cur_mysql.close()
cur_oracle.close()
oracle_conn.close()

#
# Eof
#

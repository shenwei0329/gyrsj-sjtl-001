#encoding=UTF-8
#
#   2015.12.10 by shenwei @GuiYang
#   ==============================
#   统计当天完成的申请办理数
#

import MySQLdb
import os
import sys
from subprocess import Popen,PIPE

import utils

cur_mysql = utils.mysql_conn()

# 从命令行获取业务线id
line_id = sys.argv[1]

# 获取属于该业务线的表单ID条件列表
form_id = utils.get_line(cur_mysql,line_id)

# 从申请单总表中获取当天的记录
#   ed_cnt：当天完成的申请
#   ing_cnt：当天受理的申请
ed_cnt = cur_mysql.execute('select id from col_summary where to_days(finish_date)=to_days(now()) and state=3 and line_id=%s and %s' % (line_id,form_id))
ing_cnt = cur_mysql.execute('select id from col_summary where to_days(start_date)=to_days(now()) and state=0 and line_id=%s and %s' % (line_id,form_id))

# 存入当天业绩
#print(">>> %s,%s <<<" % (ing_cnt,ed_cnt))
cur_mysql.execute('update year_total set m=%s where id=0 and line_id=%s' % (ing_cnt,line_id))

cur_mysql.close()

#
# Eof
#

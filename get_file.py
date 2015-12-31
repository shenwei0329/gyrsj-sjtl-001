#encoding=UTF-8
#
#   created by shenwei @GuiYang 2015.12.13
#
#   通过申请单ID获取它的附件文件信息
#
#

import utils

# 通过申请单ID获取formmain表项
def get_field(cur_mysql,id):
	sql = 'select a.formmain_name from line_def a,ctp_summary b where a.form_def_id=b.form_appid and b.id= %s' % id
	cnt = cur_mysql.execute(sql)
	if cnt>0:
		one = cur_mysql.fetchone()
		formmain_name = str(one[0])

		sql = 'select * from formmain where formmain_name = "%s" ' % formmain_name
		cnt = cur_mysql.execute(sql)
		if cnt>0:
			one = cur_mysql.fetchone()
			print one

cur_mysql = utils.mysql_conn()
sql = 'select form_appid,form_recordid from col_summary'
total_cnt = cur_mysql.execute(sql)

if total_cnt>0:

	form_appids = []
	form_recordids = []
	for i in range(total_cnt):
		one = cur_mysql.fetchone()
		form_appids.append(str(one[0]))
		form_recordids.append(str(one[1]))

	for i in range(total_cnt):

cur_mysql.close()

#
# Eof
#

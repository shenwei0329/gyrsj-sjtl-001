#encoding=UTF-8
#

import utils

cur_mysql = utils.mysql_conn()
oracle_conn = utils.oracle_conn()
cur_oracle = oracle_conn.cursor()

sql = 'select form_def_id from line_def'
cnt = cur_mysql.execute(sql)
if cnt>0:
	ids = []
	for i in range(cnt):
		one = cur_mysql.fetchone()
		ids.append(str(one[0]))

	# 清空 form_field_def 记录
	sql = 'delete from form_field_def'
	cur_mysql.execute(sql)

	for form_def_id in ids:
		ret = utils.get_formmain_field_desc(cur_oracle,form_def_id)
		if ret is not None:
			print("-------------------------------------------")
			for v in ret:
				print("%s : %s\n" %(v, ret[v]))
				sql = 'insert into form_field_def(formmain,field_name,name) values("%s","%s","%s")' % (ret['formmain'],v.encode('utf-8'),ret[v].encode('utf-8'))
				print sql
				cur_mysql.execute(sql)
			print("-------------------------------------------")

cur_oracle.close()
cur_mysql.close()
oracle_conn.close()

#
# Eof
#

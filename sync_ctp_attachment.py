#encoding=UTF-8
#
#	2015.12.10 by shenwei @GuiYang
#	==============================
#	从OA同步ctp_attachment表
#

import utils

cur_mysql = utils.mysql_conn()
oracle_conn = utils.oracle_conn()
cur_oracle = oracle_conn.cursor()

cur = cur_oracle.execute('select ID,REFERENCE,SUB_REFERENCE,FILENAME,FILE_URL,CREATEDATE,ATTACHMENT_SIZE from ctp_attachment order by createdate')
while 1:
	one = cur.fetchone()
	if one!=None:
		id = str(one[0])
		if utils.is_include(cur_mysql,'ctp_attachment',id)==0:
			sql = 'insert into ctp_attachment(ID,REFERENCE,SUB_REFERENCE,FILENAME,FILE_URL,CREATEDATE,ATTACHMENT_SIZE) values('
			for i in range(len(one)):
				if i==0:
					sql += str(one[0])
				elif i==3 or i==5:
					sql += ',"'+ str(one[i])+'"'
				else:
					sql += ','+ str(one[i])
			sql += ')'
			#print sql
			cur_mysql.execute(sql)
	else:
		break
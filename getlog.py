#encoding=utf-8
#
#
#

import cx_Oracle

def PrintOne(v):
	one = v.fetchone()
	if one!=None:
		print(one)
	return one

tns_name = cx_Oracle.makedsn('10.169.8.59','1521','orcl')
db = cx_Oracle.connect('v3xuser','Www123456',tns_name)

cur_src = db.cursor()

tables = ['ctp_user_message','ctp_app_log','ctp_affair','logon_log','ctp_process_log']

while 1:

	# for 'ctp_user_message'
	#
	print("[ %s ]:" % tables[0])
	print("-------------------------------------------------------")
	cur = cur_src.execute('select sender_id,user_id,message_content from '+tables[0]+' order by creation_date')
	while 1:
		if PrintOne(cur)==None:
			break;

	# for 'ctp_app_log'
	#
	print("[ %s ]:" % tables[1])
	print("-------------------------------------------------------")
	cnt = cur_src.execute('select action_user_id,action_department_id,action_account_id,param0,param1,param2,ip from '+tables[1]+' order by action_date')
	while 1:
		if PrintOne(cur)==None:
			break;

	# for 'ctp_affair'
	#
	print("[ %s ]:" % tables[2])
	print("-------------------------------------------------------")
	cnt = cur_src.execute('select member_id,sender_id,subject,object_id,state,form_id,form_operation_id,receive_time from '+tables[2]+' order by receive_time')
	while 1:
		if PrintOne(cur)==None:
			break;

	# for 'logon_log'
	#
	print("[ %s ]:" % tables[3])
	print("-------------------------------------------------------")
	cnt = cur_src.execute('select account_id,department_id,member_id,logon_time,logout_time from '+tables[3]+' order by logon_time')
	while 1:
		if PrintOne(cur)==None:
			break;

	# for 'ctp_process_log'
	#
	print("[ %s ]:" % tables[4])
	print("-------------------------------------------------------")
	cnt = cur_src.execute('select process_id,activity_id,action_id,action_user_id,param0,param1,action_time from '+tables[4]+' order by action_time')
	while 1:
		if PrintOne(cur)==None:
			break;

	break

#process = Popen('mysql -ushenwei -psw64419 v50', stdin=PIPE, shell=True)  
#output = process.communicate('source '+t+'.sql')  

cur_src.close()
#cur_dst.close()
conn_src.close()
#conn_dst.close()

#encoding=UTF-8
#

from subprocess import Popen,PIPE
print db.dsn

cur_src = db.cursor()

tables = ['org_member']

info = cur_src.execute('select * from '+tables[0])

while 1:
	one = info.fetchone()
	if one!=None:
		print one
	else:
		break

cur_src.close()
db.close()


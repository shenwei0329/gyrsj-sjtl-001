#encoding=UTF-8
#
#
#

#from subprocess import Popen,PIPE
import cx_Oracle

tns_name = cx_Oracle.makedsn('10.169.8.59','1521','orcl')
db = cx_Oracle.connect('v3xuser','Www123456',tns_name)
cur_src = db.cursor()

tables = [	'col_summary order by create_date',
		'form_definition order by create_time',
		'form_resource',
		'formmain order by start_date',
		'ctp_content_all order by create_date',
		'ctp_attachment order by createdate',
		'coll_360_detail order by send_time',
		'coll_cube_detail order by start_time',
		'coll_cube_index order by id',
		'coll_cube_index_set order by id',
		'coll_cube_data order by update_date']

while 1:

	for t in tables:
		#
		print("[ %s ]:" % t)
		print("-------------------------------------------------------")
		rec = cur_src.execute('select * from '+t)
		while 1:
			one = rec.fetchone()
			if one==None:
				break;
			print(one)

	break

#process = Popen('mysql -ushenwei -psw64419 v50', stdin=PIPE, shell=True)  
#output = process.communicate('source '+t+'.sql')  

cur_src.close()
db.close()

#
# Eof
#


#encoding=UTF-8
#	Created by shenwei @GuiYang
#
#	当ETL工具从OA系统获取到基础数据的SQL文件后，因OA采用的Oracle与MySQL存在语言差异
#   需要在使用这些SQL语句时进行关键字替换。
#

import MySQLdb
from subprocess import Popen,PIPE
import os

#MySQL数据库连接定义
conn = MySQLdb.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='123456',
    db='gyrsj',
    charset="utf8")
cur = conn.cursor()

#OA的基础数据列表
tables = ['org_member','org_unit','org_level','org_post']

for t in tables:
    f = t + '.sql'
    fsize = os.path.getsize(f)
    if fsize<=0:
        continue

    #print("do sync...")
    try:
        #在同步前，须清除原有表
        cur.execute('drop table '+t)
        cur.fetchall()
    except:
        print('No table ['+t+']')
    finally:
        #做语法替换
        if fsize>0:
            cmd = 'sed -i "s/%s//g" %s' % ("'||chr(10)||'",f)
            os.popen(cmd)
            cmd = 'sed -i "s/%s//g" %s' % ("'||chr(13)||'",f)
            os.popen(cmd)
            cmd = 'sed -i "s/INTEGER/bigint/g" %s' % f
            os.popen(cmd)
            cmd = 'sed -i "s/VARCHAR2/varchar/g" %s' % f
            os.popen(cmd)
            cmd = 'sed -i "s/orcl/gyrsj/g" %s' % f
            os.popen(cmd)
            cmd = 'sed -i "s/CLOB/longtext/g" %s' % f
            os.popen(cmd)
            '''执行SQL'''
            process = Popen('mysql -uroot -p123456 gyrsj', stdin=PIPE, shell=True)
            output = process.communicate('source '+f)
    print(".done.")
cur.close()
conn.close()


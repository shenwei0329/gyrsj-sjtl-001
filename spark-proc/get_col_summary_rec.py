#encoding=UTF-8
#
#   2015.12.10 by shenwei @GuiYang
#   ==============================
#
#

import utils

def do_rec(cur,cur_mysql):

    while 1:
        one = cur.fetchone()
        if one is None:
            break

        s = ""

        for i in range(len(one)):

            if i==0:
                s = str(one[i]).replace('\n','').replace('\r','').replace(',',' ').replace('(自动发起)','').replace('（补正）','') + "-"
            elif i==1:
                s += str(one[i]).replace('\m','').replace('\n','').replace('\r','').replace(',',' ').replace('(自动发起)','').replace('（补正）','').strip() + '<:KEY:>'
            elif i==6:
                sql = 'select a.name,b.name from org_member a, org_post b where a.id="%s" and b.id=a.org_post_id' % str(one[i])
                cnt = cur_mysql.execute(sql)
                if cnt>0:
                    oone = cur_mysql.fetchone()
                    s += ("%s@%s<:T:>" % (str(oone[0]),str(oone[1])))
            else:
                s += str(one[i]).replace('\n','').replace('\r','').replace(',',' ').replace('(自动发起)','').replace('（补正）','') + "<:T:>"

        print(s)

cur_mysql = utils.mysql_conn()
oracle_conn = utils.oracle_conn()
cur_oracle = oracle_conn.cursor()

cur = cur_oracle.execute('select create_date,subject,id,state,start_date,finish_date,start_member_id,current_nodes_info from col_summary order by create_date')
do_rec(cur,cur_mysql)

cur_oracle.close()
oracle_conn.close()
cur_mysql.close()

#
# Eof
#

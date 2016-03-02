#encoding=UTF-8
#
#   2015.12.10 by shenwei @GuiYang
#   ==============================
#
#   2016.3.2@贵阳市人社局
#   - 在KEY中增加 流水号字段 <:SN:>
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
                cr_date = str(one[i]).replace('\m','').replace('\n','').replace('\r','').replace(',',' ').replace('(自动发起)','').replace('（补正）','')
                s = cr_date + "-"
            elif i==1:
                subject = str(one[1]).replace('\m','').replace('\n','').replace('\r','').replace(',',' ').replace('(自动发起)','').replace('（补正）','').strip()
                sql = 'select yw_sn from col_summary where create_date="%s" and subject="%s"' % (cr_date,subject)
                cnt = cur_mysql.execute(sql)
                if cnt>0:
                    oone = cur_mysql.fetchone()
                    yw_sn = str(oone[0])
                else:
                    yw_sn = ""
                s += subject + ("<:SN:>%s" % yw_sn) + '<:KEY:>'
            elif i==2 or i==3:
                sql = 'select a.name,b.name from org_member a,org_post b where a.id="%s" and b.id=a.org_post_id' % str(one[i])
                cnt = cur_mysql.execute(sql)
                if cnt>0:
                    oone = cur_mysql.fetchone()
                    s += ('%s@%s<:T:>' % (str(oone[0]),str(oone[1])))
            else:
                s += str(one[i]).replace('\n','').replace('\r','').replace(',',' ').replace('(自动发起)','').replace('（补正）','') + "<:T:>"

        print(s.strip())

cur_mysql = utils.mysql_conn()
oracle_conn = utils.oracle_conn()
cur_oracle = oracle_conn.cursor()

cur = cur_oracle.execute('select create_date,subject,member_id,sender_id,receive_time,complete_time,node_policy from ctp_affair order by create_date')
do_rec(cur,cur_mysql)

cur_oracle.close()
oracle_conn.close()
cur_mysql.close()

#
# Eof
#

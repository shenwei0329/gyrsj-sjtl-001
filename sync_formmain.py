#encoding=UTF-8
#
#	2015.12.10 by shenwei @GuiYang
#	==============================
#	从OA同步formmain表，该表保存了申请单附件的关联
#   formmain.field00?? <-> ctp_attachment.sub_reference
#   ctp_attachment.file_url为附件文件存放的名称
#   ctp_attachment.filename为附件文件的真实名称
#   附件文件按日期存放在/Seeyon/G6/base/upload目录下
#   路径：upload/2015/12/4/，代表申请受理日期为2015年12月4日
#

import utils

cur_mysql = utils.mysql_conn()
oracle_conn = utils.oracle_conn()
cur_oracle = oracle_conn.cursor()

# 获得业务线1的formmain表名列表
formmain_rec = utils.get_formmain(cur_mysql,1)
# 同步每个formmain表
for f in formmain_rec:
	utils.sync_formmain(cur_oracle,cur_mysql,f)

# 获取业务线2的formmain表名列表
formmain_rec = utils.get_formmain(cur_mysql,2)
# 同步每个formmain表
for f in formmain_rec:
	utils.sync_formmain(cur_oracle,cur_mysql,f)

cur_mysql.close()
cur_oracle.close()
oracle_conn.close()
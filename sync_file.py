#encoding=UTF-8
#	Created by shenwei @GuiYang
#
#   在OA的应用服务器上运行，用于同步附件文件
#
#   在master上运行：
#       rsync --daemon --config=/etc/rsyncd.conf
#

import time
from subprocess import Popen

while 1:
	# 把上传的文件同步到master上
	cmd = "rsync -avz /cygdrive/d/Seeyon/G6/base/upload 10.169.7.10::rdata"
	process = Popen(cmd, stdin=None, shell=True)
	process.wait()

	time.sleep(60)

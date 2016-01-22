#encoding=UTF-8
#
#  数据库关联工具 【 数据库 间 关联 之 A 表关联】 构建器
#  ======================================
#	2016.1.22 by shenwei @GuiYang
#
#

import sys;
from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext

APP_NAME = "TableABuilder"

# 函数1
# 用途：分离以':'间隔的 K-V
#
def f1(s):
    ss = s.split(':')
    return (ss[0],ss[1])

# 函数2
# 用途：合成两个字符串，以','为间隔
#
def f2(a,b):
    return ("%s,%s" % (a,b))

def main(sc):

    # 装载　A　表
    lines = sc.textFile("/tmp/root/table_a.txt")
    # 获取 A 表 K-V[]
    pairs = lines.map(f1)
    res = pairs.reduceByKey(f2).collect()

    for r in res:
        s = ""
        i = 0
        for v in r:

            if len(v)==0:
                continue

            if i==0:
                s += v + ':'
                i = 1
            elif i==1:
                s += v
                i = 2
            else:
                s += (',' + v)

        # s中的数据格式
        # 表名:[ID,...]
        #
        print s

if __name__ == "__main__":

 
    reload(sys)
    sys.setdefaultencoding("utf8")

    conf = SparkConf().setAppName(APP_NAME)
    #conf = conf.setMaster("local[*]")
    #conf = conf.setMaster("spark://master:7077")
    #conf = conf.setMaster("yarn-cluster")
    conf = conf.setMaster("yarn-client")
    sc   = SparkContext(conf=conf)

    main(sc)

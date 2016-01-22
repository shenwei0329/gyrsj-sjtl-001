#encoding=UTF-8
#
#  数据库关联工具 【 数据库 间 关联 】 分析器
#  ======================================
#	2016.1.22 by shenwei @GuiYang
#
#

import sys;
from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext

APP_NAME = "TableAnalyser"

# 函数0
# 用途：分离以','间隔的 K-V
#
def f0(s):
    ss = s.split(',')
    return (ss[0],ss[1])

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

# 函数3
# 用途：分离以'^'间隔的 K-V
#
def f3(s):
    ss = s.split('^')
    return (ss[0],ss[1])

def main(sc):

    # 获取 A 内容
    A = sc.textFile("/tmp/root/res_a.txt")
    # 构建 A 的 K-V[]
    A_pairs = A.map(f1).collect()

    # 获取 B 内容
    # 构建 B 的 K-V[]
    B = sc.textFile("/tmp/root/res_b.txt")
    B_pairs = B.map(f1).collect()

    a_table_names = []
    a_table_values = []
    for pair in A_pairs:
        # 获取 表名
        a_table_names.append(pair[0])
        # 获取该表的 ID值组
        dat = pair[1].split(',')
        a_table_values.append(dat)

    '''
    for i in range(len(a_table_names)):
        print(" %s -> %s" % (a_table_names[i],a_table_values[i]))
    '''

    b_table_names = []
    b_table_values = []
    for pair in B_pairs:
        # 获取 表名
        b_table_names.append(pair[0])

        # 进一步分解出该表内容的 K-V[]
        entry = pair[1][:-1].split(',')

        if len(entry)==1 and len(str(entry[0]))<1:
            # 该表无记录时，填充K-V = ('None','None')
            b_table_values.append(('None','None'))
            continue

        # 构建 RDD
        vv = sc.parallelize(entry)
        # 分解成 K-V[]
        v_pairs = vv.map(f3)
        # 获得 V 数组值
        b_table_values.append(v_pairs.reduceByKey(f2).collect())

        # 此时，b_table_values的内容是：
        # 域名,[域值,...]

        # 将 B 表各个 域的值 与 A 表值 进行逐个比较
        # 若 Bi.fi.[...] in Aj[...]中，则：B.f 与 Aj 相关
        # 注：len(Bi.fi)>0 and Bi.fi[]!='None' and len(Bi.fi[])>5
        #

    '''
    print(">>> b_table_names:  %d" % len(b_table_names))
    print(">>> b_table_values: %d" % len(b_table_values))

    for i in range(len(b_table_names)):
        print(" %s -> %s" % (b_table_names[i],b_table_values[i]))
    '''

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

#encoding=UTF-8
#
#  数据库关联工具 【 数据库 间 关联 】 分析器
#  ======================================
#	2016.1.22 by shenwei @GuiYang
#
#  2016.1.24: 调试基本通过，至少2小时没出结果！运算量还真大。
#

import sys;
from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext

APP_NAME = "TableAnalyser"

# 函数1
# 用途：分离以':'间隔的 K-V
#
def f1(s):
    return tuple(s.split(':'))

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
    if len(ss)<2:
        return ("None","None")
    return tuple(ss)

def main(sc):

    # 获取 A 内容
    A = sc.textFile("/tmp/root/res_a.txt")
    # 构建 A 的 K-V[]
    A_pairs = A.map(f1).collect()

    # 获取 B 内容
    B = sc.textFile("/tmp/root/res_b.txt")
    # 构建 B 的 K-V[]
    B_pairs = B.map(f1).collect()

    debug_info = []
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

        if pair[1]==',':
            continue

        # 获取 表名
        b_table_names.append(pair[0])

        # 进一步分解出该表内容的 K-V[]
        # 获得 V 数组值：(域名,"域值,...")
        _tmp = sc.parallelize(tuple(pair[1][:-1].split(','))).map(f3).reduceByKey(f2).collect()
        b_table_values.append(_tmp)

    # 将 B 表各个 域的值 与 A 表值 进行逐个比较
    # 若 Bi.fi.[...] in Aj[...]中，则：B.f 与 Aj 相关
    # 注：len(Bi.fi)>0 and Bi.fi[]!='None' and len(Bi.fi[])>5
    #

    a_b_rel = {}
    b_i = 0

    # 缓存A表记录
    # 为了提高分析速度，先把A表特征缓存
    #
    a_values = []
    a_names = []
    a_i = 0
    for a in a_table_values:
        # a = [域值,...]
        if len(a)==0:
            # 空表
            a_i += 1
            continue

        aRDD = sc.parallelize(tuple(a)).map(lambda s: (s,1)).cache()
        a_values.append(aRDD)
        a_names.append(a_table_names[a_i])
        a_i += 1

    # 扫描每个B表以及表内每一个域
    # =========================
    # 非常耗时的工作！
    #
    for bs in b_table_values:

        if bs[0] == 'None' or len(bs)!=2:
            # 空表
            b_i += 1
            continue

        # 检索 [('域名','域值,...'),('域名','域值,...'),...]
        for b in bs:
            # b = (域名,'域值,...')

            # 合并相同的 特征值
            b_value = sc.parallelize(tuple(str(b[1]).split(','))).map(lambda s: (s,1)).reduceByKey(lambda a,b: 1).cache()

            # 扫描每个A表的主键组
            for i in range(len(a_values)):

                # ！！！算法核心！！！
                #===================
                # 合并 A 和 B.域值，做KEY统计，过滤出值>1的，再合并B.域值，做统计，过滤出值==1的，收集起来，看看是否有内容
                #
                count = sc.parallelize(('begin',)).map(lambda s: (s,1)).union(a_values[i]).union(b_value).\
                    reduceByKey(lambda a,b: a+b).filter(lambda v: v[1]>1).union(b_value).reduceByKey(lambda a,b: a+b).filter(lambda v: v[1]==1).count()

                #debug_info.append(">: isInclude(%d)" % (count))

                if count==0:
                    # 表明，该表域的值被完整映射到 表A 的ID域中，所以，表明这两个表通过 该域 构建相关
                    a_b_rel[a_names[i]] = [b_table_names[b_i],b[0]]

                #a_b_rel[a_table_names[a_i]] = [tuple(_tmp),a_result]

                a_i += 1

        #if len(a_b_rel)>20:
        #    break

        b_i += 1

    for key in a_b_rel:
        print("%s,%s,%s" % (key,a_b_rel[key][0],a_b_rel[key][1]))

    for v in debug_info:
        print("%s" % v)

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

#encoding=UTF-8
#
#

import sys;
from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext

APP_NAME = "myTest"

def f0(s):
	ss = s.split('<:KEY:>')
	return (ss[0],ss[1])

def f1(s1,s2):
	
	if type(s1)!=tuple:
		if type(s2)==tuple:
			return (s1,)+s2
		return (s1,s2)
	return s1+(s2,)

def f2(s):
	
	reload(sys);
	sys.setdefaultencoding("utf8") 

        if type(s[1])==tuple and len(s[1])>0:
		sss = ("",)
		for v in s[1]:
			if type(sss)!=tuple:
				sss = tuple(str(v).split('<:T:>'))
			else:
				sss += tuple(str(v).split('<:T:>'))
	else:
		sss = s[1]
	return (s[0],sss)

def main(sc):

        reload(sys);
        sys.setdefaultencoding("utf8")

	mess = sc.textFile("/tmp/root/log.txt").map(f0).reduceByKey(f1).map(f2).sortByKey().collect()
	#mess = sc.textFile("/tmp/root/log.txt").map(f0).reduceByKey(f1).collect()

	for m in mess:
		rec = {}
		"""
			yyyy-mm-dd HH:MM:SS-subject<:SN:>yw_sn
		"""
		#print(m[0])
		rec['create_date'] = m[0][0:19]
		subject_sn = (m[0][20:]).split('<:SN:>')
		rec['subject'] = subject_sn[0]
		rec['sn'] = subject_sn[1]
		
		field = []
		dd = {}
                if type(m[1])==tuple and len(m[1])>1:
			i = 0
			for v in m[1]:
				if len(str(v))>0:
					if i==0:
						dd['receiver'] = str(v)
					elif i==1:
						dd['sender'] = str(v)
					elif i==2:
						dd['start_date'] = str(v)
					elif i==3:
						dd['end_date'] = str(v)
					elif i==4:
						dd['post'] = str(v)
					#print("\t%s" % str(v))
					i += 1
				else:
					if len(dd)>0:
						field.append(dd)
					i = 0
					dd = {}
					#print("++++ %s " % str(dd))
		"""
		else:
			print("\t%s" % str(m[1][0]))
		"""

		rec["field"] = field

		print(rec['subject'])
		print(rec['sn'])
		print(rec['create_date'])

		field = rec['field']
		for f in field:
			print("\tPOST: %s" % f['post'])
			print("\t\t%s - %s" % (f['start_date'],f['end_date']))
			print("\tReceiver: %s" % f['receiver'])
			print("\t\tSender: %s" % f['sender'])
			print("")

		print("------------------")

if __name__ == "__main__":

 
	reload(sys);
	sys.setdefaultencoding("utf8") 

	conf = SparkConf().setAppName(APP_NAME)
	#conf = conf.setMaster("local[*]")
	#conf = conf.setMaster("spark://master:7077")
	#conf = conf.setMaster("yarn-cluster")
	conf = conf.setMaster("yarn-client")
	sc   = SparkContext(conf=conf)

        main(sc)

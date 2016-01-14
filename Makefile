#
#

all:PutExample.class GetExample.class Hbase.class

PutExample.class: PutExample.java
	javac -classpath `hbase classpath` PutExample.java -Xlint:deprecation
	java -classpath `hbase classpath` PutExample 2>/dev/null

GetExample.class: GetExample.java
	javac -classpath `hbase classpath` GetExample.java -Xlint:deprecation
	java -classpath `hbase classpath` GetExample 2>/dev/null

Hbase.class: Hbase.java
	javac -classpath `hbase classpath` Hbase.java -Xlint:deprecation
	java -classpath `hbase classpath` Hbase 2>/dev/null


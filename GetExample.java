/*
 */

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.KeyValue;
import org.apache.hadoop.hbase.util.Bytes;
import java.util.ArrayList;
import java.util.List;

import java.io.IOException;

public class GetExample {

	public static void main(String[] args) throws IOException {

		List<Get> gets = new ArrayList<Get>();

		Configuration conf = HBaseConfiguration.create();

		HTable table = new HTable(conf,"member");

		Get get = new Get(Bytes.toBytes("shenwei"));
		get.addColumn(Bytes.toBytes("info"),Bytes.toBytes("name"));
		gets.add(get);

		Get get1 = new Get(Bytes.toBytes("shenwei"));
		get1.addColumn(Bytes.toBytes("info"),Bytes.toBytes("addr"));
		gets.add(get1);

		Get get2 = new Get(Bytes.toBytes("shenwei"));
		get2.addColumn(Bytes.toBytes("info"),Bytes.toBytes("sex"));
		gets.add(get2);

		Result[] ress = table.get(gets);
		System.out.println("Result: " + ress);

		for (Result res : ress){
			for (KeyValue kv : res.raw()){
				System.out.println("Row: " + Bytes.toString(kv.getRow()) + 
					" Family: " + Bytes.toString(kv.getFamily()) +
					" Qualifier: " + Bytes.toString(kv.getQualifier()) +
					" Value: " + Bytes.toString(kv.getValue()));
			}
		}
	}
}

/*
 */

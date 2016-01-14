/*
 */

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.util.Bytes;

import java.io.IOException;

public class PutExample {

	public static void main(String[] args) throws IOException {

		Configuration conf = HBaseConfiguration.create();

		HTable table = new HTable(conf,"member");

		Put put = new Put(Bytes.toBytes("shenwei"));

		put.add(Bytes.toBytes("info"),Bytes.toBytes("sex"),Bytes.toBytes("man"));

		table.put(put);
	}
}

/*
 */

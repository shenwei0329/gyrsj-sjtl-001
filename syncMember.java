/*
 * 构建Hbase下的“人物”主题数据集
 * ===========================
 * 2016.1.18 Created by shenwei @GuiYang
 *
 * -2016.1.21：增加人与人之间的关联信息
 *
 */

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.HColumnDescriptor;
import org.apache.hadoop.hbase.HTableDescriptor;
import org.apache.hadoop.hbase.KeyValue;
import org.apache.hadoop.hbase.client.Delete;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.HBaseAdmin;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.HTablePool;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.util.Bytes;

import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Connection;
import java.sql.Statement;

import java.util.Date;
import java.text.SimpleDateFormat;

public class syncMember {

    // 声明静态配置
    static Configuration conf = null;
    static {
        conf = HBaseConfiguration.create();
        conf.set("hbase.zookeeper.quorum", "master");
    }

    /*
     * 创建表
     * 
     * @tableName 表名
     * 
     * @family 列族列表
     */
    public static void creatTable(String tableName, String[] family)
            throws Exception {
        HBaseAdmin admin = new HBaseAdmin(conf);
        HTableDescriptor desc = new HTableDescriptor(tableName);
        for (int i = 0; i < family.length; i++) {
            desc.addFamily(new HColumnDescriptor(family[i]));
        }
        if (admin.tableExists(tableName)) {
            //System.out.println("table Exists!");
            /*System.exit(0);*/
            return;
        } else {
            admin.createTable(desc);
            System.out.println("create table Success!");
        }
    }

    /*
     * 为表添加数据（适合知道有多少列族的固定表）
     * 
     * @rowKey rowKey
     * 
     * @tableName 表名
     * 
     * @column1 第一个列族列表
     * 
     * @value1 第一个列的值的列表
     * 
     * @column2 第二个列族列表
     * 
     * @value2 第二个列的值的列表
     */
    public static void addData(String rowKey, String tableName,
            String family, String column, String value) throws IOException {

        //System.out.println(">>> addData("+rowKey+","+tableName+","+family+","+column+","+value+")");
        Put put = new Put(Bytes.toBytes(rowKey));// 设置rowkey
        HTable table = new HTable(conf, Bytes.toBytes(tableName));// HTabel负责跟记录相关的操作如增删改查等//

        put.add(Bytes.toBytes(family),Bytes.toBytes(column), Bytes.toBytes(value));
        table.put(put);

        //System.out.println("add data Success!");
    }

    /*
     * 根据rwokey查询
     * 
     * @rowKey rowKey
     * 
     * @tableName 表名
     */
    public static Result getResult(String tableName, String rowKey)
            throws IOException {
        Get get = new Get(Bytes.toBytes(rowKey));
        HTable table = new HTable(conf, Bytes.toBytes(tableName));// 获取表
        Result result = table.get(get);
        for (KeyValue kv : result.list()) {
            System.out.println("family:" + Bytes.toString(kv.getFamily()));
            System.out
                    .println("qualifier:" + Bytes.toString(kv.getQualifier()));
            System.out.println("value:" + Bytes.toString(kv.getValue()));
            System.out.println("Timestamp:" + kv.getTimestamp());
            System.out.println("-------------------------------------------");
        }
        return result;
    }

    /*
     * 根据rwokey查询
     * 
     * @rowKey rowKey
     * 
     * @tableName 表名
     *
     * @Family 列名
     *
     */
    public static Result getResultWithFamily(String tableName, String rowKey, String Family)
            throws IOException {
        Get get = new Get(Bytes.toBytes(rowKey));
        HTable table = new HTable(conf, Bytes.toBytes(tableName));// 获取表
        Result result = table.get(get);
        for (KeyValue kv : result.list()) {
            if (Bytes.toString(kv.getFamily()).equals(Family)) {
                System.out.println("family:" + Bytes.toString(kv.getFamily()));
                System.out.println("qualifier:" + Bytes.toString(kv.getQualifier()));
                System.out.println("value:" + Bytes.toString(kv.getValue()));
                System.out.println("Timestamp:" + kv.getTimestamp());
                System.out.println("-------------------------------------------");
            }
        }
        return result;
    }

    /*
     * 遍历查询hbase表
     * 
     * @tableName 表名
     */
    public static void getResultScann(String tableName) throws IOException {
        Scan scan = new Scan();
        ResultScanner rs = null;
        HTable table = new HTable(conf, Bytes.toBytes(tableName));
        try {
            rs = table.getScanner(scan);
            for (Result r : rs) {
                for (KeyValue kv : r.list()) {
                    System.out.println("row:" + Bytes.toString(kv.getRow()));
                    System.out.println("family:"
                            + Bytes.toString(kv.getFamily()));
                    System.out.println("qualifier:"
                            + Bytes.toString(kv.getQualifier()));
                    System.out
                            .println("value:" + Bytes.toString(kv.getValue()));
                    System.out.println("timestamp:" + kv.getTimestamp());
                    System.out
                            .println("-------------------------------------------");
                }
            }
        } finally {
            rs.close();
        }
    }

    /*
     * 遍历查询hbase表
     * 
     * @tableName 表名
     */
    public static void getResultScann(String tableName, String start_rowkey,
            String stop_rowkey) throws IOException {
        Scan scan = new Scan();
        scan.setStartRow(Bytes.toBytes(start_rowkey));
        scan.setStopRow(Bytes.toBytes(stop_rowkey));
        ResultScanner rs = null;
        HTable table = new HTable(conf, Bytes.toBytes(tableName));
        try {
            rs = table.getScanner(scan);
            for (Result r : rs) {
                for (KeyValue kv : r.list()) {
                    System.out.println("row:" + Bytes.toString(kv.getRow()));
                    System.out.println("family:"
                            + Bytes.toString(kv.getFamily()));
                    System.out.println("qualifier:"
                            + Bytes.toString(kv.getQualifier()));
                    System.out
                            .println("value:" + Bytes.toString(kv.getValue()));
                    System.out.println("timestamp:" + kv.getTimestamp());
                    System.out
                            .println("-------------------------------------------");
                }
            }
        } finally {
            rs.close();
        }
    }

    /*
     * 查询表中的某一列
     * 
     * @tableName 表名
     * 
     * @rowKey rowKey
     */
    public static void getResultByColumn(String tableName, String rowKey,
            String familyName, String columnName) throws IOException {
        HTable table = new HTable(conf, Bytes.toBytes(tableName));
        Get get = new Get(Bytes.toBytes(rowKey));
        get.addColumn(Bytes.toBytes(familyName), Bytes.toBytes(columnName)); // 获取指定列族和列修饰符对应的列
        Result result = table.get(get);
        for (KeyValue kv : result.list()) {
            System.out.println("family:" + Bytes.toString(kv.getFamily()));
            System.out
                    .println("qualifier:" + Bytes.toString(kv.getQualifier()));
            System.out.println("value:" + Bytes.toString(kv.getValue()));
            System.out.println("Timestamp:" + kv.getTimestamp());
            System.out.println("-------------------------------------------");
        }
    }

    /*
     * 更新表中的某一列
     * 
     * @tableName 表名
     * 
     * @rowKey rowKey
     * 
     * @familyName 列族名
     * 
     * @columnName 列名
     * 
     * @value 更新后的值
     */
    public static void updateTable(String tableName, String rowKey,
            String familyName, String columnName, String value)
            throws IOException {
        HTable table = new HTable(conf, Bytes.toBytes(tableName));
        Put put = new Put(Bytes.toBytes(rowKey));
        put.add(Bytes.toBytes(familyName), Bytes.toBytes(columnName),
                Bytes.toBytes(value));
        table.put(put);
        System.out.println("update table Success!");
    }

    /*
     * 查询某列数据的多个版本
     * 
     * @tableName 表名
     * 
     * @rowKey rowKey
     * 
     * @familyName 列族名
     * 
     * @columnName 列名
     */
    public static void getResultByVersion(String tableName, String rowKey,
            String familyName, String columnName) throws IOException {
        HTable table = new HTable(conf, Bytes.toBytes(tableName));
        Get get = new Get(Bytes.toBytes(rowKey));
        get.addColumn(Bytes.toBytes(familyName), Bytes.toBytes(columnName));
        get.setMaxVersions(5);
        Result result = table.get(get);
        for (KeyValue kv : result.list()) {
            System.out.println("family:" + Bytes.toString(kv.getFamily()));
            System.out
                    .println("qualifier:" + Bytes.toString(kv.getQualifier()));
            System.out.println("value:" + Bytes.toString(kv.getValue()));
            System.out.println("Timestamp:" + kv.getTimestamp());
            System.out.println("-------------------------------------------");
        }
        /*
         * List<?> results = table.get(get).list(); Iterator<?> it =
         * results.iterator(); while (it.hasNext()) {
         * System.out.println(it.next().toString()); }
         */
    }

    /*
     * 删除指定的列
     * 
     * @tableName 表名
     * 
     * @rowKey rowKey
     * 
     * @familyName 列族名
     * 
     * @columnName 列名
     */
    public static void deleteColumn(String tableName, String rowKey,
            String falilyName, String columnName) throws IOException {
        HTable table = new HTable(conf, Bytes.toBytes(tableName));
        Delete deleteColumn = new Delete(Bytes.toBytes(rowKey));
        deleteColumn.deleteColumns(Bytes.toBytes(falilyName),
                Bytes.toBytes(columnName));
        table.delete(deleteColumn);
        System.out.println(falilyName + ":" + columnName + "is deleted!");
    }

    /*
     * 删除指定的列
     * 
     * @tableName 表名
     * 
     * @rowKey rowKey
     */
    public static void deleteAllColumn(String tableName, String rowKey)
            throws IOException {
        HTable table = new HTable(conf, Bytes.toBytes(tableName));
        Delete deleteAll = new Delete(Bytes.toBytes(rowKey));
        table.delete(deleteAll);
        System.out.println("all columns are deleted!");
    }

    /*
     * 删除表
     * 
     * @tableName 表名
     */
    public static void deleteTable(String tableName) throws IOException {
        HBaseAdmin admin = new HBaseAdmin(conf);
        admin.disableTable(tableName);
        admin.deleteTable(tableName);
        System.out.println(tableName + "is deleted!");
    }

    public static void main(String[] args) throws Exception {

        SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd");
        String now_date = df.format(new Date());

        // 创建表
        String tableName[] = {"rsj_member"};
        String[][] family = {
                             {"info","login","index","flg","yw_sn","start_date","end_date","member",
                                "post","subject","dlt_time","dlt_rate","sn","message","col","col_member","col_message"}
                            };
        int i = 0;
        String s;
        for (String tn : tableName) {
            s = ">>> Create Table [ " + tn + " ].";
            for (String fm : family[i]) {
                s += ".( " + fm + " )";
            }
            creatTable(tn, family[i]);
            i += 1;
            //System.out.println(s);
        }
	
        // mysql
        Connection conn = null;
        Connection conn1 = null;
        String sql;

        String url = "jdbc:mysql://master:3306/gyrsj?user=root&password=123456&useUnicode=true&characterEncoding=UTF8";
        try {
            Class.forName("com.mysql.jdbc.Driver");
            //System.out.println("...Loading MySQL Driver OK");
            conn = DriverManager.getConnection(url);
            Statement stmt = conn.createStatement();

            // 添加业务流水 到 “流程”主题库
            //sql = "select member_id,uuid,flg,t_stamp,create_date from member_log";
            sql = "select member_id,uuid,flg,t_stamp,create_date from member_log where create_date>"+now_date;
            ResultSet rs = stmt.executeQuery(sql);

            String memberID;
            String uuid;
            String tableN = "rsj_member";
            String yw_sn;

            while (rs.next()) {
                memberID = rs.getString(1);
                uuid = rs.getString(2);
                addData(memberID,tableN,"index",rs.getString(5)+rs.getString(4),uuid);
                if (rs.getString(3).equals("3")) continue;
                addData(memberID,tableN,"flg",uuid,rs.getString(3));

                // 添加明细
                conn1 = DriverManager.getConnection(url);
                Statement stmt1 = conn1.createStatement();

                if (rs.getString(3).equals("0")){
                    sql = "select yw_sn from sn_log" + " where uuid='" + uuid + "'";
                    ResultSet rs1 = stmt1.executeQuery(sql);
                    if (rs1.next()) {
                        yw_sn = rs1.getString(1);
                        addData( memberID,tableN, "yw_sn",uuid,yw_sn);
                    }
                    sql = "select sn,member,post,subject,start_date,end_date,dlt_time,dlt_rate from wf_log" +
                            " where uuid='" + uuid + "'";
                    //System.out.println(">>> sql:"+sql);
                    rs1 = stmt1.executeQuery(sql);
                    if (rs1.next()) {
                        addData( memberID,tableN, "sn",uuid,rs1.getString(1));
                        addData( memberID,tableN, "member",uuid,rs1.getString(2));
                        addData( memberID,tableN, "post",uuid,rs1.getString(3));
                        addData( memberID,tableN, "subject",uuid,rs1.getString(4));
                        addData( memberID,tableN, "start_date",uuid,rs1.getString(5));
                        addData( memberID,tableN, "end_date",uuid,rs1.getString(6));
                        addData( memberID,tableN, "dlt_time",uuid,rs1.getString(7));
                        addData( memberID,tableN, "dlt_rate",uuid,rs1.getString(8));
                    }
                }

                if (rs.getString(3).equals("1") || rs.getString(3).equals("2")){
                    sql = "select message from warn_log" + " where uuid='" + uuid + "'";
                    //System.out.println(">>> sql:"+sql);
                    ResultSet rs1 = stmt1.executeQuery(sql);
                    while (rs1.next()) {
                        addData( memberID,tableN, "message",uuid,rs1.getString(1));
                    }
                }

            }

            // 添加人与人之间的关联信息
            //sql = "select id,sender_id,receiver_id,message,create_date from col_user_message";
            sql = "select id,sender_id,receiver_id,message,create_date from col_user_message where create_date>"+now_date;
            rs = stmt.executeQuery(sql);

            String id,sender_id,receiver_id,message,create_date;

            while (rs.next()) {

                id = rs.getString(1);
                sender_id = rs.getString(2);
                receiver_id = rs.getString(3);
                message = rs.getString(4);
                create_date = rs.getString(5);

                //System.out.println(">>> +[ "+sender_id+" ].[ "+tableN+" ].[ "+create_date+" ].] "+receiver_id+" ].[ "+message+" ]");

                addData(sender_id,tableN, "col",create_date,id);
                addData(sender_id,tableN, "col_member",id,receiver_id);
                addData(sender_id,tableN, "col_message",id,message);

                addData(receiver_id,tableN, "col",create_date,id);
                addData(receiver_id,tableN, "col_member",id,sender_id);
                addData(receiver_id,tableN, "col_message",id,message);

            }

            // 添加人员登录日志
            //sql = "select member_id,login,logout,ip from login_log";
            sql = "select member_id,login,logout,ip from login_log where login>"+now_date;
            rs = stmt.executeQuery(sql);

            String login,logout,ip_addr;

            while (rs.next()) {

                memberID = rs.getString(1);
                login = rs.getString(2);
                logout = rs.getString(3);
                ip_addr = rs.getString(4);

                addData(memberID,tableN, "login",login,logout+"@"+ip_addr);
            }

        } catch (SQLException e) {
            System.out.println("MySQL op. Error!");
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            conn.close();
            conn1.close();
        }

        // 遍历查询
        //getResultScann("rsj_member", "A","z");
        // 根据row key范围遍历查询
        //getResultScann("blog2", "rowkey4", "rowkey5");

        // 查询
        //getResult("member", "shenwei");
        //getResultWithFamily("member", "shenwei","login");

        // 查询某一列的值
        //getResultByColumn("blog2", "rowkey1", "author", "name");

        // 更新列
        //updateTable("blog2", "rowkey1", "author", "name", "bin");

        // 查询某一列的值
        //getResultByColumn("blog2", "rowkey1", "author", "name");

        // 查询某列的多版本
        //getResultByVersion("blog2", "rowkey1", "author", "name");

        // 删除一列
        //deleteColumn("blog2", "rowkey1", "author", "nickname");

        // 删除所有列
        //deleteAllColumn("blog2", "rowkey1");

        // 删除表
        //deleteTable("blog2");

    }
}


SQL笔记



```sql
insert into test (on_time_stamp) 
	select to_timestamp(on_time,'YYYYMMDDHH24MISS') from test;
insert into test (off_time_stamp) 
	select to_timestamp(off_time,'YYYYMMDDHH24MISS') from test;
```

会添加两倍原有的行，其他字段都是Null



```sql

/*复制表，48秒*/
drop table temp0;
create table temp0 as
	(select * from split_20190301) 

delete from temp0 where
	(on_line=off_line and on_sta_id=off_sta_id)
delete from temp0 where
	cast(substring(off_time from 9 for 2) as integer)>23
/*到此，删去7%记录*/


alter table temp0 add on_time_stamp timestamp without time zone;
alter table temp0 add off_time_stamp timestamp without time zone;

/*update耗时2分钟*/
update temp0 
	set on_time_stamp=to_timestamp(test.on_time,'YYYYMMDDHH24MISS'),
		off_time_stamp=to_timestamp(test.off_time,'YYYYMMDDHH24MISS')

/*添加顺序id,耗时1min*/
ALTER TABLE temp0
    ADD COLUMN serial_id serial 

/*下一次上车时间早于上一次下车时间：1%记录，耗时53s */
delete from temp0 where 
		(serial_id in
		(select temp0.serial_id
			from temp0 inner join (select * from temp0) temp01  
			on temp0.serial_id=temp01.serial_id-1 and temp0.card_id= temp01.card_id and age(temp0.off_time_stamp,temp01.on_time_stamp) > interval '0'
		))
	 or (serial_id in 
		(select temp01.serial_id
			from temp0 inner join (select * from temp0) temp01  
			on temp0.serial_id=temp01.serial_id-1 and temp0.card_id= temp01.card_id and age(temp0.off_time_stamp,temp01.on_time_stamp) > interval '0'
		))
	 


select age(timestamp '2019-03-01 16:10:00', timestamp '2019-03-01 16:20:00') < interval '0'

select test.columns, test2.columns from test inner join (select * from test) test2  
	on test.card_id=test2.card_id and age(test.on_time_stamp,test2.on_time_stamp) < interval '0'

ALTER TABLE public.test
    ADD COLUMN serial_id serial 


select count(*) from
	(select test.serial_id,test.card_id, test.on_sta_name,test.on_time_stamp,test.off_sta_name,test.off_time_stamp,
		test2.serial_id,test2.card_id, test2.on_sta_name,test2.on_time_stamp,test2.off_sta_name,test2.off_time_stamp 
		from test inner join (select * from test) test2  
		on test.serial_id=test2.serial_id-1 and test.card_id= test2.card_id and age(test.off_time_stamp,test2.on_time_stamp) > interval '0'
	 ) time_abnormal
	 
下一次上车时间早于上一次下车时间：481对，1%记录 

```



```sql
SELECT AddGeometryColumn ('test','position',4326,'POINT',2);
alter table test add column on_position geography(POINT,4326);
alter table test add column off_position geography(POINT,4326);

update test set on_position=ST_GeogFromText('SRID=4326;POINT('||on_long||' '||on_lat||')');
update test set off_position=ST_GeogFromText('SRID=4326;POINT('||off_long||' '||off_lat||')');

select test.card_id,test.serial_id,test1.serial_id,test.on_sta_name,test.off_sta_name,test1.on_sta_name,test1.off_sta_name,test.on_time_stamp,
test.off_time_stamp,test1.on_time_stamp,test1.off_time_stamp
from test inner join (select * from test) test1  
			on test.card_id= test1.card_id 
				and age(test1.on_time_stamp,test.off_time_stamp) > interval '0' 
				and age(test1.on_time_stamp,test.off_time_stamp) < interval '30 minutes'
				and (test.serial_id - test1.serial_id)>0
				and ST_distance(test.off_position,test1.on_position)<500


select * from
(
	select test.serial_id,test.card_id,test.on_time_stamp,row_number() over(partition by card_id order by card_id,on_time_stamp) as rn from test 
) ct
where ct.rn>10			

select * ,row_number() over(order by card_id,on_time_stamp) from test where card_id in
(select test.card_id
from test inner join (select * from test) test1  
			on test.card_id= test1.card_id 
				and age(test1.on_time_stamp,test.off_time_stamp) > interval '0' 
				and age(test1.on_time_stamp,test.off_time_stamp) < interval '30 minutes'
				and (test.serial_id - test1.serial_id)>0
				and ST_distance(test.off_position,test1.on_position)<500
)

```



```sql
CREATE TABLE tbl (                                                                        
    col1 int,                                                                             
    col2 int                                                                              
);                                                                                        

INSERT INTO tbl SELECT i/10000, i/100000                                                  
FROM generate_series (1,10000000) s(i);                                                   

ANALYZE tbl;                                     

select * from pg_stats where tablename = 'tbl' and attname = 'col1';
-[ RECORD 1 ]-----------------------------------------------------------
schemaname             | public
tablename              | tbl
attname                | col1
inherited              | f
null_frac              | 0
avg_width              | 4
n_distinct             | 1000
most_common_vals       | {318,564,596,...}
most_common_freqs      | {0.00173333,0.0017,0.00166667,0.00156667,...}
histogram_bounds       | {0,8,20,30,39,...}
correlation            | 1
most_common_elems      | 
most_common_elem_freqs | 
elem_count_histogram   |
```



1.我们要清楚，sql的执行顺序：

from语句->where语句->group by语句->having语句->order by语句->select 语句

2.row_number()分析函数 
说明：返回结果集分区内行的序列号，每个分区的第一行从 1 开始。 
语法：ROW_NUMBER () OVER ([ <partition_by_clause>]<order_by_clause> ) 
备注：ORDERBY 子句可确定在特定分区中为行分配唯一 ROW_NUMBER 的顺序。 
参数：<partition_by_clause> ：将FROM 子句生成的结果集划入应用了 ROW_NUMBER 函数的分区。 
<order_by_clause>：确定将 ROW_NUMBER 值分配给分区中行的顺序。 
返回类型：bigint 。

row_number()从1开始，为每一条分组记录返回一个数字
--------------------- 
作者：安善良民弱女子 
来源：CSDN 
原文：https://blog.csdn.net/u011008029/article/details/49995685 
版权声明：本文为博主原创文章，转载请附上博文链接！

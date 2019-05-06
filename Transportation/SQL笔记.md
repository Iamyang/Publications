SQL笔记



```sql
insert into test (on_time_stamp) 
	select to_timestamp(on_time,'YYYYMMDDHH24MISS') from test;
insert into test (off_time_stamp) 
	select to_timestamp(off_time,'YYYYMMDDHH24MISS') from test;
```

会添加两倍原有的行，其他字段都是Null



```sql
delete from test where
	(on_line=off_line and on_sta_name=off_sta_name) or
	cast(substring(on_time from 9 for 2) as integer)>23 or
	card_id in (select card_id from test group by card_id having count(card_id)>20)


alter table test add on_time_stamp timestamp without time zone;
alter table test add off_time_stamp timestamp without time zone;

update test 
	set on_time_stamp=to_timestamp(test.on_time,'YYYYMMDDHH24MISS'),
		off_time_stamp=to_timestamp(test.off_time,'YYYYMMDDHH24MISS')

select age(timestamp '2019-03-01 16:10:00', timestamp '2019-03-01 16:20:00') < interval '0'

select test.columns, test2.columns from test inner join (select * from test) test2  
	on test.card_id=test2.card_id and age(test.on_time_stamp,test2.on_time_stamp) < interval '0'

	
```


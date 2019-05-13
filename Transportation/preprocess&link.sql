/*复制表*/
drop table if exists test;
create table test as table sample_20190301;

delete from test where
	(on_line=off_line and on_sta_id=off_sta_id);
delete from test where
	cast(substring(off_time from 9 for 2) as integer)>23;
/*到此，删去7%记录*/

/*添加类型为日期的新列*/
alter table test add on_time_stamp timestamp without time zone;
alter table test add off_time_stamp timestamp without time zone;
update test 
	set on_time_stamp=to_timestamp(test.on_time,'YYYYMMDDHH24MISS'),
		off_time_stamp=to_timestamp(test.off_time,'YYYYMMDDHH24MISS');

/*添加坐标点为geography类型的新列*/
alter table test add column on_position geography(POINT,4326);
alter table test add column off_position geography(POINT,4326);
update test set on_position=ST_GeogFromText('SRID=4326;POINT('||on_long||' '||on_lat||')');
update test set off_position=ST_GeogFromText('SRID=4326;POINT('||off_long||' '||off_lat||')');

/*添加为每个卡记录计数的新列*/
alter table test add column row_num bigint;
update test 
	set row_num= t1.row_num
	from (select card_id,on_time_stamp, row_number() over(partition by card_id order by on_time_stamp)  row_num from test) t1
	where test.card_id=t1.card_id and test.on_time_stamp=t1.on_time_stamp;

/*删除（1）下一次上车时间与上一次下车时间间隔小于1秒 （2）下一次上车时间与上一次下车时间间隔小于30分钟且速度大于60km/h：2%记录*/
delete from test 
using (select test.card_id,test.row_num as r1,test1.row_num as r2
			from test inner join (select * from test) test1  
			on test.card_id= test1.card_id 
	   			and test.row_num=test1.row_num-1  
	   			and (age(test1.on_time_stamp,test.off_time_stamp) <= interval '1 seconds' 
					 or ( age(test1.on_time_stamp,test.off_time_stamp) < interval '30 minutes'
						 and ST_distance(test.off_position,test1.on_position)/1000
							/ (extract(hour from age(test1.on_time_stamp,test.off_time_stamp))
							   +extract(minute from age(test1.on_time_stamp,test.off_time_stamp))/60
							   +extract(second from age(test1.on_time_stamp,test.off_time_stamp))/3600)
							>=60
					 	)
					)
		)t1		
where test.card_id=t1.card_id and (test.row_num=t1.r1 or test.row_num=t1.r2);

/*更新计数*/
update test 
	set row_num= t1.row_num
	from (select card_id,on_time_stamp, row_number() over(partition by card_id order by on_time_stamp)  row_num from test) t1
	where test.card_id=t1.card_id and test.on_time_stamp=t1.on_time_stamp;

 
drop table if exists link_temp;
create table link_temp as
(select test.card_id,test.row_num as r1,test1.row_num as r2,row_number()over(partition by test.card_id order by test.row_num) as row_num
			from test join (select * from test) test1  
			on test.card_id= test1.card_id 
	   			and test.row_num=test1.row_num-1  
	   			and age(test1.on_time_stamp,test.off_time_stamp) < interval '30 minutes'
				and ST_distance(test.off_position,test1.on_position)<=300
 );

drop table if exists link_temp2;
create table link_temp2 as
(select card_id,min(r1) as start_row,max(r2) as end_row from link_temp group by card_id, r1-row_num
);

update test
set (off_mode,off_line,off_dir,off_sta_id,off_sta_name,off_long,off_lat,off_time,off_time_stamp,off_position)=
		(t1.off_mode,t1.off_line,t1.off_dir,t1.off_sta_id,t1.off_sta_name,t1.off_long,t1.off_lat,
		 t1.off_time,t1.off_time_stamp,t1.off_position)
from (select test.card_id,test.row_num,test1.off_mode,test1.off_line,test1.off_dir,test1.off_sta_id,test1.off_sta_name,test1.off_long,test1.off_lat,
		 test1.off_time,test1.off_time_stamp,test1.off_position
	from test inner join link_temp2 on test.card_id=link_temp2.card_id and test.row_num=link_temp2.start_row
	inner join (select * from test)test1 on test1.card_id=link_temp2.card_id and test1.row_num=link_temp2.end_row
 	) t1
where test.card_id=t1.card_id and test.row_num=t1.row_num;



delete from test
using link_temp2
where test.card_id=link_temp2.card_id and (test.row_num>link_temp2.start_row and test.row_num<=link_temp2.end_row);


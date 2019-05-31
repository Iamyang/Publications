/*
	本代码实现：数据清洗和一个统计
	数据输入：初始刷卡数据sample_20190301
	数据输出：清洗后的数据cleaned_basic
	整体上：从原表sample_20190301复制到新表cleaned_basic，在cleaned_basic上进行操作。清洗后的结果仍在cleaned_basic中。
			后续的统计和换乘合并将在cleaned_basic基础上进行
	数据清洗：
		共有四种异常数据：
			（1）上下车点一样的记录
			（2）下车时间超过24点
			（3）下一次上车时间与上一次下车时间间隔过短以至于不可能发生换车，此处取为1秒
			（4）下一次上车与上一次下车时间间隔较短但两个站点距离间隔很大以至于不可能发生换车，
				此处取换车时间间隔30分钟内，速度大于60km/h。
		为了辅助清洗，添加了5个新字段，这5个字段在之后的处理中仍然有用：
			上下车时间为日期类型的字段
			上下车点为postgis geography类型的字段
			为每个人乘车次数计数的字段
		清洗结束后，约有11%的记录被删去
	一个统计：
		统计同一个人连续两次乘车时下一次上车与上一次下车的时间差，并输出到csv
		
*/



/*------------------------------数据清洗----------------------------*/
/*保留上下车点不一样的记录，判断规则：上下车线路号不同或线路号相同而站点编号不同*/
/*保留下车时间不超过24点的记录，判断规则：小时字段<=24*/
/*添加上下车时间类型为日期的新列 f_tm_stamp,t_tm_stamp，原来的时间为字符串，不方便使用*/
/*添加上下车点为geography类型的新列 f_position,t_position，方便后续计算距离*/
drop table if exists cleaned_temp;
create table cleaned_temp 
as	(
		select	sample_20190301.*
				,to_timestamp(f_tm,'YYYYMMDDHH24MISS') as f_tm_stamp
				,to_timestamp(t_tm,'YYYYMMDDHH24MISS') as t_tm_stamp
				,ST_GeogFromText('SRID=4326;POINT('||f_lon||' '||f_lat||')')::geography as f_position
				,ST_GeogFromText('SRID=4326;POINT('||t_lon||' '||t_lat||')')::geography as t_position
		from	sample_20190301
		where	cast(substring(t_tm from 9 for 2) as integer)<24
		and		(	f_line!=t_line
				or	(f_line=t_line and fst_num!=tst_num)
				)
			
	)
;

/*添加每个人乘车次数计数的新列row_num，例如：一个人共有5次乘车，则五条记录的row_num为1 2 3 4 5，排序规则是上车时间由早到晚*/
drop table if exists cleaned_temp1;
create table cleaned_temp1 
as	(
		select	cleaned_temp.*
				,row_number() over(partition by card_id order by f_tm_stamp) as row_num
		from	cleaned_temp
	)
;

--删去临时表
drop table if exists cleaned_temp;

/*删除异常记录
（1）下一次上车时间与上一次下车时间间隔小于1秒 
（2）下一次上车时间与上一次下车时间间隔小于30分钟且速度大于60km/h：2%记录
*/
delete from cleaned_temp1
using	(
			select t1.card_id,t1.row_num as r1,t2.row_num as r2
			from cleaned_temp1	as t1
			inner join (select * from cleaned_temp1) t2  
			on t1.card_id= t2.card_id 
			and t1.row_num=t2.row_num-1  
			and (age(t2.f_tm_stamp,t1.t_tm_stamp) <= interval '1 seconds' 
				or (age(t2.f_tm_stamp,t1.t_tm_stamp) < interval '30 minutes'
					and ST_distance(t1.t_position,t2.f_position)/1000/
							(	extract(hour from age(t2.f_tm_stamp,t1.t_tm_stamp))
							   +extract(minute from age(t2.f_tm_stamp,t1.t_tm_stamp))/60
							   +extract(second from age(t2.f_tm_stamp,t1.t_tm_stamp))/3600   
							)
						>=60
					)
				)
		)abnormal
where	cleaned_temp1.card_id=abnormal.card_id 
and 	(cleaned_temp1.row_num=abnormal.r1 or cleaned_temp1.row_num=abnormal.r2)
;

alter table cleaned_temp1 drop column row_num;

--最终表格cleaned_20190301
drop table if exists cleaned_20190301;
create table cleaned_20190301
as		(
			select	cleaned_temp1.*
					,row_number() over(partition by card_id order by f_tm_stamp) as row_num
			from	cleaned_temp1
		)
;

--删去临时表
drop table if exists cleaned_temp1;

/*------------------------------数据清洗结束----------------------------*/	

/*---------------------一个统计-----------------------------*/
/*统计同一个人连续两次乘车下一次上车与上一次下车的时间差（未合并换乘）,并输出到csv*/
copy (
	select (extract(hour from interval_)+extract(minute from interval_)/60+extract(second from age(cleaned_basic1.f_tm_stamp,cleaned_basic.t_tm_stamp))/3600) as interval_daily
from (select age(cleaned_basic1.f_tm_stamp,cleaned_basic.t_tm_stamp) as interval_ 
		from cleaned_basic inner join (select * from cleaned_basic) cleaned_basic1  
					on cleaned_basic.card_id= cleaned_basic1.card_id 
						and cleaned_basic.row_num=cleaned_basic1.row_num-1
		) t1
)
to 'D:/Data/Sample/interval_without_link.csv' (format csv, delimiter ',');



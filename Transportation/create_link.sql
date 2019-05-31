/*
	本代码实现：换乘合并
	数据输入：清洗后的乘车记录cleaned_basic
	数据输出：合并后换乘的记录link_result. 后续计算基于link_result
	经统计，约有10%的记录被合并
	
	判断换乘的基本规则：时间间隔小于30分钟，距离间隔小于300m
	具体思路：
		以一个人的乘车记录为例：
			上车点 下车点 记录编号row_num（编号按照上车时间由早到晚排列）
			a 		b		1
			b 		c		2
			c 		d		3
			e 		f		4
				
		（1）首先找到两两换乘的记录：按照时间将每条记录与下一条记录做连接，若满足换乘规则，则存储其行号到link_count中
			对于例子得到2条记录：
			1 2
			2 3
		（2）换乘可能存在多次，需要找到换乘的起点和终点，基于link_count，结果存储到link_count2中
			对于例子得到1条记录：
			start_row end_row
			1 		  3
		（3）取乘车记录中行号为起点编号的起点信息，行号为终点编号的终点信息，得到换乘合并后的记录，存储到link_temp中
			对于例子得到1条记录：
			a	d
		（4）除去换乘记录，有些记录为发生换乘，筛选出来存储到 link_temp2中
			对于例子得到1条记录：
			e	f
		（5）合并换乘出行link_temp和非换乘出行link_temp2，得到完整的出行记录，存储到link_result
			对于例子得到2条记录：
			a	d
			e	f
		（6）删除临时表link_count，link_count2，link_temp，link_temp2
*/

/*创建临时表，仅存储前后两次换乘出行记录的行号。判断换乘规则：时间间隔小于30分钟，距离间隔小于300m*/ 
drop table if exists link_count;
create table link_count as
(select cleaned_basic.card_id,cleaned_basic.row_num as r1,cleaned_basic1.row_num as r2,row_number()over(partition by cleaned_basic.card_id order by cleaned_basic.row_num) as row_num
			from cleaned_basic join (select * from cleaned_basic) cleaned_basic1  
			on cleaned_basic.card_id= cleaned_basic1.card_id 
	   			and cleaned_basic.row_num=cleaned_basic1.row_num-1  
	   			and age(cleaned_basic1.f_tm_stamp,cleaned_basic.t_tm_stamp) < interval '30 minutes'
				and ST_distance(cleaned_basic.t_position,cleaned_basic1.f_position)<=300
 );
 
/*创建临时表，存储换乘的起始行号*/ 
drop table if exists link_count2;
create table link_count2 as
(select card_id,min(r1) as start_row,max(r2) as end_row from link_count group by card_id, r1-row_num);

/*创建临时表，存储换乘出行的合并后的出行记录*/ 
drop table if exists link_temp;
create table link_temp as
(select cleaned_basic.card_id,cleaned_basic.f_mode,cleaned_basic.f_line,cleaned_basic.f_dir,cleaned_basic.fst_num,cleaned_basic.fst_name,cleaned_basic.f_lon,cleaned_basic.f_lat,cleaned_basic.f_tm,
		cleaned_basic1.t_mode,cleaned_basic1.t_line,cleaned_basic1.t_dir,cleaned_basic1.tst_num,cleaned_basic1.tst_name,cleaned_basic1.t_lon,cleaned_basic1.t_lat,cleaned_basic1.t_tm,cleaned_basic.f_tm_stamp,cleaned_basic1.t_tm_stamp,cleaned_basic.f_position,cleaned_basic1.t_position,cleaned_basic.row_num
		from cleaned_basic inner join link_count2 on cleaned_basic.card_id=link_count2.card_id and cleaned_basic.row_num=link_count2.start_row
		inner join (select * from cleaned_basic)cleaned_basic1 on cleaned_basic1.card_id=link_count2.card_id and cleaned_basic1.row_num=link_count2.end_row
);

/*创建临时表，存储非换乘出行的出行记录*/ 
drop table if exists link_temp2;
create table link_temp2 as
(select cleaned_basic.* from cleaned_basic
	except 
	select cleaned_basic.* from cleaned_basic join link_count2 
		on cleaned_basic.card_id=link_count2.card_id 
			and (cleaned_basic.row_num>=link_count2.start_row and cleaned_basic.row_num<=link_count2.end_row)
);

--合并换乘出行和非换乘出行的记录，存储到新表link_result中
drop table if exists link_result;
create table link_result as
(select link_temp.* from link_temp
	union all 
	select link_temp2.* from link_temp2
);


/*删除临时表*/
drop table if exists link_count;
drop table if exists link_count2;
drop table if exists link_temp;
drop table if exists link_temp2;
/*----------------------换乘合并结束------------------------*/

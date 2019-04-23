# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 15:36:00 2019

@author: Liu Yang
"""
import time
import os
#import datetime as dt
import csv
len_record=16
def process_record(record):
    record[1]=record[1][-2:]# change'\tDT' or '&DT' to 'DT'
    if len(record[-1])==15:
        record[-1]=record[-1][:-1]#delete '\n' in the end of time 
    return record
def judge_same_onoff(record):
    same_onoff=0
    if record[2]==record[10] and record[3]==record[11] and record[4]==record[12]:
        same_onoff=1
    return same_onoff
def split_line(line):
    splits=line.split(',')
    card_id=splits[0]
    splits=splits[1:]
    n_records=int(len(splits)/len_record)
    records=[]
    for i in range(n_records):
        record=splits[i*len_record:(i+1)*len_record]
        record=[card_id]+record
        record=process_record(record)
        records.append(record)
    return records
def split_link(file_path):
    n_lines=100000#每次读100,000行
    processed_lines=[]
#    count=0
    with open(file_path,'r',encoding='UTF-8') as file:# reading time is about 9sec
        while True:
            lines=file.readlines(n_lines)
            if not lines:
                break
            for line in lines:
                records=split_line(line)
                processed_lines+=records
    return processed_lines
def compute_statistics(records):
    person_trips={}
    person_abtrips={}#异常记录：上下车点一样
    for record in records:
        card_id=record[0]
        if card_id in person_trips:
            person_trips[card_id]+=1
            person_abtrips[card_id]+=judge_same_onoff(record)
        else:
            person_trips[card_id]=1
            person_abtrips[card_id]=judge_same_onoff(record)
    return person_trips,person_abtrips

if __name__ == '__main__':
#    all_records=[]
    read_path = "D:/Data/Card_data" #文件夹目录
    files= os.listdir(read_path) #得到文件夹下的所有文件名称
    write_path="D:/Data/splitted_card_data"
    
    for file in files: #遍历文件夹
        print(time.ctime(),file,'start')
        file_path=read_path+"/"+file
        records=split_link(file_path)#分割好的记录
        with open(write_path+'/splitted_'+file[2:]+'.csv','w',newline='',encoding='UTF-8') as f:
            writer=csv.writer(f)
            writer.writerows(records)
        records=[]
        
#        all_records.append(records) #存储所有文件的记录

#    start=time.time()
#    records=split_link(r'D:\Data\Card_data\LK20190301') 
#    print('Process time:',time.time()-start)
    
#    with open(r'D:\Data\splitted_card_data\splitted_20190301.csv','w',newline='',encoding='UTF-8') as file:
#        writer=csv.writer(file)
#        writer.writerows(records)
#        
#    with open(r'D:\Data\splitted_card_data\splitted_20190301.csv','r') as file:# reading time is about 9sec       
#        temp=file.readlines(1000)
#        
      
#        
#        

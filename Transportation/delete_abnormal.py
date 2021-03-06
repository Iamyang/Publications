# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 14:04:27 2019

@author: wb-yl519673
"""

import time
import numpy as np
import pandas as pd
import os
import csv
def read_records(file_path):
    records = pd.read_csv(file_path, header=None)
    column_name = ['card_id', 'on_mode', 'on_line', 'on_dir', 'on_sta_id', 'on_sta_name', \
                   'on_long', 'on_lat', 'on_time', 'off_mode', 'off_line', 'off_dir', 'off_sta_id', \
                   'off_sta_name', 'off_long', 'off_lat', 'off_time']
    records.columns = column_name

    return records

def delete_abnormal(records):
    same_onoff = records[records.on_sta_id == records.off_sta_id]
    records.drop(same_onoff.index, axis='index', inplace=True)  # 删除上下车点一样的记录

    time_abn = records[records.off_time % 1000000 > 235959]
    records.drop(time_abn.index, axis='index', inplace=True)  # 删除时间超过23:59:59的记录

    max_record = 20  # 经检查，一天中超过20的有7人，再结合常识，判定日记录数超过20为异常。
    card_id = records.card_id.value_counts()
    abnormal_card = card_id[(card_id >= max_record)]
    records = records[~ records.card_id.isin(abnormal_card.index)]

    records['on_time'] = pd.to_datetime(records.on_time, format='%Y%m%d%H%M%S')
    records['off_time'] = pd.to_datetime(records.off_time, format='%Y%m%d%H%M%S')

    return records
def delete_timeab(records):
    abnormal=[]
    current=records['card_id'][0]
    for i in range(1,len(records)):
        if records['card_id'][i]==current:
            if records['on_time'][i]<records['off_time'][i-1]:
              abnormal.append(i)  
        else:
            current=records.card_id[i]
    records.drop(abnormal,axis='index',inplace=True)
    
if __name__ == '__main__':


#    read_path = "D:/Data/split_card_data_201903/"  # 文件夹目录
#    files = os.listdir(read_path)  # 得到文件夹下的所有文件名称
    write_path = "D:/Data/normal_card_data_201903/"
    files = os.listdir(write_path)  # 得到文件夹下的所有文件名称
    
    for file in files:  # 遍历文件夹
        print(time.ctime(), file, 'start')
        file_path = write_path + file
#        records = read_records(file_path)  # 分割好的记录
#        records = delete_abnormal(records)
        records=pd.read_csv(file_path,index_col=False)
        records=delete_timeab(records)
        
        records.to_csv(file_path,index=False)
        records = []



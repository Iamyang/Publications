# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 09:11:44 2019

@author: Liu Yang
"""
import time
import numpy as np
import pandas as pd
R=6371004#unit:meter
dist_thre=200#unit:meter
time_thre=1200#unit:second
    
def distance_latlong(lat1,long1,lat2,long2):
    '''Compute the euclidean distance between two points in GPS coordinates '''
    lat1=np.radians(lat1)
    lat2=np.radians(lat2)
    long1=np.radians(long1)
    long2=np.radians(long2)
    rad=np.sin(lat1)*np.sin(lat2)+np.cos(lat1)*np.cos(lat2)*np.cos(long1-long2)
    if rad>1 or rad<-1:
        rad=1
    elif rad<-1:
        rad=-1
#        print(rad,lat1,long1,lat2,long2)
#        raise Exception('invalid rad')
    
    distance=R*np.arccos(rad)
    return distance
def read_records(file_path):
    records=pd.read_csv(file_path,header=None)
    column_name=['card_id','on_mode','on_line','on_dir','on_sta_id','on_sta_name',\
                 'on_long','on_lat','on_time','off_mode','off_line','off_dir','off_sta_id',\
                 'off_sta_name','off_long','off_lat','off_time']
    records.columns=column_name
    
    return records
def delete_abnormal(records):
    same_onoff=records[records.on_sta_id==records.off_sta_id]
    records.drop(same_onoff.index,axis='index',inplace=True)#删除上下车点一样的记录
    
    time_abn=records[records.off_time%1000000>235959]
    records.drop(time_abn.index,axis='index',inplace=True)
    
    max_record=20#日记录数超过20认为异常
    card_id=records.card_id.value_counts()
    abnormal_card=card_id[(card_id>=max_record)]
    records=records[~ records.card_id.isin(abnormal_card.index)]
    
    records['on_time']=pd.to_datetime(records.on_time,format='%Y%m%d%H%M%S')
    records['off_time']=pd.to_datetime(records.off_time,format='%Y%m%d%H%M%S')
    
    return records
def link(records):
    card_id=records.card_id.value_counts()
    records_2=records[records.card_id.isin(card_id[card_id>=2].index)]
    
    drop=[]
    for cid,cgroup in records_2.groupby('card_id'):
        n_records=len(cgroup)
        index=cgroup.index
        i=0
        while i<n_records-1:
            k=i
            while i<n_records-1:
                dist=distance_latlong(cgroup.off_lat[index[i]],cgroup.off_long[index[i]],\
                                      cgroup.on_lat[index[i+1]],cgroup.on_long[index[i+1]])
                interval=(cgroup.on_time[index[i+1]]-cgroup.off_time[index[i]]).total_seconds()
                if dist<dist_thre and interval<time_thre:
                    records.loc[index[k],'off_mode':'off_time']=records.loc[index[i+1],'off_mode':'off_time']
                    drop.append(index[i+1])
                    i+=1
                else:
                    i+=1
                    break
    return records
if __name__ == '__main__':
    file_path=r'D:\Data\splitted_card_data_201903\splitted_20190301.csv'
    records=read_records(file_path)
    
    print('Reading finished',time.ctime())
    records=delete_abnormal(records)
    print('Deleting abnormal records finished',time.ctime())
#    links=link(records.copy())
    card_id=records.card_id.value_counts()
    records_2=records[records.card_id.isin(card_id[card_id>=2].index)]
    
    drop=[]
    for cid,cgroup in records_2.groupby('card_id'):
        n_records=len(cgroup)
        index=cgroup.index
        i=0
        while i<n_records-1:
            k=i
            while i<n_records-1:
                dist=distance_latlong(cgroup.off_lat[index[i]],cgroup.off_long[index[i]],\
                                      cgroup.on_lat[index[i+1]],cgroup.on_long[index[i+1]])
                interval=(cgroup.on_time[index[i+1]]-cgroup.off_time[index[i]]).total_seconds()
                if dist<dist_thre and interval<time_thre:
                    records.loc[index[k],'off_mode':'off_time']=records.loc[index[i+1],'off_mode':'off_time']
                    drop.append(index[i+1])
                    i+=1
                else:
                    i+=1
                    break
    

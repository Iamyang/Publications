# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 14:55:27 2019

@author: wb-yl519673
"""

import time
import numpy as np
import pandas as pd
import os
import csv
R = 6371004  # unit:meter
dist_thre = 200  # unit:meter
time_thre = 1200  # unit:second


def distance_latlong(lat1, long1, lat2, long2):
    '''Compute the euclidean distance between two points in GPS coordinates '''
    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)
    long1 = np.radians(long1)
    long2 = np.radians(long2)
    rad = np.sin(lat1) * np.sin(lat2) + np.cos(lat1) * np.cos(lat2) * np.cos(long1 - long2)
    if rad > 1 or rad < -1:
        rad = 1
    elif rad < -1:
        rad = -1
    #        print(rad,lat1,long1,lat2,long2)
    #        raise Exception('invalid rad')

    distance = R * np.arccos(rad)
    return distance


if __name__ == '__main__':
    file_path = "D:/Data/normal_card_data_201903/20190301.csv"
    records=pd.read_csv(file_path)
    records['off_time']=pd.to_datetime(records['off_time'])
    records['on_time']=pd.to_datetime(records['on_time'])
    
    interval_all=[]
    current=records['card_id'][0]
    for i in range(1,len(records)):
        if records['card_id'][i]==current:
            dist=distance_latlong(records['off_lat'][i-1],records['off_long'][i-1],records['on_lat'][i],records['on_long'][i])
            if dist<dist_thre:
                interval = (records['on_time'][i] - records['off_time'][i-1]).total_seconds()
                interval_all.append(interval)
        else:
            current=records.card_id[i]
    
    abnormal=[]
    current=records['card_id'][0]
    for i in range(1,len(records)):
        if records['card_id'][i]==current:
            if records['on_time'][i]<records['off_time'][i-1]:
              abnormal.append(i)  
        else:
            current=records.card_id[i]
            
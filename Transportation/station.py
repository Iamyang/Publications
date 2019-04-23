# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 11:27:56 2019

@author: Liu Yang
"""

import numpy as np
import pandas as pd
import os
R=6371004#unit:meter
def distance_latlong(lat1,long1,lat2,long2):
    '''Compute the euclidean distance between two points in GPS coordinates '''
    lat1=np.radians(lat1)
    lat2=np.radians(lat2)
    long1=np.radians(long1)
    long2=np.radians(long2)
    rad=np.sin(lat1)*np.sin(lat2)+np.cos(lat1)*np.cos(lat2)*np.cos(long1-long2)
    distance=R*np.arccos(rad)
    return distance

if __name__ == '__main__':
    path='D:/Data/StationBasic_SRC'
    files= os.listdir(path) #得到文件夹下的所有文件名称
    all_records=[]
    for file in files:
        with open(path+'/'+file,'r') as f:# reading time is about 9sec       
            records=f.readlines() 
            for row in records:
                row=row.split(',')
                if len(row)==1:
                    continue
                elif len(row)==7:
                    row=row[:-1]
                elif len(row)==8:
                    row=row[:-2]
                all_records.append(row)
    df=pd.DataFrame(all_records,columns=['line_id','line_dir','sta_id','sta_name','long','lat'])            
    df=df.astype({'long':'float','lat':'float','line_dir':'int','sta_id':'int'})
    
    df.to_csv('D:/Data/stations_all.csv')
    
#    sta_name_count=df.sta_name.value_counts()
#        
#    sta_name_all=[]
#    temp=[]
#    for lid,lgroup in df.groupby('sta_name'):
#        if len(lgroup)==1:
#            continue
#        if lgroup.long.std()>1e-4 or lgroup.lat.std()>1e-4:
#            temp.append(lid)
#        
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 16:30:15 2019

@author: wb-yl519673
"""
import time
import pandas as pd
import os
if __name__ == '__main__':
    station=['北京站','北京南站','北京西站','西直门','西直门南','西直门外','丰台火车站']
    
    read_path = "D:/Data/normal_card_data_201903/"  # 文件夹目录
    files = os.listdir(read_path)  # 得到文件夹下的所有文件名称
    write_path = "D:/Data/forGao/"

    for file in files:  # 遍历文件夹
        print(time.ctime(), file, 'start')
        file_path = read_path + file
        records = pd.read_csv(file_path)  # 分割好的记录
        selected=records[(records.off_sta_name.isin(station)) | (records.on_sta_name.isin(station))]
        selected.to_csv(write_path+file,index=False)
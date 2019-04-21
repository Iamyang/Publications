# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 10:36:43 2019

@author: Liu Yang
"""

import numpy as np
R=6371.004#metric:km
def distance_latlong(lat1,long1,lat2,long2):
    '''Compute the euclidean distance between two points in GPS coordinates '''
    lat1=np.radians(lat1)
    lat2=np.radians(lat2)
    long1=np.radians(long1)
    long2=np.radians(long2)
    rad=np.sin(lat1)*np.sin(lat2)+np.cos(lat1)*np.cos(lat2)*np.cos(long1-long2)
    distance=R*np.arccos(rad)
    return distance


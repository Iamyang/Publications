# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 11:11:06 2019

@author: wb-yl519673
"""

import os
os.environ['JAVA_HOME']=r'C:\Program Files\Java\jdk-12.0.1'
os.environ['PYTHONPATH']=r'D:\spark-2.4.1-bin-hadoop2.7\python'

from pyspark import SparkContext
logfile='D:/spark-2.4.1-bin-hadoop2.7/README.md'
sc=SparkContext('local','First app')
logData=sc.textFile(logfile).cache()
numAs = logData.filter(lambda s: 'a' in s).count()
numBs = logData.filter(lambda s: 'b' in s).count()

#-------------------------------------------------------------------------------
# Name:        濠电姷鏁告慨鐑姐€傞挊澹╋綁宕ㄩ弶鎴濈€銈呯箰閻楀棝鎮為崹顐犱簻闁圭儤鍨甸弳鐐烘煟濠垫劒閭柡?
# Purpose:
#
# Author:      lenovo
#
# Created:     03/07/2017
# Copyright:   (c) lenovo 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import numpy as np
import pickle
from cairo import *
from igraph import *
def readPickle(fname):
    file=open(fname,'rb')
    pkl=pickle.load(file)
    file.close()
    return pkl
def main():
    fdir="E:/Senior/Graduation project/YahooFlickr/NewYorktemp/Motifs/Motif_interval"
    os.chdir(fdir)
##    refmatcount=readPickle("refmatcount.pkl")
##    moid=list(refmatcount.keys())
    refmatrix=readPickle("refmatrix.pkl")
    lmat=len(refmatrix)
    node_names=[str(i) for i in range(1,31)]
    for i in range(lmat):
        keys=list(refmatrix[i].keys())
        keys.sort(key=operator.itemgetter(0,1))
        values=list(map(refmatrix[i].get,keys))
        adjmat=np.array(values).reshape((30,30))
        g=Graph.Adjacency((adjmat > 0).tolist())
        g.es['weight'] = adjmat[adjmat.nonzero()]
        g.vs['label'] = node_names
        g.es['width'] = g.es['weight']
        plot(g, str(i)+'.png',layout='fr', labels=True, margin=20)



if __name__ == '__main__':
    main()

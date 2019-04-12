#-------------------------------------------------------------------------------
# Name:        Motifs
# Purpose:     Mining motifs from the whole network
#
# Author:      Liu Yang
#
# Created:     20/03/2017
# Copyright:   (c) lenovo 2017
# Licence:     <your licence>
#-----------------Readme---------------
#the number of nodes of motifs refered to
#the number of networks regarded as motifs
#indegree of motifs
#outdegree of motifs
#adjacency matrix of motifs
#threshold to judge if a network is a motif
#the number of trips which has certain numbers of nodes
#    global refcountnumnodes,refnumnetworks,refindegree,refoutdegree,refmatrix,refmatcount,thre
#    global counthnumnodes,countnumnodes,thre,number
##Input:TrajSingleClean: each file is a user's trip with a list of records.
##each record is (location ID,latitude,longitude,year,month,day,hour,minute,second)
#-------------------------------------------------------------------------------
import time
import os
import pickle
import numpy as np
ind_combination=[]
sitenumber=30#there are total 30 attractions
snadd1=sitenumber+1#for the convenience of range function
meta=[0 for i in range(snadd1)]

thre=round(0.02*2622)
thre_sub_node_num=8
thre_motif_node_num=8
thre_node_num=20

refnumnetworks=0
refcountnumnodes=[]
refoutdegree=[]
refindegree=[]
refmatrix=[]
refmatcount={}

cpgoon=True
v={}
tempcount=0
def permute(start,ehnumnodes,outdegree,indegree,newmatrix,oldmatrix):
    global cpgoon,v,tempcount
    if start==ehnumnodes and cpgoon==True:
        compare(ehnumnodes,newmatrix,oldmatrix)
    else:
        for i in range(start,ehnumnodes+1):
            if cpgoon==False:
                break
            else:
                if outdegree[v[i]]==outdegree[v[start]] and indegree[v[i]]==indegree[v[start]]:
                    v[i],v[start]=v[start],v[i]
                    permute(start+1,ehnumnodes,outdegree,indegree,newmatrix,oldmatrix)
                    v[i],v[start]=v[start],v[i]
def compare(ehnumnodes,newmatrix,oldmatrix):
    global cpgoon
    cpgoon=False
    for i in range(1,ehnumnodes+1):
        if cpgoon==True:
            break
        for j in range(1,ehnumnodes+1):
            if oldmatrix[(i,j)]!=newmatrix[(v[i],v[j])]:
                cpgoon=True
                break

#'locations' is a list that denotes the trajectory
#cout:outdegree,cin:indegree,cmatrix:adjacency matrix
def getNetwork(locations):
    cout={}
    cin={}
    cmatrix={}
    ehnumnodes=0
    enumnodes=len(locations)
    hlocations=[]
    for i in range(1,snadd1):
        cout[i]=0
        cin[i]=0
        for j in range(1,snadd1):
            cmatrix[(i,j)]=0
    for i in range(enumnodes):
        if locations[i] not in hlocations:
            hlocations.append(locations[i])
    for i in range(1,enumnodes):
        cout[locations[i-1]]+=1
        cin[locations[i]]+=1
        cmatrix[(locations[i-1],locations[i])]+=1
    return cout,cin,cmatrix,hlocations

def orderNetwork(outdegree,indegree,adjmatrix,ehnumnodes):
    maxout=0
    maxin=0
    maxid=0
    for i in range(1,snadd1):
        if i>ehnumnodes:
            break
        maxout=outdegree[i]
        maxin=indegree[i]
        maxid=i
        for j in range(i+1,snadd1):
            if outdegree[j]>maxout:
                maxout=outdegree[j]
                maxin=indegree[j]
                maxid=j
            elif outdegree[j]==maxout:
                if indegree[j]>maxin:
                    maxout=outdegree[j]
                    maxin=indegree[j]
                    maxid=j
            else:
                pass
        if i!=maxid:
            outdegree[i],outdegree[maxid]=outdegree[maxid],outdegree[i]
            indegree[i],indegree[maxid]=indegree[maxid],indegree[i]
            for j in range(1,snadd1):
                if j==i:
                    adjmatrix[(i,i)],adjmatrix[(maxid,maxid)]=adjmatrix[(maxid,maxid)],adjmatrix[(i,i)]
                elif j==maxid:
                    adjmatrix[(i,maxid)],adjmatrix[(maxid,i)]=adjmatrix[(maxid,i)],adjmatrix[(i,maxid)]
                else:
                    adjmatrix[(i,j)],adjmatrix[(maxid,j)]=adjmatrix[(maxid,j)],adjmatrix[(i,j)]
                    adjmatrix[(j,i)],adjmatrix[(j,maxid)]=adjmatrix[(j,maxid)],adjmatrix[(j,i)]

    return outdegree,indegree,adjmatrix

def straj2loca(straj):
    locations=[]
    length=len(straj)
    locations.append(int(straj[0][0]))
    #if ith location==(i+1)th location,only save once.
    for i in range(1,length):
        if straj[i][0]==straj[i-1][0]:
            continue
        else:
            locations.append(int(straj[i][0]))
    return locations

def judgeMotifNew(ehnumnodes,outdegree,indegree,ematrix):
#judging if the motif is new
    global cpgoon,v
    notexist=True
    index=-1
    for i in range(refnumnetworks):
        if notexist==False:
            break
        if refcountnumnodes[i]!=ehnumnodes:
            continue
        flagdegree=True
        for j in range(1,ehnumnodes+1):
            if outdegree[j]!=refoutdegree[i][j] or indegree[j]!=refindegree[i][j]:
                flagdegree=False
                break
        if flagdegree==True:
            for k in range(1,ehnumnodes+1):
                v[k]=k
            cpgoon=True
            permute(1,ehnumnodes,outdegree,indegree,ematrix,refmatrix[i])
            notexist=cpgoon
            if notexist==False:
                index=i
                break
    return notexist,index

def appendNewMotif(ehnumnodes,outdegree,indegree,ematrix):
    global refcountnumnodes,refnumnetworks,refindegree,refoutdegree,refmatrix,refmatcount
    refmatcount[refnumnetworks]=1
    refnumnetworks+=1
    refcountnumnodes.append(ehnumnodes)
    refoutdegree.append(outdegree)
    refindegree.append(indegree)
    refmatrix.append(ematrix)

def filterMotif(threshold):
    global refcountnumnodes,refnumnetworks,refindegree,refoutdegree,refmatrix,refmatcount
    temp=0
    crefmatcount=refmatcount.copy()
    for key,value in crefmatcount.items():
        if value<threshold:
            del refmatcount[key]
            del refindegree[key-temp]
            del refoutdegree[key-temp]
            del refmatrix[key-temp]
            del refcountnumnodes[key-temp]
            temp+=1

def saveList(fname,lst):
    fw=open(fname,'wb')
    pickle.dump(lst,fw)
    fw.close()

def extractIndex(exnumber,totalnumber):
    if exnumber>totalnumber:
        print('Error:exnumber should be less than totalnumber')
        exit
    out=[-1 for i in range(exnumber)]
    base=np.arange(totalnumber)
    combine(base,out,totalnumber,exnumber)
def combine(base,out,n,m):
    global ind_combination
    if m==0:
        ind_combination.append(np.asarray(out))
        return
    else:
        for i in range(n,m-1,-1):
            out[m-1]=base[i-1]
            combine(base,out,i-1,m-1)
def readPickle(fname):
    file=open(fname,'rb')
    pkl=pickle.load(file)
    file.close()
    return pkl
def filterTraj():
    fwdir="E:/Senior/Graduation project/YahooFlickr/NewYorktemp/New_Traj_Delete/"
    fdir="E:/Senior/Graduation project/YahooFlickr/NewYorktemp/New_Traj"
    os.chdir(fdir)
    flist=os.listdir()
    count=0
    for fname in flist:
        straj=readPickle(fname)
        locations=straj2loca(straj)
        enumnodes=len(locations)#the number of attractions visited
        if enumnodes>=thre_node_num:
            saveList(fwdir+fname,straj)
            os.remove(fname)
def main():
    #filterTraj()
    global refcountnumnodes,refnumnetworks,refindegree,refoutdegree,refmatrix,refmatcount
    global ind_combination

    fdir="E:/Senior/Graduation project/YahooFlickr/NewYorktemp/New_Traj"
    os.chdir(fdir)
    flist=os.listdir()
    numnode1=0
    numnode2=0
    motif_trip=[]
    combination={}

    for i in range(3,thre_node_num+1):
        if i>thre_sub_node_num:
            tr=thre_sub_node_num
        else:
            tr=i
        for j in range(3,tr+1):
            ind_combination=[]
            extractIndex(j,i)
            combination[(j,i)]=ind_combination

    for fname in flist:
        straj=readPickle(fname)
        locations=straj2loca(straj)
        enumnodes=len(locations)#the number of attractions visited
        if enumnodes==1:
            numnode1+=1
            continue
        if enumnodes==2:
            outdegree,indegree,ematrix,hlocations=getNetwork(locations)
            ehnumnodes=len(hlocations)#the number of attractions visited without repetition
            if ehnumnodes==2:
                numnode2+=1
            else:
                numnode1+=1
                print(fname)
                print(traj)
            continue

        ind_trip=[]
        start=time.clock()
        for snum in range(3,enumnodes+1):
            if snum>thre_sub_node_num:
                snum=thre_sub_node_num
            indc=combination[(snum,enumnodes)]
            lind=len(indc)
            for i in range(lind):
                loca_arr=np.asarray(locations)
                sloca=loca_arr[indc[i]].tolist()
                temp=[]
                temp.append(sloca[0])
                for j in range(1,snum):
                    if sloca[j]==sloca[j-1]:
                        continue
                    else:
                        temp.append(sloca[j])
                sloca=temp
                outdegree,indegree,ematrix,hlocations=getNetwork(sloca)
                ehnumnodes=len(hlocations)#the number of attractions visited without repetition
                if ehnumnodes>thre_motif_node_num or ehnumnodes==1:#according to statistics, there exist no motifs with more than 8 nodes
                    continue
                outdegree,indegree,ematrix=orderNetwork(outdegree,indegree,ematrix,ehnumnodes)
                notexist,index=judgeMotifNew(ehnumnodes,outdegree,indegree,ematrix)
                if notexist==True:
                    ind_trip.append(refnumnetworks)
                    appendNewMotif(ehnumnodes,outdegree,indegree,ematrix)
                else:
                    if index not in ind_trip:
                        ind_trip.append(index)
                        refmatcount[index]+=1
        motif_trip.append([fname,ind_trip])
        finish=time.clock()
        print(finish-start)

##    mat=np.zeros((7,7))
##    for i in range(len(refmatrix)):
##        print(i)
##        matrix=refmatrix[i]
##        for j in range(1,7):
##            for k in range(1,7):
##                mat[j-1,k-1]=matrix[(j,k)]
##        print(mat)
    #print(refmatrix)
    crefmatcount=refmatcount.copy()
    crefmatrix=refmatrix.copy()
    filterMotif(thre)

    fwdir="E:/Senior/Graduation project/YahooFlickr/NewYorktemp/Motifs/Motif_interval"
    os.chdir(fwdir)
    saveList("crefmatcount.pkl",crefmatcount)
    saveList("crefmatrix.pkl",crefmatrix)
    saveList("refmatcount.pkl",refmatcount)
    saveList("refoutdegree.pkl",refoutdegree)
    saveList("refindegree.pkl",refindegree)
    saveList("refmatrix.pkl",refmatrix)
    saveList("refcountnumnodes.pkl",refcountnumnodes)
    saveList("motif_trip.pkl",motif_trip)
    print('numnode1:',numnode1)
    print('numnode2:',numnode2)


if __name__ == '__main__':
    main()

'''
use within-cluster connection COUNT algorithm.
modules of algorithm

Last edited: June 7
'''


from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.externals import joblib
import sys
import numpy as np
import pandas as pd
import random as rd
import json
import arrow as ar
import scipy.sparse as scs
import simFunction as sf

time1 = ar.now()
######### input
# target = '0000841919'
target = '0000187738' #SimM_ind[0] ##"0000"
Rec_dict_len = 1000
path = '../trainedData/'
pca = joblib.load(path + 'PCA_model.pkl')           #trained pca
km_pca = joblib.load(path + 'km_pca_model.pkl')     #trained kmeans model
SimM1 = np.load(path + 'SimilaryMatrix.npy')        #trained based line similarity matrix
SimM_ind = np.load(path + 'SM_index.npy')           #trained index of similarity matrix
fv = pd.read_table(path + 'FeatureVector.txt', sep = '\t', dtype= {'CMark': object}, index_col = 0) #trained featureVector
fv = fv.set_index('CMark')
A_sparse_send = scs.load_npz(path + 'A_sparse_send_full.npz')
score_mtx_rec = A_sparse_send.transpose(copy = True)
score_mtx_send = score_mtx_rec.transpose(copy = True)
# fname_nl = path +'namelist.txt'
# with open(fname_nl, 'r') as f:
#     namelist = json.load(f)
namelist = list(fv.index)
#########
rd.seed(19920804)
Rec_dict = {}
SimPair = {}
NBS = {}
NBR = {}
n_mark = len(SimM_ind)
SM1_ind_set = set(SimM_ind)
thres = 0
# if target in SimM_ind:
#     fv = fv.loc[SimM_ind]
# else:
#     fv = fv.loc[np.append(SimM_ind, target)]


Mark2Ind = {}
for i in range(n_mark):
    Mark2Ind[SimM_ind[i]] = i
    x = SimM_ind[i]
    x_ind = namelist.index(x)
    xx_ind = (score_mtx_send[x_ind,:]>thres).nonzero()[1]
    xx_ind_sort = sorted(xx_ind, key=lambda k: score_mtx_send[x_ind,k])[::-1]
    NBS[x] = []
    for j in xx_ind_sort:
        if (namelist[j] in SM1_ind_set) and (namelist[j]!=x):
            NBS[x].append(namelist[j])
    if len(NBS[x])==0:
        del NBS[x]
    xx_ind = (score_mtx_send[:,x_ind]>thres).nonzero()[0]
    xx_ind_sort = sorted(xx_ind, key=lambda k: score_mtx_send[k,x_ind])[::-1]
    NBR[x] = []
    for j in xx_ind_sort:
        if (namelist[j] in SM1_ind_set) and (namelist[j]!=x):
            NBR[x].append(namelist[j])
    if len(NBR[x])==0:
        del NBR[x]

if target not in NBS:
    x = target
    x_ind = namelist.index(x)
    xx_ind = (score_mtx_send[x_ind,:]>thres).nonzero()[1]
    xx_ind_sort = sorted(xx_ind, key=lambda k: score_mtx_send[x_ind,k])[::-1]
    NBS[x] = []
    for j in xx_ind_sort:
        if (namelist[j] in SM1_ind_set) and (namelist[j]!=x):
            NBS[x].append(namelist[j])
    if len(NBS[x])==0:
        del NBS[x]

if target not in NBR:
    x = target
    x_ind = namelist.index(x)
    xx_ind = (score_mtx_send[:,x_ind]>thres).nonzero()[0]
    xx_ind_sort = sorted(xx_ind, key=lambda k: score_mtx_send[k,x_ind])[::-1]
    NBR[x] = []
    for j in xx_ind_sort:
        if (namelist[j] in SM1_ind_set) and (namelist[j]!=x):
            NBR[x].append(namelist[j])
    if len(NBR[x])==0:
        del NBR[x]
# of_D = open('May-June/DownRec_fast.txt', 'a')
# of_U = open('May-June/UpRec_fast.txt', 'a')

print(target)
## compute similarity vector
print('Compute Sim.\n')
Rec_dict[target] ={}
x = target
rdl = 150
sim_v = np.array([])

## depth 2 similarity , to change to depth 1 similarity, can only compute
## sim_v = [sim(fv.loc[target], fv.loc[x]) for x in SimM_ind]
for j in range(n_mark):
    # if (j>1):
        # break
    y = SimM_ind[j]
    t = 1
    D_send = 0
    D_rec = 0
    if (x in NBS) and( y in NBS):
        nn = len(NBS[x])
        mm = len(NBS[y])
        if (nn>rdl):
            NBS[x] = [NBS[x][ind] for ind in rd.sample(range(nn), rdl)]
            nn = rdl
        if (mm>rdl):
            NBS[y] = [NBS[y][ind] for ind in rd.sample(range(mm), rdl)]
            mm = rdl
        t = t +1
        alist = []
        blist = []
        for k in NBS[x]:
            alist = alist + [k] * mm
        blist = NBS[y] * nn
        D = []
        # print('%d, %d'%(nn,mm))
        for k in range(nn*mm):
            # if (k%(rdl*10)==0):
            #     print('k = %d'%k)
            if (alist[k] in Mark2Ind.keys()) and (blist[k] in Mark2Ind.keys()):
                D.append(SimM1[Mark2Ind[alist[k]], Mark2Ind[blist[k]]])
            elif (alist[k]+'\t'+ blist[k] in SimPair):
                D.append(SimPair[alist[k]+'\t'+ blist[k]])
            elif (blist[k]+'\t'+ alist[k] in SimPair):
                D.append(SimPair[blist[k]+'\t'+ alist[k]])
            else:
                SimPair[alist[k]+'\t'+ blist[k]] = sf.sim_com(fv.loc[alist[k]], fv.loc[blist[k]])
                D.append(SimPair[alist[k]+'\t'+ blist[k]])
        m = np.matrix(np.reshape(D, (nn, mm)))
        D_send = max(m.max(axis = 0).mean(), m.max(axis = 1).mean())
    D_com = sf.sim_com(fv.loc[x], fv.loc[y])
    if (x in NBR) and (y in NBR):
        nn = len(NBR[x])
        mm = len(NBR[y])
        if (nn>rdl):
            NBR[x] = [NBR[x][ind] for ind in rd.sample(range(nn), rdl)]
            nn = rdl
        if (mm>rdl):
            NBR[y] = [NBR[y][ind] for ind in rd.sample(range(mm), rdl)]
            mm = rdl
        t = t +1
        alist = []
        blist = []
        # print('%d, %d'%(nn,mm))
        for k in NBR[x]:
            alist = alist + [k] * mm
        blist = NBR[y] * nn
        D = []
        for k in range(nn*mm):
            # if (k%(rdl*10)==0):
                # print('k = %d'%k)
            if (alist[k] in Mark2Ind.keys()) and (blist[k] in Mark2Ind.keys()):
                D.append(SimM1[Mark2Ind[alist[k]], Mark2Ind[blist[k]]])
            elif (alist[k]+'\t'+ blist[k] in SimPair):
                D.append(SimPair[alist[k]+'\t'+ blist[k]])
            elif (blist[k]+'\t'+ alist[k] in SimPair):
                D.append(SimPair[blist[k]+'\t'+ alist[k]])
            else:
                SimPair[alist[k]+'\t'+ blist[k]] = sf.sim_com(fv.loc[alist[k]], fv.loc[blist[k]])
                D.append(SimPair[alist[k]+'\t'+ blist[k]])
        m = np.matrix(np.reshape(D, (nn, mm)))
        D_rec = max(m.max(axis = 0).mean(), m.max(axis = 1).mean())
    sim_v = np.append(sim_v,(D_send + D_rec + D_com)/t)


print('finish computing sim vec\n')
## apply pca on sim_v

sim_v_pca = pca.transform(sim_v.reshape(1,-1))

## predict km cluster

np_label = km_pca.predict(sim_v_pca)

cl_index = np.where(km_pca.labels_ ==np_label) #find the index of same cluster, which is used to do collaborative filtering

sim_v_cl = sim_v[cl_index]
cl_index_2 = [ namelist.index(SimM_ind[i])for i in cl_index[0]]
## collaborative Filtering
print('Collaborative Filtering')

## down stream recommmendation
Re_list = np.zeros(shape = (score_mtx_send.shape[1],))
score_mtx_send[score_mtx_send>0] = 1
Re_list = score_mtx_send[cl_index_2,].transpose().dot(sim_v_cl)/sim_v_cl.sum()

# for i in range(score_mtx.shape[1]):
#     # if (i%10000 ==0):
#     #     print(i)
#     score_vt = score_mtx[cl_index[0],i]
#     ## I use some filter to de-noise, to simplify, can just
#     ## Re_list[i] = score_vt.transpose().dot(sim_v_cl)/sim_v_cl.sum() or even without loop
#     ## Re_list = score_mtx[cl_index[0],].transpose().dot(sim_v_cl)/sim_v_cl.sum()
#     if (score_vt.count_nonzero()>4) and(sim_v_cl[score_vt.nonzero()[0]].sum()>0.7):
#         temp = (score_vt>0).toarray().reshape(len(sim_v_cl),)*sim_v_cl ##
#         temp[np.argsort(temp)[::-1][5:]] = 0
#         most_similar_company = temp
#         Re_list[i] = score_vt.transpose().dot(most_similar_company)/most_similar_company.sum()

target_down_stream =A_sparse_send[namelist.index(target),:].todense()

'''
given 1-depth similarity matrix. Compute the 2-depth similary matrix.

last edited: June 7

'''
import numpy as np
import pandas as pd
import random as rd
import json
import arrow as ar
import simFunction as sf
import scipy.sparse as scs
import sys

rd.seed(19920804)
try:
    path = '../' + sys.argv[1]
except:
    path = '../trainedDataSmall/'
print('path = ' +path)
#print('breakFlag = ' + str(breakFlag))

with open(path +'namelist.txt', 'r') as f:
    namelist = json.load(f)
nameset = set(namelist)
SimM1 = np.load(path +'SimilaryMatrix.npy')
SM1_ind = np.load(path +'SM_index.npy')
SM1_ind_set = set(SM1_ind)
n_mark = len(SM1_ind)
SimM2 = np.identity(n_mark)
SimPair = {}
Mark2Ind = {}
fv = pd.read_table(path +'FeatureVector.txt', sep = '\t', dtype= {'CMark': object}, index_col = 0)
fv = fv.set_index('CMark')
rdl = 150
mtx_sps = scs.load_npz(path + 'A_sparse_send_full.npz')
NBS = {}
NBR = {}
namedic = {}
for i,key in enumerate(namelist):
    namedic[key] = i
print('start')
test_time1 = ar.now()
base_line_index = [ namedic[i] for i in SM1_ind]
base_namedic = {}
for i,ind in enumerate(base_line_index):
    base_namedic[ind] = i
for i, x in enumerate(SM1_ind):
    Mark2Ind[x] = i
    x_ind = base_line_index[i]
    mtx_sps[x_ind, x_ind] = 0
    xx_ind = (mtx_sps[x_ind, base_line_index]>1).nonzero()[1]
    # print(len(xx_ind))
    if len(xx_ind)>0:
        xx_ind_sort = sorted(xx_ind, key=lambda k: mtx_sps[x_ind,k])[::-1]
        NBS[x] = [SM1_ind[j] for j in xx_ind_sort[0:min(rdl, len(xx_ind))]]

    xx_ind = (mtx_sps[base_line_index,x_ind]>1).nonzero()[0]
    # print(len(xx_ind))
    if len(xx_ind)>0:
        xx_ind_sort = sorted(xx_ind, key=lambda k: mtx_sps[k,x_ind])[::-1]
        NBR[x] = [SM1_ind[j] for j in xx_ind_sort[0:min(rdl, len(xx_ind))]]
test_time2 = ar.now()
print('NBS and NBR time:')
print(test_time2 - test_time1)

with open(path +'NBS.txt', 'w') as f:
    json.dump(NBS, f)
with open(path +'NBR.txt', 'w') as f:
    json.dump(NBR, f)

for i in range(n_mark):
    x = SM1_ind[i]
    if (i%100==0):
        # break
        print(i)
    time1 = ar.now()
    for j in range(i+1, n_mark):
        # if (j>1):
            # break
        y = SM1_ind[j]
        t = 1
        D_send = 0
        D_rec = 0
        if (x in NBS) and( y in NBS):
            nn = len(NBS[x])
            mm = len(NBS[y])
            # if (nn>rdl):
            #     print('>rdl')
            #     NBS[x] = [NBS[x][ind] for ind in rd.sample(range(nn), rdl)]
            #     nn = rdl
            # if (mm>rdl):
            #     print('>rdl')
            #     NBS[y] = [NBS[y][ind] for ind in rd.sample(range(mm), rdl)]
            #     mm = rdl
            t = t +1
            alist = []
            blist = []
            for k in NBS[x]:
                alist = alist + [k] * mm
            blist = NBS[y] * nn
            D = []
            for k in range(nn*mm):
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
        D_com = SimM1[i,j]
        if (x in NBR) and (y in NBR):
            nn = len(NBR[x])
            mm = len(NBR[y])
            # if (nn>rdl):
            #     print('>rdl')
            #     NBR[x] = [NBR[x][ind] for ind in rd.sample(range(nn), rdl)]
            #     nn = rdl
            # if (mm>rdl):
            #     print('>rdl')
            #     NBR[y] = [NBR[y][ind] for ind in rd.sample(range(mm), rdl)]
            #     mm = rdl
            t = t +1
            alist = []
            blist = []
            for k in NBR[x]:
                alist = alist + [k] * mm
            blist = NBR[y] * nn
            D = []
            for k in range(nn*mm):
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
        SimM2[i,j] = (D_send + D_rec + D_com)/t
        SimM2[j,i] = SimM2[i,j]
    time2 = ar.now()
#    print(time2-time1)
np.save(path +'SimilaryMatrix2', SimM2)
with open(path +'SimPair.json', 'w', encoding = 'utf8') as of:
    json.dump(SimPair, of)
logf = open(path +'SimilaryMatrix2_log.txt', 'w', encoding = 'utf8')
logf.write('Neighbor extracted by list\n')
logf.write('Use Ar, As and fix feature vectors.\n')
logf.write(str(ar.now()))
logf.close()

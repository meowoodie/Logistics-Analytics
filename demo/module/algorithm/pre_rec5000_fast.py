'''
use within-cluster connection COUNT algorithm.

Last edited: May 28
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

#########
Start_p = 2000
End_p = 5000
#########

pca = joblib.load('output/PCA_model.pkl')
km_pca = joblib.load('output/km_pca_model.pkl')
SimM1 = np.load('output/SimilaryMatrix.npy')
SimM_ind = np.load('output/SM_index.npy')
# target_list = ['0000841919', '0000536923','0000501372','0000407808', ##3C
#                 '0001532950','0001516417','0001521830',              ##fresh
#                 '0000693220', '0000608357', '0000579436']            ##health
with open('May-June/namelist.txt', 'r') as f:
    target_list = json.load(f)[Start_p:End_p]
with open('May-June/flag_tr_te.txt', 'r') as f:
    tr_te = json.load(f)
Rec5000_dict = {}
Rec_dict_len = 1000
# target = '0000187738' #SimM_ind[0] ##"0000"
n_mark = len(SimM_ind)
fv = pd.read_table('May-June/FeatureVector.txt', sep = '\t', dtype= {'CMark': object}, index_col = 0)
fv = fv.set_index('CMark')
# if target in SimM_ind:
#     fv = fv.loc[SimM_ind]
# else:
#     fv = fv.loc[np.append(SimM_ind, target)]

rd.seed(19920804)
with open('May-June/NeighborSend_list_True.txt', 'r') as f:
    NBS= json.load(f)
with open('May-June/NeighborRec_list_True.txt', 'r') as f:
    NBR= json.load(f)
with open('output/SimPair.json', 'r', encoding = 'utf8') as f:
    SimPair = json.load(f)
global w, indlistlen
w = {'oversea': 1, 'indust1': 8, 'indust2': 5, 'area': 1, 'DayAverage': 3, 'Variation': 3, 'toInd': 15, 'fromInd': 10, 'SoverR': 10, 'toIndSet': 15, 'fromIndSet':10}
w = pd.Series(w)
w = w/sum(w)
indlistlen = 12


def overlap(x):
    a = x.iloc[0]
    b = x.iloc[1]
    a = set(a[1:-1].replace("'", '').replace(" ",'').split(','))
    b = set(b[1:-1].replace("'", '').replace(" ",'').split(','))
    if ('' in a) or('' in b):
        ol = 0
    else:
        ol = len(a & b) / len(a|b)
    return(ol)

def sim_com(a, b):
    sim = 0
    sim += w['oversea'] * int(a[0] == b[0])           #oversea
    sim += w['indust1'] * int(a[1] == b[1])           #indust1
    sim += w['indust2'] * int(a[2] == b[2])
    sim += w['area'] * int(a[3] == b[3])           #area
    sim += w['DayAverage'] * (1 - abs(a[4] - b[4])/(a[4] + b[4]))      #DayAverage
    sim += w['Variation'] * (1 - abs(a[5] - b[5])/(a[5]+b[5]))           #Variation
    r = 1                                   #control the influence of main industry, eg: for less influence can choose r = 0.5
    sim += w['toInd'] * (1 - np.linalg.norm((abs(a[6:(6 + indlistlen)] - b[6:(6 + indlistlen)]) * (pd.concat([a[6:(6+indlistlen)], b[6:(6+indlistlen)]], axis = 1).max(axis = 1) ** r)),
                                                ord = 1)/2)  #toIndust
    sim += w['fromInd'] * (1 - np.linalg.norm((abs(a[(6 + indlistlen):(6+ 2* indlistlen)] - b[(6 + indlistlen):(6+ 2* indlistlen)]) *
                                                 (pd.concat([a[(6 + indlistlen):(6+ 2* indlistlen)], b[(6 + indlistlen):(6+ 2* indlistlen)]], axis = 1).max(axis =1) ** r)),
                                                ord = 1)/2)#fromIndust
    sim += w['SoverR'] * (1 - abs(a[6 + 2 * indlistlen] - b[6 + 2 * indlistlen])/ (a[6 + 2 * indlistlen] + b[6 + 2 * indlistlen]))
    sim += w['toIndSet'] * np.linalg.norm(np.array(pd.concat([a[(7 + 2 * indlistlen):(7 + 3 * indlistlen) ], b[(7 + 2 * indlistlen): (7 + 3 * indlistlen)]], axis = 1).apply(
        axis = 1, func = lambda x: overlap(x)))*np.array((a[6:(6 + indlistlen)] + b[6:(6 + indlistlen)])/2), ord = 1)
    sim += w['fromIndSet'] * np.linalg.norm(np.array(pd.concat([a[7 + 3 * indlistlen: ], b[7 + 3 * indlistlen:]], axis = 1).apply(
        axis = 1, func = lambda x: overlap(x))) * np.array((a[(6 + indlistlen):(6+ 2 * indlistlen)] + b[(6 + indlistlen):(6+ 2 * indlistlen)])/2), ord = 1)
    return(sim)
Mark2Ind = {}
for i in range(n_mark):
    Mark2Ind[SimM_ind[i]] = i
of_D = open('May-June/DownRec_fast.txt', 'a')
of_U = open('May-June/UpRec_fast.txt', 'a')

for cc, target in enumerate(target_list):
    print(cc)
    print(target)
    ## compute similarity vector
    print('Compute Sim.\n')
    Rec5000_dict[target] ={}
    x = target
    time1 = ar.now()
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
                    SimPair[alist[k]+'\t'+ blist[k]] = sim_com(fv.loc[alist[k]], fv.loc[blist[k]])
                    D.append(SimPair[alist[k]+'\t'+ blist[k]])
            m = np.matrix(np.reshape(D, (nn, mm)))
            D_send = max(m.max(axis = 0).mean(), m.max(axis = 1).mean())
        D_com = sim_com(fv.loc[x], fv.loc[y])
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
                    SimPair[alist[k]+'\t'+ blist[k]] = sim_com(fv.loc[alist[k]], fv.loc[blist[k]])
                    D.append(SimPair[alist[k]+'\t'+ blist[k]])
            m = np.matrix(np.reshape(D, (nn, mm)))
            D_rec = max(m.max(axis = 0).mean(), m.max(axis = 1).mean())
        sim_v = np.append(sim_v,(D_send + D_rec + D_com)/t)


    print('finish computing sim vec\n')
    ## apply pca on sim_v

    sim_v_pca = pca.transform(sim_v.reshape(1,-1))

    ## predict km cluster

    np_label = km_pca.predict(sim_v_pca)

    cl_index = np.where(km_pca.labels_ ==np_label)
    if target in SimM_ind:
        cl_index = (cl_index[0][np.where(cl_index[0]!=Mark2Ind[target])],)
    sim_v_cl = sim_v[cl_index]

    ## collaborative Filtering
    print('Collaborative Filtering')
    path = 'May-June/'
    fname_nl = path +'namelist.txt'
    with open(fname_nl, 'r') as f:
        namelist = json.load(f)
    ## down stream recommmendation
    score_mtx = scs.load_npz('May-June/A_sparse_send.npz')
    Re_list = np.zeros(shape = (score_mtx.shape[1],))
    score_mtx[score_mtx>0] = 1
    Re_list = score_mtx[cl_index[0],].transpose().dot(sim_v_cl)/sim_v_cl.sum()

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
    fname_As = path + 'A_s.txt'
    with open(fname_As, 'r') as f:
        A_s = json.load(f)
    target_down_stream =np.zeros(shape = (score_mtx.shape[1],))
    if target in A_s:
        for y in A_s[target]:
            if (tr_te[target+'-'+y]==1):
                target_down_stream[namelist.index(y)] = A_s[target][y]
    count = 0
    i = -1
    Re_list_index = np.argsort(Re_list)[::-1]
    print('Down stream company recommendation:')
    Ds_rl = []
    Ds_rl2 = []
    while (count<Rec_dict_len):
        i += 1
        if (i>=5000):
            print(target)
            break
        if (target_down_stream[Re_list_index[i]] >0):
            continue
        if (namelist[Re_list_index[i]] ==target):
            continue
        Ds_rl.append((namelist[Re_list_index[i]], Re_list[Re_list_index[i]]))
        Ds_rl2.append(namelist[Re_list_index[i]])
        # print(namelist[Re_list_index[i]])
        count +=1
    Rec5000_dict[target]['Down'] = Ds_rl
    # a = np.argsort(Re_list)[::-1][0:200]
    # b = np.argsort(target_down_stream)[::-1][0:200]
    # set.intersection(set(a),set(b))
    ## up stream recommmendation


    score_mtx = scs.load_npz('May-June/A_sparse_rec.npz')
    Re_list = np.zeros(shape = (score_mtx.shape[1],))
    score_mtx[score_mtx>0] = 1
    Re_list = score_mtx[cl_index[0],].transpose().dot(sim_v_cl)/sim_v_cl.sum()
    # for i in range(score_mtx.shape[1]):
    #     # if (i%10000 ==0):
    #     #     print(i)
    #     score_vt = score_mtx[cl_index[0],i]
    #     if (score_vt.count_nonzero()>4) and(sim_v_cl[score_vt.nonzero()[0]].sum()>0.7):
    #         temp = (score_vt>0).toarray().reshape(len(sim_v_cl),)*sim_v_cl
    #         temp[np.argsort(temp)[::-1][5:]] = 0
    #         most_similar_company = temp
    #         Re_list[i] = score_vt.transpose().dot(most_similar_company)/most_similar_company.sum()
    fname_Ar = path + 'A_r.txt'
    with open(fname_Ar, 'r') as f:
        A_r = json.load(f)
    target_up_stream =np.zeros(shape = (score_mtx.shape[1],))
    if target in A_r:
        for y in A_r[target]:
            if (tr_te[y+'-'+target]==1):
                target_up_stream[namelist.index(y)] = A_r[target][y]
    count = 0
    i = -1
    Re_list_index = np.argsort(Re_list)[::-1]
    print('Up stream company recommendation:')
    us_rl = []
    us_rl2 = []
    while (count<Rec_dict_len):
        i += 1
        if (i>=5000):
            print(target)
            break
        if (target_up_stream[Re_list_index[i]] >0):
            continue
        if (namelist[Re_list_index[i]] ==target):
            continue
        us_rl.append((namelist[Re_list_index[i]], Re_list[Re_list_index[i]]))
        us_rl2.append(namelist[Re_list_index[i]])
        # print(namelist[Re_list_index[i]])
        count +=1
    Rec5000_dict[target]['Up'] = us_rl
    of_D.write(json.dumps(target)+'##?##'+json.dumps(Ds_rl2)+'\n')
    of_U.write(json.dumps(target)+'##?##'+json.dumps(us_rl2)+'\n')
    # print(target+'\t', file = sys.stderr)
    # print(Rec5000_dict[target], file = sys.stderr)
with open('output/Rec5000_fast_dict_'+str(Start_p)+'_'+str(End_p)+'.json', 'w') as of:
    json.dump(Rec5000_dict, of)
logf = open('output/Rec5000_fast_dict_log.txt', 'w', encoding = 'utf8')
logf.write('produced by pred_newp_Rec5000_fast.py')
logf.write(str(ar.now()))
logf.close()
of_D.close()
of_U.close()
time2 = ar.now()
print(time2-time1)

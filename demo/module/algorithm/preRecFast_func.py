'''
use within-cluster connection COUNT algorithm.
function

Last edited: July 2nd
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


def recom(target, pca, km_pca, SimM1, SimM_ind, fv, A_sparse_send, NBS, NBR, namelist):
    #########
    Rec_dict_len = 1000
    score_mtx_rec = A_sparse_send.transpose(copy = True)
    score_mtx_send = score_mtx_rec.transpose(copy = True)
    rd.seed(19920804)
    Rec_dict = {}
    SimPair = {}
    n_mark = len(SimM_ind)
    SM1_ind_set = set(SimM_ind)
    thres = 1
    rdl = 150
    # if target in SimM_ind:
    #     fv = fv.loc[SimM_ind]
    # else:
    #     fv = fv.loc[np.append(SimM_ind, target)]
    namedic = {}
    for i,key in enumerate(namelist):
        namedic[key] = i
    base_line_index = [ namedic[i] for i in SimM_ind]
    base_namedic = {}
    for i,ind in enumerate(base_line_index):
        base_namedic[ind] = i
    Mark2Ind = {}
    for i in range(n_mark):
        Mark2Ind[SimM_ind[i]] = i

    if target not in NBS:
        x = target
        x_ind = namelist.index(x)
        score_mtx_send[x_ind, x_ind] = 0
        xx_ind = (score_mtx_send[x_ind,base_line_index]>thres).nonzero()[1]
        if len(xx_ind)>0:
            xx_ind_sort = sorted(xx_ind, key=lambda k: score_mtx_send[x_ind,k])[::-1]
            NBS[x] = [SimM_ind[j] for j in xx_ind_sort[0:min(rdl, len(xx_ind))]]

    if target not in NBR:
        x = target
        x_ind = namelist.index(x)
        xx_ind = (score_mtx_send[base_line_index,x_ind]>thres).nonzero()[0]
        if len(xx_ind)>0:
            xx_ind_sort = sorted(xx_ind, key=lambda k: score_mtx_send[k,x_ind])[::-1]
            NBR[x] = [SimM_ind[j] for j in xx_ind_sort[0:min(rdl, len(xx_ind))]]
    # of_D = open('May-June/DownRec_fast.txt', 'a')
    # of_U = open('May-June/UpRec_fast.txt', 'a')

    print(target)
    ## compute similarity vector
    print('Compute Sim.\n')
    Rec_dict[target] ={}
    x = target
    sim_v = np.array([])
    print("size of neighbor")
    print(len(NBS[x]))
    print(len(NBR[x]))

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
            # if (nn>rdl):
            #     NBS[x] = [NBS[x][ind] for ind in rd.sample(range(nn), rdl)]
            #     nn = rdl
            # if (mm>rdl):
            #     NBS[y] = [NBS[y][ind] for ind in rd.sample(range(mm), rdl)]
            #     mm = rdl
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
            # if (nn>rdl):
            #     NBR[x] = [NBR[x][ind] for ind in rd.sample(range(nn), rdl)]
            #     nn = rdl
            # if (mm>rdl):
            #     NBR[y] = [NBR[y][ind] for ind in rd.sample(range(mm), rdl)]
            #     mm = rdl
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

    target_down_stream =A_sparse_send[namelist.index(target),:].toarray()[0]
    count = 0
    i = -1
    Re_list_index = np.argsort(Re_list)[::-1]
    print('Down stream company recommendation:')
    Ds_rl = []
    # Ds_rl2 = []
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
        # Ds_rl2.append(namelist[Re_list_index[i]])
        # print(namelist[Re_list_index[i]])
        count +=1
    Rec_dict[target]['Down'] = Ds_rl
    # a = np.argsort(Re_list)[::-1][0:200]
    # b = np.argsort(target_down_stream)[::-1][0:200]
    # set.intersection(set(a),set(b))
    ## up stream recommmendation



    Re_list = np.zeros(shape = (score_mtx_rec.shape[1],))
    score_mtx_rec[score_mtx_rec>0] = 1
    Re_list = score_mtx_rec[cl_index[0],].transpose().dot(sim_v_cl)/sim_v_cl.sum()
    # for i in range(score_mtx.shape[1]):
    #     # if (i%10000 ==0):
    #     #     print(i)
    #     score_vt = score_mtx[cl_index[0],i]
    #     if (score_vt.count_nonzero()>4) and(sim_v_cl[score_vt.nonzero()[0]].sum()>0.7):
    #         temp = (score_vt>0).toarray().reshape(len(sim_v_cl),)*sim_v_cl
    #         temp[np.argsort(temp)[::-1][5:]] = 0
    #         most_similar_company = temp
    #         Re_list[i] = score_vt.transpose().dot(most_similar_company)/most_similar_company.sum()

    target_up_stream = A_sparse_send.transpose()[namelist.index(target),:].toarray()[0]
    count = 0
    i = -1
    Re_list_index = np.argsort(Re_list)[::-1]
    print('Up stream company recommendation:')
    us_rl = []
    # us_rl2 = []
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
        # us_rl2.append(namelist[Re_list_index[i]])
        # print(namelist[Re_list_index[i]])
        count +=1
    Rec_dict[target]['Up'] = us_rl

    res = {"up_ids":[], "up_scores":[], "down_ids":[], "down_scores":[]}
    for value in Rec_dict[target]['Up']:
        res["up_ids"].append(value[0])
        res["up_scores"].append(value[1])
    for value in Rec_dict[target]['Down']:
        res["down_ids"].append(value[0])
        res["down_scores"].append(value[1])
    return res
    # print(target+'\t', file = sys.stderr)
    # print(Rec5000_dict[target], file = sys.stderr)
# with open(path + 'Rec_fast_dict.json', 'w') as of:
#     json.dump(Rec_dict, of)
# logf = open(path + 'Rec_fast_dict_log.txt', 'w', encoding = 'utf8')
# logf.write('produced by predRecFast.py')
# logf.write(str(ar.now()))
# logf.close()
# time2 = ar.now()
# print(time2-time1)

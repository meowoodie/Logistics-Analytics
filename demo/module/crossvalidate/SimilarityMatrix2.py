'''
given 1-depth similarity matrix. Compute the 2-depth similary matrix.

last edited: April 26

'''
import numpy as np
import pandas as pd
import random as rd
import json
import arrow as ar


rd.seed(19920804)
with open('May-June/NeighborSend_list_True.txt', 'r') as f:
    NBS= json.load(f)
with open('May-June/NeighborRec_list_True.txt', 'r') as f:
    NBR= json.load(f)
SimM1 = np.load('output/SimilaryMatrix.npy')
SM1_ind = np.load('output/SM_index.npy')
n_mark = len(SM1_ind)
SimM2 = np.identity(n_mark)
with open('output/SimPair.json', 'r', encoding = 'utf8') as f:
    SimPair = json.load(f)
Mark2Ind = {}
fv = pd.read_table('May-June/FeatureVector.txt', sep = '\t', dtype= {'CMark': object}, index_col = 0)
fv = fv.set_index('CMark')
rdl = 150


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

for i in range(n_mark):
    Mark2Ind[SM1_ind[i]] = i


for i in range(n_mark):
    x = SM1_ind[i]
    # if (i>0):
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
            if (nn>rdl):
                print('>rdl')
                NBS[x] = [NBS[x][ind] for ind in rd.sample(range(nn), rdl)]
                nn = rdl
            if (mm>rdl):
                print('>rdl')
                NBS[y] = [NBS[y][ind] for ind in rd.sample(range(mm), rdl)]
                mm = rdl
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
                    SimPair[alist[k]+'\t'+ blist[k]] = sim_com(fv.loc[alist[k]], fv.loc[blist[k]])
                    D.append(SimPair[alist[k]+'\t'+ blist[k]])
            m = np.matrix(np.reshape(D, (nn, mm)))
            D_send = max(m.max(axis = 0).mean(), m.max(axis = 1).mean())
        D_com = SimM1[i,j]
        if (x in NBR) and (y in NBR):
            nn = len(NBR[x])
            mm = len(NBR[y])
            if (nn>rdl):
                print('>rdl')
                NBR[x] = [NBR[x][ind] for ind in rd.sample(range(nn), rdl)]
                nn = rdl
            if (mm>rdl):
                print('>rdl')
                NBR[y] = [NBR[y][ind] for ind in rd.sample(range(mm), rdl)]
                mm = rdl
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
                    SimPair[alist[k]+'\t'+ blist[k]] = sim_com(fv.loc[alist[k]], fv.loc[blist[k]])
                    D.append(SimPair[alist[k]+'\t'+ blist[k]])
            m = np.matrix(np.reshape(D, (nn, mm)))
            D_rec = max(m.max(axis = 0).mean(), m.max(axis = 1).mean())
        SimM2[i,j] = (D_send + D_rec + D_com)/t
        SimM2[j,i] = SimM2[i,j]
    time2 = ar.now()
    print(time2-time1)
np.save('output/SimilaryMatrix2', SimM2)
with open('output/SimPair.json', 'w', encoding = 'utf8') as of:
    json.dump(SimPair, of)
logf = open('output/SimilaryMatrix2_log.txt', 'w', encoding = 'utf8')
logf.write('Neighbor extracted by list\n')
logf.write('Use Ar, As and fix feature vectors.\n')
logf.write(str(ar.now()))
logf.close()

'''
Extract features of given marks.
Compute pair-wised smilarity matrix. 1 degree similarity.

last edited: April 26
'''

import pandas as pd
import numpy as np
import json
mark = set()
path = 'May-June/'
with open(path+'com_list_5000_BSGS.txt','r') as markfile:
    mark = set(json.load(markfile)[0:1000])
fv = pd.read_table('May-June/FeatureVector.txt', sep = '\t', dtype= {'CMark': object}, index_col = 0)
fv = fv.set_index('CMark')
fv = fv.loc[mark]
global w, indlistlen
w = {'oversea': 1, 'indust1': 8, 'indust2': 5, 'area': 1, 'DayAverage': 3, 'Variation': 3, 'toInd': 15, 'fromInd': 10, 'SoverR': 10, 'toIndSet': 15, 'fromIndSet':10}
w = pd.Series(w)
w = w/sum(w)
indlistlen = 12
def show_fv(x):
    k = 0
    for y in fv.loc[x]:
        print(fv.loc[x].index[k],' ',fv.loc[x][k])
        k +=1


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
n_mark = len(mark)
SimM = np.identity(n_mark)
SimM_ind = np.array(fv.index)
np.save('output/SM_index', SimM_ind)
for i in range(n_mark):
    print(i)
    for j in range(i+1, n_mark):
        SimM[i,j] = sim_com(fv.loc[SimM_ind[i]], fv.loc[SimM_ind[j]])
        SimM[j,i] = SimM[i,j]
np.save('output/SimilaryMatrix', SimM)

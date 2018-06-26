import json as js
import simFunction as sf
import pandas as pd
import numpy as np
path = ['../trainedDataSmall/', '../trainedDataTest/']
fileName = ['dicts.txt','dictr.txt','dicts_mark.txt', 'dictr_mark.txt', 'tplg.txt', 'cnt.txt', 'inform.txt', 'A_s.txt','A_r.txt','namelist.txt']
fv0 = pd.read_table(path[0]+'FeatureVector.txt', sep = '\t', dtype= {'CMark': object}, index_col = 0)
fv0 = fv0.set_index('CMark')

fv1 = pd.read_table(path[1]+'FeatureVector.txt', sep = '\t', dtype= {'CMark': object}, index_col = 0)
fv1 = fv1.set_index('CMark')

namelist = list(fv0.index)

id1 = '0001044400'
id2 = '0000761974'
sf.sim_com(fv0.loc[id1], fv0.loc[id2])
sf.sim_com(fv1.loc[id1], fv0.loc[id2])


SimM10 = np.load(path[0] +'SimilaryMatrix.npy')
SimM11 = np.load(path[1] +'SimilaryMatrix.npy')
SM1_ind0 = np.load(path[0] +'SM_index.npy')
SM1_ind1 = np.load(path[1] +'SM_index.npy')
dic1 = {}
for i, key in enumerate(SM1_ind1):
    dic1[key] = i
dic0 = {}
for i, key in enumerate(SM1_ind0):
    dic0[key] = i
for i, key in enumerate(dic0):
    if key not in dic1:
        print(i)
        print(key)
for i,id1 in enumerate(SM1_ind0):
    for j, id2 in enumerate(SM1_ind0):
        # print(SimM10[i,j] - SimM11[dic1[id1], dic1[id2]])
        if abs(SimM10[i,j] - SimM11[dic1[id1], dic1[id2]])>0.0001:
            print(SimM10[i,j] - SimM11[dic1[id1], dic1[id2]])
baseLength = 1000
with open(path[0]+'com_list_5000.txt','r') as markfile:
    mark0 = js.load(markfile)[0:baseLength]
with open(path[1]+'com_list_5000.txt','r') as markfile:
    mark1 = js.load(markfile)[0:baseLength]
diff_ind = []
for i, value in enumerate(mark0):
    if value != mark1[i]:
        diff_ind.append(i)

with open(path[0]+'activites.txt', 'r') as f:
    ac0 = js.load(f)
with open(path[1]+'activites.txt', 'r') as f:
    ac1 = js.load(f)

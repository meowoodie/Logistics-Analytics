'''
Extract features of given marks.
Compute pair-wised smilarity matrix. 1 degree similarity.

last edited: April 26
'''
####
breakflag = True
####
import pandas as pd
import numpy as np
import json
import simFunction as sf
mark = set()
path = '../trainedData/'
with open(path+'com_list_5000.txt','r') as markfile:
    mark = set(json.load(markfile)[0:2000])
fv = pd.read_table(path+'FeatureVector.txt', sep = '\t', dtype= {'CMark': object}, index_col = 0)
fv = fv.set_index('CMark')
fv = fv.loc[mark]

n_mark = len(mark)
SimM = np.identity(n_mark)
SimM_ind = np.array(fv.index)
np.save(path +'SM_index', SimM_ind)
for i in range(n_mark):
    print(i)
    if i>10:
        if breakflag:
            break

    for j in range(i+1, n_mark):
        SimM[i,j] = sf.sim_com(fv.loc[SimM_ind[i]], fv.loc[SimM_ind[j]])
        SimM[j,i] = SimM[i,j]
np.save(path +'SimilaryMatrix', SimM)

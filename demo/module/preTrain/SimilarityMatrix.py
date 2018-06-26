'''
Extract features of given marks.
Compute pair-wised smilarity matrix. 1 degree similarity.

last edited: April 26
'''
import pandas as pd
import numpy as np
import json
import simFunction as sf
import sys
import arrow as ar
####
try:
    breakFlag = sys.argv[2] == 'True'
except:
    breakFlag = True
####
start_time = ar.now()
try:
    path = '../' + sys.argv[1]
except:
    path = '../trainedDataSmall/'
try:
    baseLength = int(sys.argv[3])
except:
    baseLength = 1000
with open(path+'com_list_5000.txt','r') as markfile:
    mark = json.load(markfile)[0:baseLength]

print('path = ' +path)
print('breakFlag = ' + str(breakFlag))

fv = pd.read_table(path+'FeatureVector.txt', sep = '\t', dtype= {'CMark': object}, index_col = 0)
fv = fv.set_index('CMark')
fv = fv.loc[mark]

n_mark = len(mark)
SimM = np.identity(n_mark)
SimM_ind = np.array(fv.index)
np.save(path +'SM_index', SimM_ind)
for i in range(n_mark):
    # print(SimM_ind[i])
    if (i%50==0):
        print(i)
        if breakFlag:
            break

    for j in range(i+1, n_mark):
        SimM[i,j] = sf.sim_com(fv.loc[SimM_ind[i]], fv.loc[SimM_ind[j]])
        SimM[j,i] = SimM[i,j]
np.save(path +'SimilaryMatrix', SimM)
end_time = ar.now()
with open(path + 'similarity.log', 'w') as of:
    of.write(str(baseLength)+ '\n')
    of.write('Starts at: '+ str(start_time)+'\n')
    of.write('Ends at: ' + str(end_time)+'\n')

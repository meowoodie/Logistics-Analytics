'''
change A_s to a sparse csc_matrix

last edited: April 26
'''

import json as js
from scipy.sparse import csc_matrix as spm
import scipy.sparse
import numpy as np
import arrow as ar

code_start_time = ar.now()
path = 'May-June/'
fname_As = path + 'A_s.txt'
fname_Ar = path + 'A_r.txt'
fname_nl = path +'namelist.txt'
fname_tr_te = path +'flag_tr_te.txt'
with open(fname_nl, 'r') as f:
    namelist = js.load(f)
with open(fname_As, 'r') as f:
    A_s = js.load(f)
with open(fname_tr_te, 'r') as f:
    tr_te = js.load(f)
# with open(fname_Ar, 'r') as f:
#     A_r = js.load(f)
SimM_ind = np.load('output/SM_index.npy')
row = []
column = []
data  = []
count = -1
test_sum = 0
for x in SimM_ind:
    count += 1
    print(count)
    if x not in A_s :
        continue
    for y in A_s[x]:
        if (tr_te[x+'-'+y]==1):
            row.append(count)
            column.append(namelist.index(y))
            data.append(A_s[x][y])
        else:
            test_sum +=1
print(test_sum)
row = np.array(row)
column = np.array(column)
data = np.array(data)
n = len(namelist)
A_sparse_send = spm((data,(row, column)), shape= (len(SimM_ind), n))
scipy.sparse.save_npz(path+'A_sparse_send', A_sparse_send)
# print('receive \n')
# for x in SimM_ind:
#     if x not in nameset:
#         namelist.append(x)
#         nameset.add(x)
#     if x not in A_r:
#         continue
#     for y in A_r[x]:
#         if y not in nameset:
#             namelist.append(y)
#             nameset.add(y)
#         if (len(namelist)%1000==0):
#             print(len(namelist))
#         row.append(namelist.index(y))
#         column.append(namelist.index(x))
#         data.append(A_r[x][y])
# row = np.array(row)
# column = np.array(column)
# data = np.array(data)
# n = len(namelist)
# A_sparse = spm((data,(row, column)), shape= (n, n))
# scipy.sparse.save_npz(path+'A_sparse', A_sparse)
# with open(path +'A_index.txt', 'w') as f:
#     js.dump(namelist, f)

logf = open(path+'A_sparse_send_log.txt', 'w')
logf.write('V->B, where V is in the 1000 pivots. a 1000*5000 matrix.\n')
logf.write('Code starts at: '+str(code_start_time)+'\n')
logf.write('Code ends at: '+str(ar.now()))
logf.close()

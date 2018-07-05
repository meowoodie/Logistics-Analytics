'''
change A_r to a sparse csc_matrix

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
with open(fname_Ar, 'r') as f:
    A_r = js.load(f)
with open(fname_tr_te, 'r') as f:
    tr_te = js.load(f)
# with open(fname_Ar, 'r') as f:
#     A_r = js.load(f)
SimM_ind = np.load('output/SM_index.npy')
row = []
column = []
data  = []
count = -1
for x in SimM_ind:
    count += 1
    print(count)
    if x not in A_r :
        continue
    for y in A_r[x]:
        if (tr_te[y+'-'+x]==1):
            row.append(count)
            column.append(namelist.index(y))
            data.append(A_r[x][y])
row = np.array(row)
column = np.array(column)
data = np.array(data)
n = len(namelist)
A_sparse_rec = spm((data,(row, column)), shape= (len(SimM_ind), n))
scipy.sparse.save_npz(path+'A_sparse_rec', A_sparse_rec)


logf = open(path+'A_sparse_rec_log.txt', 'w')
logf.write('Only contain A->V,  where V is in the 1000 pivots. 1000*5000matrix.\n')
logf.write('Code starts at: '+str(code_start_time)+'\n')
logf.write('Code ends at: '+str(ar.now()))
logf.close()

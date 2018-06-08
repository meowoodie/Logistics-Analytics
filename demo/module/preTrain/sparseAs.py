'''
change A_s to a sparse csc_matrix 610,000 by 610,000 sparse matrix
find 5000 most active companies.
last edited: June 7
'''

import json as js
from scipy.sparse import csc_matrix as spm
import scipy.sparse
import numpy as np
import arrow as ar
import json

code_start_time = ar.now()
path = '../trainedData/'
fname_As = path + 'A_s.txt'
fname_Ar = path + 'A_r.txt'
fname_nl = path +'namelist.txt'
of_comls = path +'com_list_5000.txt'
with open(fname_nl, 'r') as f:
    namelist = js.load(f)
with open(fname_As, 'r') as f:
    A_s = js.load(f)
activities_count =[0]*len(namelist)
# with open(fname_Ar, 'r') as f:
#     A_r = js.load(f)
row = []
column = []
data  = []
count = -1
test_sum = 0
for x in A_s:
    for y in A_s[x]:
        i = namelist.index(x)
        j = namelist.index(y)
        row.append(i)
        column.append(j)
        data.append(A_s[x][y])
        activities_count[i] = activities_count[i] + A_s[x][y]
        activities_count[j] = activities_count[j] + A_s[x][y]
print(len(row))
row = np.array(row)
column = np.array(column)
data = np.array(data)
n = len(namelist)
A_sparse_send = spm((data,(row, column)), shape= (n, n))
scipy.sparse.save_npz(path+'A_sparse_send_full', A_sparse_send)
sort_ind = sorted(range(n), key=lambda k: activities_count[k])
sort_ind = sort_ind[::-1]
with open(of_comls, 'w') as f:
    json.dump([ namelist[i]   for i in sort_ind[0:5000]],f)
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

logf = open(path+'A_sparse_send_full_log.txt', 'w')
logf.write('610,000 by 610,000 matrix.\n')
logf.write('Code starts at: '+str(code_start_time)+'\n')
logf.write('Code ends at: '+str(ar.now()))
logf.close()

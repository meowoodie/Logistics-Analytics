'''
find neighbor within a given mark list

last edited: April 26
'''

import numpy as np
import pandas as pd
import heapq
import json

by_list = True
path = 'May-June/'
fname_As = path + 'A_s.txt'
fname_Ar = path + 'A_r.txt'
mark = set()
if by_list:
    with open(path+'com_list_5000_BSGS.txt','r') as markfile:
        mark = set(json.load(markfile)[0:1000])
with open(path +'flag_tr_te.txt', 'r') as f:
    tr_te = json.load(f)
max_depth = 1
with open(fname_As, 'r') as f:
    A_s= json.load(f)
with open(fname_Ar, 'r') as f:
    A_r= json.load(f)
NBS = {}
NBR = {}
## send
for x in A_s:
    B = sorted(A_s[x].items(), key=lambda x: (x[1],x[0]), reverse=True)
    count = 0
    for y in B:
        count = count + 1
        if (x!=y[0]):
            if (y[1]>1) and (tr_te[x+'-'+y[0]]==1):
                if (y[0] in mark) or (not by_list):
                    if x not in NBS:
                        NBS[x] = []
                    NBS[x].append(y[0])
        if (count ==150):
            break

## receive
for x in A_r:
    B = sorted(A_r[x].items(), key=lambda x: (x[1],x[0]), reverse=True)
    count = 0
    for y in B:
        count = count + 1
        if (x!=y[0]):
            if (y[1]>1)and(tr_te[y[0]+'-'+x]==1):
                if (y[0] in mark) or (not by_list):
                    if x not in NBR:
                        NBR[x] = []
                    NBR[x].append(y[0])
        if (count ==150):
            break

fname_nbs = path +'NeighborSend_list_'+str(by_list)+'.txt'
with open(fname_nbs, 'w') as f:
    json.dump(NBS, f)
fname_nbr = path +'NeighborRec_list_'+str(by_list)+'.txt'
with open(fname_nbr, 'w') as f:
    json.dump(NBR, f)

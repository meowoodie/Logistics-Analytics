'''
    clean rawdata.
    Last edited: June 7.
'''
'''
extract data, seperate it into trainning set and test set

last edited: April 22
'''

from datetime import datetime as dt
import numpy as np
np.random.seed(920804)
import heapq
import json
import os
import arrow as ar
import sys
code_start_time = ar.now()
try:
    path = '../' + sys.argv[1]
except:
    path = '../trainedDataSmall/'
if not os.path.exists(path):
    os.makedirs(path)
fname = '../../../rawdata/steven_monthly_code_tel_201701_07_nm71.txt'
ofname_dicts = path + 'dicts.txt'
ofname_dictr = path + 'dictr.txt'
ofname_dicts_mark = path +'dicts_mark.txt'
ofname_dictr_mark = path +'dictr_mark.txt'
ofname_tplg = path + 'tplg.txt'
ofname_cnt = path + 'cnt.txt'
ofname_inform = path + 'inform.txt'
ofname_As = path + 'A_s.txt'
ofname_Ar = path + 'A_r.txt'
ofname_nl = path + 'namelist.txt'
#### Debug parameters
try:
    breakFlag = sys.argv[2] == 'True'
except:
    breakFlag = True
printline = 100000
from_time = dt.strptime('2017-05-01 00:00:00', '%Y-%m-%d %H:%M:%S')
to_time = dt.strptime('2017-06-30 23:59:59', '%Y-%m-%d %H:%M:%S')
timelen  = 61
####

#print( dt.strptime('2017-04-15 23:59:59', '%Y-%m-%d %H:%M:%S')>from_time)

f = open(fname, "r", encoding = "utf8")
'''
    extract the company mark and the corresonding time of activities
'''
problem_rows = 0
all_rows = 0
dict_s = {}
dict_r = {}
dict_s_mark = {}
dict_r_mark = {}
inform = {}
tplg = {}
A_s = {}
A_r = {}
nameset = set()
namelist = []
cnt = {}
sum_test = 0
for line in f:
    stimeNull = 0
    rtimeNull = 0
    line_ = line.split("\t")
    #print(line_)
    #print(len(line_))
    if (len(line_) == 24):
        S_com = line_[0]
        R_com = line_[13]
        if (line_[11] == 'NULL'):
            stimeNull = 1
        else:
            S_time = dt.strptime(line_[11], '%Y-%m-%d %H:%M:%S')
        if (line_[12] == 'NULL'):
            rtimeNull = 1
        else:
            R_time = dt.strptime(line_[12], '%Y-%m-%d %H:%M:%S')
        if (stimeNull == 0) and(rtimeNull == 0):
            if (S_time <= to_time) and (S_time >= from_time) and(R_time <= to_time) and(R_time >= from_time):
                if S_com not in tplg:
                    dict_s[S_com] = []
                    dict_r[S_com] = []
                    dict_s_mark[S_com] = []
                    dict_r_mark[S_com] = []
                    tplg[S_com] = set()
                    cnt[S_com] = set()
                    tplg[S_com].add(S_com)
                    inform[S_com] = line_[1: 10]
                if R_com not in tplg:
                    tplg[R_com] = set()
                    cnt[R_com] = set()
                    dict_r[R_com] = []
                    dict_s[R_com] = []
                    dict_r_mark[R_com] = []
                    dict_s_mark[R_com] = []
                    inform[R_com] = line_[14: 23]
                if S_com not in A_s:
                    A_s[S_com] = {}
                if R_com not in A_r:
                    A_r[R_com] = {}
                nameset.add(R_com)
                nameset.add(S_com)
                dict_s[S_com].append(S_time)
                dict_s_mark[S_com].append(R_com)
                tplg[S_com].add(R_com)
                cnt[S_com].add(R_com)
                tplg[R_com].add(S_com)
                cnt[R_com].add(S_com)
                dict_r[R_com].append(R_time)
                dict_r_mark[R_com].append(S_com)
                if R_com not in A_s[S_com]:
                    A_s[S_com][R_com] = 1
                else:
                    A_s[S_com][R_com] += 1
                if S_com not in A_r[R_com]:
                    A_r[R_com][S_com] = 1
                else:
                    A_r[R_com][S_com] += 1
#print(tplg)
    else:
        problem_rows = problem_rows + 1
    all_rows = all_rows + 1
    if (all_rows % printline) == 0:
        if breakFlag:
            break
        print('%d\n' %all_rows)
tplglist = {}
for x in tplg:
    tplglist[x] = [y for y in tplg[x]]
print('1')
cntlist = {}
for x in cnt:
    cntlist[x] = [y for y in cnt[x]]
print('2')
for x in dict_s:
    n = len(dict_s[x])
    sort_ind = sorted(range(n), key=lambda k: dict_s[x][k])
    dict_s[x] = [ dict_s[x][i] for i in sort_ind]
    dict_s_mark[x] = [ dict_s_mark[x][i] for i in sort_ind]
    dict_s[x] =[ np.around(x.total_seconds() / 3600, decimals = 2) for x in (np.array(dict_s[x][0:(n)]) - np.array(from_time))]
print('3')
for x in dict_r:
    n = len(dict_r[x])
    sort_ind = sorted(range(n), key=lambda k: dict_r[x][k])
    dict_r[x] = [ dict_r[x][i] for i in sort_ind]
    dict_r_mark[x] = [ dict_r_mark[x][i] for i in sort_ind]
    dict_r[x] =[ np.around(x.total_seconds() / 3600, decimals = 2) for x in (np.array(dict_r[x][0:(n)]) - np.array(from_time))]
print('4')
namelist = [x for x in nameset]
print('5')
with open(ofname_tplg, 'w') as outfile:
    json.dump(tplglist, outfile)
del(tplglist)
print('1')
with open(ofname_cnt, 'w') as outfile:
    json.dump(cntlist, outfile)
del(cntlist)
print('2')
with open(ofname_As, 'w') as outfile:
    json.dump(A_s, outfile)
del(A_s)
with open(ofname_Ar, 'w') as outfile:
    json.dump(A_r, outfile)
del(A_r)
print('3')
with open(ofname_dicts, 'w') as outfile:
    json.dump(dict_s, outfile)
del(dict_s)
print('4')
with open(ofname_dictr, 'w') as outfile:
    json.dump(dict_r, outfile)
del(dict_r)
print('5')
with open(ofname_nl, 'w') as outfile:
    json.dump(namelist, outfile)
del(namelist)
print('6')
with open(ofname_inform, 'w') as outfile:
    json.dump(inform, outfile)
del(inform)
print('7')
with open(ofname_dictr_mark, 'w') as outfile:
    json.dump(dict_r_mark, outfile)
del(dict_r_mark)
print('8')
with open(ofname_dicts_mark, 'w') as outfile:
    json.dump(dict_s_mark, outfile)
del(dict_s_mark)
print('9')



f.close()
logf = open(path+'data_xtr_log.txt', 'w', encoding = 'utf8')
logf.write('Produced by xtr_in_subsample.py\n')
logf.write('Add a dictionary for training(1) and testing(-1).\n')
logf.write('Code starts at: '+str(code_start_time)+'\n')
logf.write('Code ends at: '+str(ar.now()))
logf.close()

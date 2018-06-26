'''
Compute features.

Change: Ar and As


last edited: June 7
'''

from datetime import datetime as dt
import numpy as np
import pandas as pd
import heapq
import json
import arrow as ar
import sys
code_start_time = ar.now()
try:
    path = '../' + sys.argv[1]
except:
    path = '../trainedDataSmall/'

fname_dict = path + 'dicts.txt'
fname_dicts_mark = path +'dicts_mark.txt'
fname_tplg = path + 'tplg.txt'
fname_cnt = path + 'cnt.txt'
fname_inform = path + 'inform.txt'
fname_As = path + 'A_S.txt'
fname_nl = path + 'namelist.txt'
fname_fv = path +'FeatureVector.txt'
with open(fname_dict, 'r') as f:
    dict = json.load(f)
with open(fname_As, 'r') as f:
    A_s = json.load(f)
with open(fname_cnt, 'r') as f:
    cnt = json.load(f)
with open(fname_inform, 'r') as f:
    inform = json.load(f)
with open(fname_nl, 'r') as f:
    namelist = json.load(f)
with open(fname_dicts_mark, 'r') as f:
    dict_s_mark = json.load(f)
#### Debug parameters
try:
    breakFlag = sys.argv[2] == 'True'
except:
    breakFlag = False

print('path = ' +path)
print('breakFlag = ' + str(breakFlag))
####

#print( dt.strptime('2017-04-15 23:59:59', '%Y-%m-%d %H:%M:%S')>from_time)

#f = open(fname, "r", encoding = "utf8")
'''
    extract the feature vectors for each company
    indust1:
    1建筑业
    2批发和零售业
    3交通运输、仓储和邮政业
    4专业服务业
    5制造业
    6政府及公共服务
    7医疗服务
    8金融业
    9房地产业
    10生活服务业
    11农、林、牧、渔业
    12能源

    oversea:
    1 是
    2 否

    fv:
    0: CompanyMark
    1: oversea
    2: indust1
    3: indust2
    4: area
    5: DayAverage
    6: Variation
    7-18: Send Indust
    19-30: Receive Indust
    31: SendOverRec
'''
fv = pd.DataFrame(namelist, columns = ['CMark'], index = namelist)
## oversea indust1 area
df = pd.DataFrame(index = namelist, columns = ['oversea', 'indust1', 'indust2', 'area'])
count = 0
for x in inform:
    count += 1
    df.loc[x, 'oversea'] = inform[x][1]
    df.loc[x, 'indust1'] = inform[x][2]
    df.loc[x, 'indust2'] = inform[x][3]
    df.loc[x, 'area'] = inform[x][7]
    if (count % 20000) == 0:
        print(count)
        if breakFlag:
            break

fv = fv.join(df)
## =====     =====
sum_test = 0

## DayAverage Variation
df = pd.DataFrame(0.000001, index = namelist, columns = ['DayAverage', 'Variation'])
count = 0
timelen = 61
for x in dict:
    count += 1
    daycount = np.zeros(timelen) + 0.000001
    for i, y in enumerate(dict[x]):
        daycount[min(int(y // 24), timelen - 1)] += 1
    mean = np.sum(daycount) / timelen
    df.loc[x, 'DayAverage'] = mean
    df.loc[x, 'Variation'] = np.std(daycount) / mean
    if (count % 20000) == 0:
        print(count)
        if breakFlag:
            break

fv = fv.join(df)
## =====     =====


## toIndust, fromIndust, SendOverRec
IndustN = 2

indust2_set = set()
for x in inform:
    indust2_set.add(inform[x][IndustN])
indust2_list = []
for x in indust2_set:
    indust2_list.append(x)
a = 'toIndust'
b = 'fromIndust'
a_ = [a+str(x) for x in range(len(indust2_list))]
b_ = [b+str(x) for x in range(len(indust2_list))]
a_set = [a + str(x) + '_set' for x in range(len(indust2_list))]
b_set = [b + str(x) + '_set' for x in range(len(indust2_list))]
c_ = ['SendOverRec']
df = pd.DataFrame(0.000001, index = namelist, columns = a_ + b_ + c_)
df_set = pd.DataFrame( index = namelist, columns = a_set + b_set)
IndustMap_to = {}
IndustMap_from = {}
IndustSet_to = {}
IndustSet_from = {}
for x in range(len(indust2_list)):
    IndustMap_to[indust2_list[x]] = a_[x]
    IndustMap_from[indust2_list[x]] = b_[x]
    IndustSet_to[indust2_list[x]] = a_set[x]
    IndustSet_from[indust2_list[x]] =  b_set[x]
count = 0
df_set = df_set.applymap(lambda x: [])
sum_test = 0
for x in A_s:
    count += 1
    #print(count)
    a = inform[x][IndustN]
    for y in A_s[x]:
        b = inform[y][IndustN]
        df.loc[x, IndustMap_to[b]] += A_s[x][y]
        df.loc[y, IndustMap_from[a]] += A_s[x][y]
        df_set.loc[x, IndustSet_to[b]].append(y)
        df_set.loc[y, IndustSet_from[a]].append(x)
        #df_set.loc[x, IndustSet_to[b]] += str(namelist.index(y)) + ' '
        #df_set.loc[y, IndustSet_from[a]] += str(namelist.index(x)) + ' '
    if (count % 20000) == 0:
        print(count)
        if breakFlag:
            break
a = df.iloc[:, 0:len(indust2_list)].sum(axis = 1)
b = df.iloc[:, len(indust2_list): 2*len(indust2_list)].sum(axis = 1)
df['SendOverRec'] = a / b
df.iloc[:, 0:len(indust2_list)] = df.iloc[:, 0:len(indust2_list)].div(a.transpose(), axis = 0)
df.iloc[:, len(indust2_list):2*len(indust2_list)] = df.iloc[:, len(indust2_list):2*len(indust2_list)].div(b.transpose(), axis = 0)
fv = fv.join(df)
fv = fv.join(df_set)
##  =====     =====

fv.to_csv(fname_fv, sep='\t')
logf = open(path+'feature_log.txt', 'w', encoding = 'utf8')
logf.write('Produced by feature.py\n')
logf.write('Feature vectors should be fine.\n')
logf.write('Use A_s instead of A\n')
logf.write('Code starts at: '+str(code_start_time)+'\n')
logf.write('Code ends at: '+str(ar.now()))
logf.close()

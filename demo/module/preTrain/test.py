'''
Compute features.

Change: Ar and As


last edited: Feb 24
'''

from datetime import datetime as dt
import numpy as np
import pandas as pd
import heapq
import json
import arrow as ar
code_start_time = ar.now()
path = '../trainedData/'
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
breakFlag = False
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

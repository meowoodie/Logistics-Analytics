import arrow as ar
from datetime import datetime as dt
import operator
import json
'''
    subsample the rawdata
'''

#### Debug parameters
## 深圳 755Y； 广州 020Y； 上海 021Y； 北京 010Y；杭州 571Y
byarea = False
bylist = True
area = {'755Y', '020Y', '021Y', '010Y','571Y' }
listfn = 'May-June/com_list_5000_BSGS.txt'
subsample = False
breakFlag = False
printline = 20000
start = ar.get(2017,5,1)
end = ar.get(2017,6,30)
codestart = ar.now()
####
fname = '../../rawdata/steven_monthly_code_tel_201701_07_nm71.txt'
ofname = 'May-June/SubSample_'+start.format('MM-DD') + '_' + end.format('MM-DD') +'_'+str(subsample)+'_byComlist'+'.txt'
ofAllNodes_name = 'May-June/AllNodes_byArea_2.txt'
nodes= {}
nodelist = []
f = open(fname, "r", encoding = 'utf8')
of = open(ofname, "w", encoding = 'utf8')
if bylist:
    with open(listfn, 'r') as ls_f:
        nodelist = json.load(ls_f)
    nodelist = set(nodelist)
count = 0
countline = 0
for line in f:
    line_ = line.split("\t")
    lineWrite = True
    count = count + 1
    if (count % printline)==0:
        if breakFlag:
            break
        print('%d\n' % count)
    if (line_[11] == 'NULL') or (line_[12] == 'NULL') or (len(line_) != 24):
        lineWrite = False
        #print('0')
        continue
    sendTime = ar.get(line_[11])
    recTime = ar.get(line_[12])
    if (sendTime>end) or (sendTime<start) or(recTime>end) or (recTime<start):
        lineWrite = False
        #print('1')
        continue
    if (byarea):
        if (line_[6] not in area) or (line_[19] not in area):
            lineWrite = False
            #print('2')
            continue
    if (bylist):
        if (line_[0] not in nodelist) or (line_[13] not in nodelist):
            lineWrite = False
            #print('3')
            continue
    if lineWrite:
        if (line_[0] not in nodes):
            nodes[line_[0]] = 1
        else:
            nodes[line_[0]] += 1
        if (line_[13] not in nodes):
            nodes[line_[13]] = 1
        else:
            nodes[line_[13]] += 1
        of.write(line)
        countline = countline + 1
codeend = ar.now()
print(codeend - codestart)
f.close()
of.close()

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import statsmodels.api as sm
import random
random.seed(920804)
np.random.seed(seed = 920804)
###
limit = 5000
###
with open('May-June/flag_tr_te.txt', 'r') as f:
    tr_te = json.load(f)
UpRF = open('May-June/UpRec_fast.txt', 'r')
DownRF = open('May-June/DownRec_fast.txt', 'r')
upDist = {}
downDist = {}
namelist = []
for i,line in enumerate(UpRF):
    line_ = line.split('##?##')
    upDist[json.loads(line_[0])] = json.loads(line_[1])
    namelist.append(json.loads(line_[0]))
    if i >limit:
        print(1)
        break
for i, line in enumerate(DownRF):
    line_ = line.split('##?##')
    downDist[json.loads(line_[0])] = json.loads(line_[1])
    if i >limit:
        print(1)
        break
recRange = [100,200,500,1000]
rate = [0]*len(recRange)
totalMiss = 0

rateRan = [0]*len(recRange)

randomUp= {}
randomDown = {}
for x in namelist:
    upSet = set()
    downSet = set()
    for y in namelist:
        if (x+'-'+y) not in tr_te:
            downSet.add(y)
        elif (x+'-'+y) in tr_te:
            if (tr_te[x+'-'+y]==-1):
                downSet.add(y)
        if (y+'-'+x) not in tr_te:
            upSet.add(y)
        elif (y+'-'+x) in tr_te:
            if (tr_te[y+'-'+x]==-1):
                upSet.add(y)
    upSet = list(upSet)
    upSet.sort()
    downSet = list(downSet)
    downSet.sort()
    if len(downSet)>1000:
        randomDown[x] = list(np.random.choice(np.array(downSet),1000, replace = False))
    else:
        randomDown[x] = list(downSet)
    if len(upSet)>1000:
        randomUp[x] = list(np.random.choice(np.array(upSet),1000, replace = False))
    else:
        randomUp[x] = list(upSet)

totalMiss_node = {}
totalRecover_node = [{},{},{},{}]
for x in namelist:
    for y in namelist:
        if (x+'-'+y) in tr_te:
            if (tr_te[x+'-'+y]==-1):
                if x not in totalMiss_node:
                    totalMiss_node[x] = 1
                    for i in range(len(recRange)):
                        totalRecover_node[i][x] = 0
                else:
                    totalMiss_node[x] = totalMiss_node[x]+1
                totalMiss +=1
                for i,length in enumerate(recRange):
                    if (y in set(downDist[x][0:length])) or (x in set(upDist[y][0:length])):
                        rate[i] +=1
                        totalRecover_node[i][x] = totalRecover_node[i][x] + 1
                    if (y in set(randomUp[x][0:length])) or (x in set(randomDown[y][0:length])):
                        rateRan[i] +=1
    if x in totalMiss_node:
        for i in range(len(recRange)):
            totalRecover_node[i][x] = totalRecover_node[i][x] / totalMiss_node[x]
with open('output/totalRecoverNode_fast.txt', 'w') as f:
    json.dump(totalRecover_node, f)

rate = [i/totalMiss for i in rate]
print(totalMiss)
print(recRange)
print(rate)

rateRan = [i/totalMiss for i in rateRan]
print(rateRan)

with open('May-June/com_list_5000_BSGS.txt', 'r') as f:
    comList = json.load(f)
lowess = sm.nonparametric.lowess
with PdfPages('output/plots_fast.pdf') as pdf:
    for i in range(len(recRange)):
        x =[]
        y =[]
        c = 0
        for name in comList:
            if name in totalRecover_node[i]:
                x.append(c)
                y.append(totalRecover_node[i][name])
                c = c +1
        plt.hist(y,bins=np.arange(0,1,0.05))
        plt.title('Histogram '+ str(recRange[i]))
        pdf.savefig()
        plt.close()
        w = lowess(y, x, frac=0.05)
        plt.scatter(x,y, s=4)
        plt.plot(w[:,0], w[:,1], 'r')
        plt.title('Scatter '+ str(recRange[i]))
        pdf.savefig()
        plt.close()
        print(np.percentile(y, [10,25,50,75,90],  interpolation = 'lower'))

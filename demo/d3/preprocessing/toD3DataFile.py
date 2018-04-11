'''
change raw_data sample to d3 data file
'''
import arrow as ar
import math
import json

data_file = open('raw_data.txt', "r")

data = []
count =0
for l in data_file:
    line_ls = ['' for i in range(20)]
    count = count +1
    line = l.split('\t')
    date_send = ar.get(line[11]) #.format('YYYY-MM-DDTHH:mm:ss')
    date_receive = ar.get(line[12])#.format('YYYY-MM-DDTHH:mm:ss')
    line_ls[0] = date_send.format('YYYY-MM-DDTHH:mm:ss')
    line_ls[1] = '2017'
    line_ls[2] = ''
    line_ls[3] = line[20]
    line_ls[4] = line[19]
    line_ls[5] = line[10]
    line_ls[6] = ''
    line_ls[7] = ''
    line_ls[8] = ''
    line_ls[9] = ''
    line_ls[10] =''
    line_ls[11] =''
    line_ls[12] = line[3]
    line_ls[13] = line[0]+','+line[3]+"("+line[1]+")" + '->' + line[13]+','+line[16]+ "("+line[14]+")"
    line_ls[14] = date_send.format('YYYY-MM-DDTHH:mm:ss')
    line_ls[15] = ''
    line_ls[16] = line[7]
    line_ls[17] = line[6]
    line_ls[18] = str(math.ceil((date_receive - date_send).total_seconds()/60/60))
    line_ls[19] = ''
    data.append(line_ls)
with open('D3Data.js', 'w') as f:
    f.write('var data_2013=' + json.dumps({'data': data}) +';')

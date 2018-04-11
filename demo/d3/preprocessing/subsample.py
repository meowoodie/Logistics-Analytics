'''
subsample 2000 record from data_file
'''
import numpy as np

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


data_file = open('../../basic_graph/SubSample_05-01_06-30.txt', 'r')
of = open('raw_data.txt', 'w')
count_line = file_len('../../basic_graph/SubSample_05-01_06-30.txt')
print(count_line)
line_to_extract = np.sort(np.random.choice(count_line, 2000, replace = False))

s = 0
for i,l in enumerate(data_file):
    if (i==line_to_extract[s]):
        s = s+1
        of.write(l)
    if (s==2000):
        break
of.close()

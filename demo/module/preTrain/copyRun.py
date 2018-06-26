import sys
try:
    path = '../' + sys.argv[1]
    fname = 'runFull.sh'
except:
    path = '../trainedDataSmall/'
    fname = 'run.sh'

of = open(path+ 'copyOfRun.txt', 'w')


with open(fname, 'r') as f:
    for line in f:
        of.write(line)

of.close()


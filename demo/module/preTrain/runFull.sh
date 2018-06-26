#!/bin/bash

export ppath='trainedDataFull/'
python3 -u copyRun.py $ppath
#python3 -u xtrData.py $ppath False
#python3 -u feature.py $ppath False
#python3 -u sparseAs.py $ppath
python3 -u SimilarityMatrix.py $ppath False 1000
python3 -u SimilarityMatrix2.py $ppath
python3 -u kmeans.py $ppath 8


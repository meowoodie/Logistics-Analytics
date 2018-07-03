
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.externals import joblib
import sys
import numpy as np
import pandas as pd
import random as rd
import json
import arrow as ar
import scipy.sparse as scs
import simFunction as sf
import preRecFast_func as pRFf

######### input
# target = '0000841919'
# target = '0000322504'
# target = '0000187738' #SimM_ind[0] ##"0000"
time0 = ar.now()
path = 'trainedDataFull/'
pca = joblib.load(path + 'PCA_model.pkl')           #trained pca
km_pca = joblib.load(path + 'km_pca_model.pkl')     #trained kmeans model
SimM1 = np.load(path + 'SimilaryMatrix.npy')        #trained based line similarity matrix
SimM_ind = np.load(path + 'SM_index.npy')           #trained index of similarity matrix
fv = pd.read_table(path + 'FeatureVector.txt', sep = '\t', dtype= {'CMark': object}, index_col = 0) #trained featureVector
fv = fv.set_index('CMark')
A_sparse_send = scs.load_npz(path + 'A_sparse_send_full.npz')

with open(path +'NBS.txt', 'r') as f:
    NBS = json.load(f)
with open(path +'NBR.txt', 'r') as f:
    NBR = json.load(f)

namelist = list(fv.index)
# indSet = set(SimM_ind)
# indSet.add(target)
# fv_base_line = fv.loc[list(indSet),:]
# del fv

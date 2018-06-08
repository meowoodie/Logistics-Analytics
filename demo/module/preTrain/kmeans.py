'''
Apply kmeans to the pca of similarity matrix.
Plot elbow curve to determine the appropriate number of clusters.

last edited: June 7.
'''

from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.externals import joblib
import arrow as ar
import matplotlib.pyplot as plt
import numpy as np
path = '../trainedData/'
SimM = np.load(path +'SimilaryMatrix2.npy')
max_k = 40
pca = PCA(n_components = max_k*2, random_state = 920804).fit(SimM)
X_pca = pca.transform(SimM)

np.random.seed(19920804)
kmeans = [KMeans(n_clusters=i, init = 'k-means++', random_state = 1+i) for i in range(1, max_k+1)]
score = [kmeans[i].fit(X_pca).score(X_pca) for i in range(len(kmeans))]
sim_score = []
for i in range(len(kmeans)):
    t = 0
    for j in range(i+1):
        t += SimM[np.ix_(np.where(kmeans[i].labels_==j)[0], np.where(kmeans[i].labels_ == j)[0])].mean()
    sim_score.append(t/(i+1))
plt.plot(range(1, max_k+1),score, 'b.-')
plt.xlabel('Number of Clusters')
plt.ylabel('Score')
plt.title('negative of within-cluster sum of squared criterion')
plt.savefig(path +'elbow_curve.pdf')
plt.clf()

plt.plot(range(1, max_k+1),sim_score, 'b.-')
plt.xlabel('Number of Clusters')
plt.ylabel('Similarity')
plt.title('within-cluster similarity')
plt.savefig(path +'within_cl_sim.pdf')


ncl = 8
pca = PCA(n_components = ncl*2, random_state = 920804).fit(SimM)
X_pca = pca.transform(SimM)
pca_file = path +'PCA_model.pkl'
joblib.dump(pca, pca_file)
km_file = path +'km_pca_model.pkl'
joblib.dump(KMeans(n_clusters=ncl, init='k-means++',random_state = 920804).fit(X_pca), km_file)
t = 0
for j in range(ncl):
    t += SimM[np.ix_(np.where(kmeans[ncl - 1].labels_==j)[0], np.where(kmeans[ncl - 1].labels_ == j)[0])].mean()
print(t/ncl)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''

'''

import sys
import arrow
import pickle
import numpy as np
import matplotlib.pyplot as plt

def deliveryTimeDistributions(
    dataset='data/data_sample.txt',
    cityset='data/city.txt',
    industryset='data/industry_lv1.txt'):
    '''
    This function is for calculating the statistics of delivery time between
    cities and industries. It will return two tensors (3D), which have
    collections (sets) of delivery time as the entries of the matrixs, as well
    as the number of invalid records in the given dataset.
    '''
    # read file path
    with open(dataset, 'r') as fdata, \
         open(cityset, 'r') as fcity, \
         open(industryset, 'r') as findustry:
        # load the set of cities and the set of industry types
        cities        = fcity.readline().strip('\n').split('\t')
        industry_lv1s = findustry.readline().strip('\n').split('\t')
        # initialization of distribution matrix
        city_interval_dist     = [ [ [] for city in cities ] for city in cities ]
        industry_interval_dist = [ [ [] for industry in industry_lv1s ] for industry in industry_lv1s ]
        # global variables for counting
        ind            = 0 # indicator for showing the process
        n_invalid_recs = 0 # number of invalid records
        # loop for scanning dataset
        for line in fdata.readlines():
            data = line.split('\t')
            ship_industry_lv1 = data[3].strip()
            ship_city         = data[8].strip()
            recv_industry_lv1 = data[16].strip()
            recv_city         = data[21].strip()
            # # get set of cities and set of industry type
            # if ship_city not in cities:
            #     cities.add(ship_city)
            # if recv_city not in cities:
            #     cities.add(recv_city)
            # if ship_industry_lv1 not in industry_lv1s:
            #     industry_lv1s.add(ship_industry_lv1)
            # if recv_industry_lv1 not in industry_lv1s:
            #     industry_lv1s.add(recv_industry_lv1)
            # get interval time of each delivery
            try:
                ship_timestamp    = arrow.get(data[11], 'YYYY-MM-DD HH:mm:ss')
                recv_timestamp    = arrow.get(data[12], 'YYYY-MM-DD HH:mm:ss')
                interval_time     = recv_timestamp - ship_timestamp
                city_interval_dist[cities.index(ship_city)][cities.index(recv_city)].append(interval_time.total_seconds())
                industry_interval_dist[industry_lv1s.index(ship_industry_lv1)][industry_lv1s.index(recv_industry_lv1)].append(interval_time.total_seconds())
            except Exception as e:
                n_invalid_recs += 1
            # processing log
            if (ind + 1) % 100000 == 0:
                print('[%s] %d records have been processed.' % (arrow.now(), (ind + 1)), file=sys.stderr)
            ind += 1

        return city_interval_dist, industry_interval_dist, n_invalid_recs

def plot2Dmatrix(matrix, labels=None):
    '''
    '''
    # make sure matrix is a numpy array
    matrix = np.array(matrix)
    # plot matrix
    fig, ax = plt.subplots()
    # font=FontProperties(fname='<span style="background-color:rgb(255,255,204);">/Library/Fonts/Songti.ttc</span>', size=10)
    img = plt.imshow(matrix,
        vmin=matrix.min(), vmax=matrix.max(),
        interpolation='nearest', cmap="jet")
    # plt.xticks(range(len(labels)), labels)
    # plt.yticks(range(len(labels)), labels)
    # ax.set_yticklabels(labels)
    # plot colorbar
    plt.colorbar()
    plt.show()

if __name__ == '__main__':
    # # calculate distribution matrix in accordance with cities and industry types
    # city_interval_dist, industry_interval_dist, _ = deliveryTimeDistributions()
    # # pickle distribution matrix as local files
    # with open('results/city_interval_dist.pkl', 'wb') as f:
    #     pickle.dump(city_interval_dist, f)
    # with open('results/industry_interval_dist.pkl', 'wb') as f:
    #     pickle.dump(industry_interval_dist, f)

    # load pickle file
    with open('results/city_interval_dist.pkl', 'rb') as f:
        city_interval_dist = pickle.load(f)
    with open('results/industry_interval_dist.pkl', 'rb') as f:
        industry_interval_dist = pickle.load(f)
    with open('data/city.txt', 'r') as fcity:
        cities = fcity.readline().strip('\n').split('\t')
    with open('data/industry_lv1.txt', 'r') as findustry:
        industry_lv1s = findustry.readline().strip('\n').split('\t')

    city_interval_num      = [ [ len(dist) for dist in row ] for row in city_interval_dist ]
    industry_interval_num  = [ [ len(dist) for dist in row ] for row in industry_interval_dist ]
    city_interval_mean     = [ [ np.mean(dist) if len(dist) else 0 for dist in row ] for row in city_interval_dist ]
    industry_interval_mean = [ [ np.mean(dist) if len(dist) else 0 for dist in row ] for row in industry_interval_dist ]
    city_interval_std      = [ [ np.std(dist) if len(dist) else 0 for dist in row ] for row in city_interval_dist ]
    industry_interval_std  = [ [ np.std(dist) if len(dist) else 0 for dist in row ] for row in industry_interval_dist ]

    plot2Dmatrix(industry_interval_std)

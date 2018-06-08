#!/bin/bash

# from row data to extract features and to train models
python3 -u xtrData.py
python3 -u feature.py
python3 -u sparseAs.py
python3 -u SimilarityMatrix.py
python3 -u SimilarityMatrix2.py
python3 -u kmeans.py

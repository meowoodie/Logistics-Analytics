#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import col
# from pyspark.sql.types import *

app_name  = "Pump"

delimiter       = ","
input_file_name = "results/count.traffic.src_area_city.csv"
field_name      = "area_city"
count_fields    = [ field_name, "count" ]
pct_fields      = [ field_name, "pct" ]
# Init Spark Context as running in local mode
sc    = SparkContext("local")
# Create a basic Spark Session 
spark = SparkSession \
	.builder \
	.appName(app_name) \
	.getOrCreate()

# Load rawdata from local file system
# And split each row by specific delimiter
source = sc.textFile(input_file_name) \
	.map(lambda x: x.split(delimiter))

count_df = spark.createDataFrame(source, count_fields)

# Get the sum of column "count"
sum_count = float(count_df.agg({"count" : "sum"}).collect()[0][0])

pct_df = count_df \
	.rdd \
	.map(lambda x: [x[0], format(float(x[1])/sum_count, ".4f")]) \
	.toDF(pct_fields) \
	.sort("pct", ascending=False)

pct_df.agg({"pct": "sum"}).show()

pct_df.write.csv("pct")
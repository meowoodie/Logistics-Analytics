#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import col
# from pyspark.sql.types import *

"""
Log (logistics) Pump

As the initial part of the pipeline, it pumps logistics records from local text file to 
its next joints with simple data preprocessing
"""

file_name  = "/Users/woodie/Downloads/sfexpress_rawdata_first2500k.txt"
app_name   = "Pump"

node_info_fields   = ["id", "main_business", "oversea", "industry_lv1", "industry_lv2", "industry_lv3", "area_code", "area_desc", "area_city", "coop_month"]
transc_info_fields = ["transc_id", "ship_timestamp", "deliver_timestamp"]
item_info_fields   = ["item_info"]
src_node_fields    = [ "src_" + field for field in node_info_fields ]
trg_node_fields    = [ "trg_" + field for field in node_info_fields ]

# TODO: MOVE OUT
# Init Spark Context as running in local mode
sc     = SparkContext("local")

# Load rawdata from local file system
# And split each row by specific delimiter
source = sc.textFile(file_name) \
	.map(lambda x: x.split("\t"))

# Create a basic Spark Session 
spark  = SparkSession \
	.builder \
	.appName(app_name) \
	.getOrCreate()
# Specify properties of fields,
# including field name and related data type
log_fields = src_node_fields + transc_info_fields + trg_node_fields + item_info_fields

# DataFrame for logistics data
log_df = spark.createDataFrame(source, log_fields)

# Joint 1:
# Calculate all nodes for the logistics graph
_src_nodes_df = log_df \
	.select(src_node_fields) \
	.dropDuplicates(["src_id"]) \
	.toDF(*(field for field in node_info_fields))
_trg_nodes_df = log_df \
	.select(trg_node_fields) \
	.dropDuplicates(["trg_id"]) \
	.toDF(*(field for field in node_info_fields))

# DataFrame for Nodes 
nodes_df = _src_nodes_df \
	.union(_trg_nodes_df) \
	.dropDuplicates(["id"])
# nodes_df.write.csv(nodes_path)

# Joint 2
# Calculate all links for the logistics graph
links_df = log_df \
	.select(["src_id", "trg_id"]) \
	.groupBy(["src_id", "trg_id"]) \
	.count()
# links_df.write.csv(links_path)

# Joint 3
# Calculate all headstreams & downstreams nodes
_node_ids_df = nodes_df.select(["id"])

_shipped_nodes_df   = links_df \
	.select(["src_id"]) \
	.withColumnRenamed("src_id", "id") \
	.distinct()
_delivered_nodes_df = links_df \
	.select(["trg_id"]) \
	.withColumnRenamed("src_id", "id") \
	.distinct()

head_ids_df = _node_ids_df.subtract(_delivered_nodes_df)
down_ids_df = _node_ids_df.subtract(_shipped_nodes_df)


# heads_df = nodes_df \
# 	.cogroup(head_ids_df) \
# 	.filter(lambda x: x[])
# 	.show()

return 

downs_df = nodes_df \
	.filter(col("id") in down_ids_df.collect()) \
	.show()

# Pipeline 4


# # Parse the input parameters
# 	parser = argparse.ArgumentParser(description="Specify the indices information for link record")
# 	parser.add_argument("-s", "--src_id_ind", required=True, type=int, help="The query id")
# 	parser.add_argument("-t", "--trg_id_ind", required=True, type=int, help="Return the top n results")
# 	parser.add_argument("-S", "--src_info_inds", required=True, help="Return the results that have the similarities above the threshold")
# 	parser.add_argument("-T", "--trg_info_inds", required=True, help="The path of the configuration file")
# 	args = parser.parse_args()
# 	src_id_ind = args.src_id_ind
# 	trg_id_ind = args.trg_id_ind
# 	src_info_inds = [ int(ind) for ind in args.src_info_inds.strip().split(",") ]
# 	trg_info_inds = [ int(ind) for ind in args.trg_info_inds.strip().split(",") ]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import col
# from pyspark.sql.types import *

"""
Log (logistics) to Nodes

As the initial part of the pipeline, it pumps logistics records from local text file to 
its next joints with simple data preprocessing.
"""

app_name = "Log2Graph"

delimiter          = "\t"
input_file_name    = "/Users/woodie/Downloads/sfexpress_rawdata_first2500k.txt"
node_info_fields   = ["id", "main_business", "oversea", "industry_lv1", "industry_lv2", "industry_lv3", "area_code", "area_desc", "area_city", "coop_month"]
transc_info_fields = ["transc_id", "ship_timestamp", "deliver_timestamp"]
item_info_fields   = ["item_info"]
src_node_fields    = [ "src_" + field for field in node_info_fields ]
trg_node_fields    = [ "trg_" + field for field in node_info_fields ]

# Init Spark Context as running in local mode
sc    = SparkContext("local")
# Create a basic Spark Session 
spark = SparkSession \
	.builder \
	.appName(app_name) \
	.getOrCreate()
# Specify properties of fields,
# including field name and related data type
log_fields = src_node_fields + transc_info_fields + trg_node_fields + item_info_fields

# ------------------------------------------
# Pipeline of the Workflow

# Load rawdata from local file system
# And split each row by specific delimiter
source = sc.textFile(input_file_name) \
	.map(lambda x: x.split(delimiter))

# DataFrame for logistics data
log_df = spark.createDataFrame(source, log_fields)

############################################
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

############################################
# Joint 2
# Calculate all links for the logistics graph
links_df = log_df \
	.select(["src_id", "trg_id"]) \
	.groupBy(["src_id", "trg_id"]) \
	.count()

############################################
# Joint 3
# Calculate all headstreams & downstreams nodes
_shipped_node_ids_df   = links_df \
	.select(["src_id"]) \
	.withColumnRenamed("src_id", "id") \
	.distinct()
_delivered_node_ids_df = links_df \
	.select(["trg_id"]) \
	.withColumnRenamed("src_id", "id") \
	.distinct()

_head_ids_df = nodes_df.select(["id"]) \
	.subtract(_delivered_node_ids_df) \
	.withColumnRenamed("id", "head_id")
_down_ids_df = nodes_df.select(["id"]) \
	.subtract(_shipped_node_ids_df) \
	.withColumnRenamed("id", "down_id") \

heads_df = nodes_df \
	.join(_head_ids_df, nodes_df.id == _head_ids_df.head_id, "inner") \
	.drop("head_id")
downs_df = nodes_df \
	.join(_down_ids_df, nodes_df.id == _down_ids_df.down_id, "inner") \
	.drop("down_id")

############################################
# Joints 4
# Calculate the industrial distribution of companies for heads & downs
heads_indust_dist_df = heads_df.groupBy("area_city").count()
downs_indust_dist_df = downs_df.groupBy("area_city").count()

# Output graph
nodes_df.write.csv(nodes_path)
links_df.write.csv(links_path)

# Output other related statistics
heads_indust_dist_df.write.csv("heads_city_dist")
downs_indust_dist_df.write.csv("downs_city_dist")

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

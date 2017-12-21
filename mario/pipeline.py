from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.types import *

import arrow

app_name  = "Pipeline for Logistics"
file_name = "/home/woodie/sfexpress_rawdata_first2500k.txt"
nodes_path = "/home/woodie/nodes.csv"
links_path = "/home/woodie/links.csv"

node_info_fields   = ["id", "main_business", "oversea", "industry_lv1", "industry_lv2", "industry_lv3", "area_code", "area_desc", "area_city", "coop_month"]
transc_info_fields = ["transc_id", "ship_timestamp", "deliver_timestamp"]
item_info_fields   = ["item_info"]
src_node_fields = [ "src_" + field for field in node_info_fields ]
trg_node_fields = [ "trg_" + field for field in node_info_fields ]

# Init Spark Context as running in local mode
sc     = SparkContext("local")
# Create a basic Spark Session 
spark  = SparkSession \
	.builder \
	.appName(app_name) \
	.getOrCreate()
# Load rawdata from local file system
# And split each row by specific delimiter
source = sc.textFile(file_name) \
	.map(lambda x: x.split("\t"))
# Specify properties of fields,
# including field name and related data type
log_fields = src_node_fields + transc_info_fields + trg_node_fields + item_info_fields

# DataFrame for logistics data
log_df = spark.createDataFrame(source, log_fields)

# Pipeline 1:
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

# Pipeline 2
# Calculate all links for the logistics graph
links_df = log_df \
	.select(["src_id", "trg_id"]) \
	.groupBy(["src_id", "trg_id"]) \
	.count()
# links_df.write.csv(links_path)

# Pipeline 3
# Calculate all headstreams & downstreams nodes
_node_ids_df = nodes_df.select(["id"])
	
_shipped_nodes_df   = links_df \
	.select(["src_id"]) \
	.distinct()
_delivered_nodes_df = links_df \
	.select(["trg_id"]) \
	.distinct()

heads_df = _node_ids_df.subtract(_delivered_nodes_df)
downs_df = _node_ids_df.subtract(_shipped_nodes_df)

heads_df.show()

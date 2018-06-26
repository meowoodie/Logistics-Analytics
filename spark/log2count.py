#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import col
# from pyspark.sql.types import *

app_name  = "Log2Count"

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

log_df.groupBy("src_area_city").count().write.csv("src_area_city")
log_df.groupBy("src_industry_lv1").count().write.csv("src_industry_lv1")
log_df.groupBy("src_industry_lv3").count().write.csv("src_industry_lv3")

log_df.groupBy("trg_area_city").count().write.csv("trg_area_city")
log_df.groupBy("trg_industry_lv1").count().write.csv("trg_industry_lv1")
log_df.groupBy("trg_industry_lv3").count().write.csv("trg_industry_lv3")
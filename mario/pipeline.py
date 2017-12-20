from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession

sc    = SparkContext("local")
spark = SparkSession \
	.builder.appName("FirstPipeline") \
	.read.text("/home/woodie/sfexpress_rawdata_first2500k.txt")

print(spark.count())




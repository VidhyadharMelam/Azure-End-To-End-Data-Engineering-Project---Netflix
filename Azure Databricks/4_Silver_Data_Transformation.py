# Databricks notebook source
# MAGIC %md
# MAGIC # Silver_Data_Transformation

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

df = spark.read.format("delta")\
        .option("header", "True")\
        .option("inferSchema", "True")\
        .load("abfss://bronze@netflixdatalake0.dfs.core.windows.net/netflix_titles")

# COMMAND ----------

display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transformation

# COMMAND ----------

# MAGIC %md
# MAGIC #### 1-Get Rid of NULL Values

# COMMAND ----------

df = df.fillna({"duration_minutes": 0, "duration_seasons": 1})

# COMMAND ----------

display(df)

# COMMAND ----------

# MAGIC %md 
# MAGIC #### 2-Convert Data Types of the Columns

# COMMAND ----------

df = df.withColumn("duration_minutes",col("duration_minutes").cast(IntegerType()))\
            .withColumn("duration_seasons",col("duration_seasons").cast(IntegerType()))

# COMMAND ----------

display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4- Fetch "TITLE" Column

# COMMAND ----------

df = df.withColumn("ShortTitle",split(col("title"),":")[0])
display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4- Fetch "RATING" Column

# COMMAND ----------

df = df.withColumn("rating",split(col("rating"),"-")[0])
display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 5- Conditional Column

# COMMAND ----------

df = df.withColumn("type_flag",when(col("type") == "Movie", 1)\
                           .when(col("type") == "TV Show", 2)\
                            .otherwise(0))



# COMMAND ----------

display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 6- Rank The Values In the Column

# COMMAND ----------

from pyspark.sql.window import Window
from pyspark.sql.functions import dense_rank, col

# COMMAND ----------

df = df.withColumn("duration_minutes",dense_rank().over(Window.orderBy(col("duration_minutes").desc())))

# COMMAND ----------

display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 7- Aggregation

# COMMAND ----------

df_vis = df.groupBy("type").agg(count("*").alias("total_count"))

display(df_vis)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write The Data to Silver Layer

# COMMAND ----------

df.write.format("delta")\
        .mode("overwrite")\
        .option("path","abfss://silver@netflixdatalake0.dfs.core.windows.net/netflix_titles")\
        .save()

# COMMAND ----------


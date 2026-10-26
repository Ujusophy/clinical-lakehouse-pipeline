# Databricks notebook source
BUCKET = "" 
RAW = f"s3://{BUCKET}/landing/synthea/csv/"

display(dbutils.fs.ls(RAW))

# COMMAND ----------

df = (spark.read
      .option("header", True)
      .csv(RAW + "patients.csv"))

df.printSchema()
print(df.count())          # should be about 1,000, plus any deceased patients' records
display(df.limit(5))

# COMMAND ----------

from pyspark.sql import functions as F

BRONZE = f"s3://{BUCKET}/bronze/synthea/"

# every CSV in the landing folder becomes one bronze table
files = [f for f in dbutils.fs.ls(RAW) if f.name.endswith(".csv")]

results = []
for f in files:
    table = f.name.replace(".csv", "")
    df = (spark.read
          .option("header", True)
          .csv(f.path)
          .withColumn("_ingested_at", F.current_timestamp())
          .withColumn("_source_file", F.col("_metadata.file_path")))

    (df.write
       .format("delta")
       .mode("overwrite")
       .option("overwriteSchema", "true")
       .save(BRONZE + table))

    results.append((table, df.count()))

display(spark.createDataFrame(results, ["table", "row_count"]))

# COMMAND ----------

display(spark.read.format("delta").load(BRONZE + "patients").limit(5))
display(spark.sql(f"DESCRIBE HISTORY delta.`{BRONZE}patients`"))

# COMMAND ----------

display(spark.sql("SHOW CATALOGS"))
print(spark.sql("SELECT current_catalog()").collect()[0][0])

# COMMAND ----------

CATALOG = "workspace"   # change if Cell 6 showed a different name

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.bronze")

for f in files:
    table = f.name.replace(".csv", "")
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {CATALOG}.bronze.{table}
        USING DELTA
        LOCATION '{BRONZE}{table}'
    """)

display(spark.sql(f"SHOW TABLES IN {CATALOG}.bronze"))

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS patients FROM workspace.bronze.patients;
# MAGIC
# MAGIC SELECT COUNT(*) AS encounters FROM workspace.bronze.encounters;
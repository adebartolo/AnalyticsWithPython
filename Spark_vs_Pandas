# Use Pandas for small to medium datasets, as it offers fast processing, simple usability, 
# and seamless integration with REST APIs. 

# Choose PySpark for large-scale datasets, leveraging distributed and parallel processing, 
# making it ideal for JDBC connections and complex ETL workflows, though it requires a Spark setup. 

import pandas as pd
import random
from pyspark.sql import SparkSession

# Function to determine whether to use Pandas or Spark
def should_use_spark(data_size, threshold=1_000_000):
    return data_size >= threshold

# Generate fake SAP data
num_records = random.randint(500_000, 1_500_000)  # Simulating different data sizes
data = generate_fake_sap_data(num_records)

print(f"Generated {num_records} records...")

if should_use_spark(len(data)):
    # Use Spark for large datasets
    spark = SparkSession.builder.appName("SAPDataIngestion").getOrCreate()
    df_spark = spark.createDataFrame(data)
    print("Using Spark:")
    df_spark.show(5)
else:
    # Use Pandas for small datasets
    df = pd.DataFrame(data)
    print("Using Pandas:")
    print(df.head())

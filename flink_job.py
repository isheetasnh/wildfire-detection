import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.schema import Schema

def run_flink_job():
    # 1. Set up the streaming environment
    env = StreamExecutionEnvironment.get_execution_environment()
    t_env = StreamTableEnvironment.create(env)

    # 2. !!! IMPORTANT !!! Update this path to where you downloaded the JAR
    # This path must be an absolute path and start with 'file://'
    # Example: 'file:///Users/yourname/project/flink-sql-connector-kafka-3.0.2-1.18.jar'
    #jar_path = "file:///Users/shivania/Documents/UMass/Sem3/CS_532/Wildfire_Detection_Project/wildfire-detection/flink-sql-connector-kafka-3.0.2-1.18.jar"
    #t_env.get_config().set("pipeline.jars", jar_path)

    # 3. Define the Kafka Source Table (reading from Kafka)
    # This SQL matches the 'wildfire-events' topic and the JSON format from Step 1
    t_env.execute_sql("""
        CREATE TABLE kafka_source (
            `total_pixels` INT,
            `min_temp_k` DOUBLE,
            `max_temp_k` DOUBLE,
            `mean_temp_k` DOUBLE
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'wildfire-events',
            'properties.bootstrap.servers' = 'kafka:29092',
            'properties.group.id' = 'flink-consumer-group-1',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json'
        )
    """)

    # 4. Define a Sink (e.g., printing to the console)
    # This just prints the data Flink receives.
    t_env.execute_sql("""
        CREATE TABLE print_sink (
            `total_pixels` INT,
            `min_temp_k` DOUBLE,
            `max_temp_k` DOUBLE,
            `mean_temp_k` DOUBLE
        ) WITH (
            'connector' = 'print'
        )
    """)

    # 5. Create and execute the processing logic
    # This simple query finds fires with a max temperature over 400 K
    table = t_env.from_path("kafka_source")
    high_temp_fires = table.where(table.max_temp_k > 400)

    # Send the results of the query to the print_sink
    high_temp_fires.execute_insert("print_sink").wait()

if __name__ == "__main__":
    run_flink_job()
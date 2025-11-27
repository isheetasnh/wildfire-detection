import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

def run_flink_job():
    env = StreamExecutionEnvironment.get_execution_environment()
    t_env = StreamTableEnvironment.create(env)

    # 1. Source: Read from 'wildfire-events'
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

    # 2. Sink: Write to 'processed-wildfire-events'
    # We use the same Kafka broker (kafka:29092) because Flink is inside Docker
    t_env.execute_sql("""
        CREATE TABLE kafka_sink (
            `total_pixels` INT,
            `min_temp_k` DOUBLE,
            `max_temp_k` DOUBLE,
            `mean_temp_k` DOUBLE
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'processed-wildfire-events',
            'properties.bootstrap.servers' = 'kafka:29092',
            'format' = 'json'
        )
    """)

    # 3. Logic: Filter for high temp fires 
    table = t_env.from_path("kafka_source")
    high_temp_fires = table.where(table.max_temp_k > 2000)

    # 4. Execute: Insert into Sink
    high_temp_fires.execute_insert("kafka_sink").wait()

if __name__ == "__main__":
    run_flink_job()
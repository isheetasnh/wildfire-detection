import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

def run_flink_job():
    env = StreamExecutionEnvironment.get_execution_environment()
    t_env = StreamTableEnvironment.create(env)

    # 1. Source: Read from 'wildfire-events'
    t_env.execute_sql("""
        CREATE TABLE kafka_source (
            `s3_timestamp` DOUBLE,
            `total_pixels` INT,
            `min_temp_k` DOUBLE,
            `max_temp_k` DOUBLE,
            `mean_temp_k` DOUBLE,
            `latitude` DOUBLE,
            `longitude` DOUBLE
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
            `s3_timestamp` DOUBLE,
            `total_pixels` INT,
            `min_temp_k` DOUBLE,
            `max_temp_k` DOUBLE,
            `mean_temp_k` DOUBLE,
            `latitude` DOUBLE,
            `longitude` DOUBLE,
            `end_to_end_delay_seconds` BIGINT
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'processed-wildfire-events',
            'properties.bootstrap.servers' = 'kafka:29092',
            'format' = 'json'
        )
    """)

    insert_stmt = """
        INSERT INTO kafka_sink
        SELECT
            s3_timestamp,
            total_pixels,
            min_temp_k,
            max_temp_k,
            mean_temp_k,
            latitude,
            longitude,
            CAST(
                UNIX_TIMESTAMP() - CAST(s3_timestamp AS BIGINT)
                AS BIGINT
            ) AS end_to_end_delay_seconds
        FROM kafka_source
        WHERE max_temp_k > 1000
    """


    t_env.execute_sql(insert_stmt).wait()

if __name__ == "__main__":
    run_flink_job()
import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

def run_flink_job():
    env = StreamExecutionEnvironment.get_execution_environment()
    t_env = StreamTableEnvironment.create(env) 
    t_env.execute_sql("""
        CREATE TABLE kafka_source (
            `s3_timestamp` DOUBLE,
            `total_pixels` INT,
            `min_temp_k` DOUBLE,
            `max_temp_k` DOUBLE,
            `mean_temp_k` DOUBLE,
            `latitude` DOUBLE,
            `longitude` DOUBLE,
            `ts` AS TO_TIMESTAMP_LTZ(CAST(s3_timestamp * 1000 AS BIGINT), 3),
            WATERMARK FOR ts AS ts - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'wildfire-events',
            'properties.bootstrap.servers' = 'kafka:29092',
            'properties.group.id' = 'flink-consumer-group-advanced',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json'
        )
    """)
 
    t_env.execute_sql("""
        CREATE TABLE kafka_sink (
            `window_start` TIMESTAMP(3),
            `window_end` TIMESTAMP(3),
            `grid_latitude` DOUBLE,
            `grid_longitude` DOUBLE,
            `sum_pixels` BIGINT,   -- NEW COLUMN
            `min_temp_k` DOUBLE,   -- (From previous fix)
            `max_temp_k` DOUBLE,
            `avg_temp_k` DOUBLE,
            `event_count` BIGINT,
            `max_end_to_end_delay_seconds` BIGINT,
            `processing_time` TIMESTAMP(3)
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'processed-wildfire-events',
            'properties.bootstrap.servers' = 'kafka:29092',
            'format' = 'json'
        )
    """)

    # 2. Update Insert Statement: Calculate SUM(total_pixels)
    insert_stmt = """
        INSERT INTO kafka_sink
        SELECT
            window_start,
            window_end,
            ROUND(latitude, 1) as grid_latitude,
            ROUND(longitude, 1) as grid_longitude,
            SUM(total_pixels) as sum_pixels,  -- AGGREGATE ACTUAL PIXELS
            MIN(min_temp_k) as min_temp_k,
            MAX(max_temp_k) as max_temp_k,
            AVG(mean_temp_k) as avg_temp_k,
            COUNT(*) as event_count,
            MAX(CAST(UNIX_TIMESTAMP() - CAST(s3_timestamp AS BIGINT) AS BIGINT)) as max_end_to_end_delay_seconds,
            PROCTIME() as processing_time
        FROM TABLE(
            TUMBLE(TABLE kafka_source, DESCRIPTOR(ts), INTERVAL '30' SECOND)
        )
        GROUP BY 
            window_start, 
            window_end, 
            ROUND(latitude, 1), 
            ROUND(longitude, 1)
        HAVING MAX(max_temp_k) > 1000
    """
    t_env.execute_sql(insert_stmt).wait()
if __name__ == "__main__":
    run_flink_job()
# wildfire-detection

This project simulates a real-time data pipeline for detecting wildfire events from GOES-19 satellite imagery.

It consists of three main components:
1.  A **Producer** (`producer.py`) that polls the [NOAA-GOES19 S3 bucket](https://noaa-goes19.s3.amazonaws.com/index.html) for new fire data.
2.  A **Streaming Service** (Kafka) that ingests the fire events.
3.  A **Consumer** (Flink) that processes the events in real-time (e.g., to find high-temperature fires).

## How to Run

### 1. Prerequisites

1. **Docker:** You must have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running. This is used to manage the Kafka and Flink services.
2. **Python 3.10+:** Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3. **Python Dependencies:** Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
4. **Flink-Kafka Connector:** The Flink job needs a JAR file to communicate with Kafka.
    1.  Download the connector: [flink-sql-connector-kafka-3.0.2-1.18.jar](httpss://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.0.2-1.18/flink-sql-connector-kafka-3.0.2-1.18.jar)
    2.  Place this `.jar` file in the root of your project folder.
    3.  Open `flink_job.py` and update the `jar_path` variable to point to its absolute path (e.g., `file:///Users/yourname/project/flink-sql-connector...jar`).

### 2. Running the Simulation

You will need **three separate terminals** for this.

**Terminal 1: Start Services**
1. The first time you run the simulation, build the Docker images:
```
docker-compose up -d --build
```

Note: If you downloaded docker-compose on Linux with sudo apt-get, you may need to run the above command with `sudo`.

2. Start the Kafka, Zookeeper, and Flink containers using Docker.
```bash
docker-compose up -d
```

3. Verify: You can check if Flink is running by visiting its dashboard at http://localhost:8081

4. Start the streaming API/test wildfire data to Kafka. This will start printing events it is sending to Kafka in the terminal, which is contnious loop.
```bash
wildfire-detection % python producer.py
```

5. Submit a Flink job. You can verify that the job is successfully runnning in dashboard http://localhost:8081, under "Running Jobs" tab. You can submit multiple jobs. Note, code changes to file flink_job.py will not be reflected in the submitted jobs. While the new submitted job after the code change will reflect that changes, it is recommended restart the docker and subit a new job, so the outputs of the two jobs are not confused. 
```bash
wildfire-detection % docker exec -it flink-jobmanager /opt/flink/bin/flink run -py /opt/flink/flink_job.py
```

6. You see the logs the of the task manager, where the output of Flink job (processed data) is outputted.
```bash
wildfire-detection % docker logs -f flink-taskmanager
```

7. Shutting Down
When you are finished, stop and remove all the Docker containers:
```
docker-compose down
```

**Terminal 2: Start Consumer**

1. Command to run the flink job
```
   docker exec -u root flink-jobmanager flink run -py /opt/flink/flink_job.py
```


## Folder Structure

- data/read_data.py: Initial experiments for reading FDCF and MCMIPC files.
- producer.py: The "real-time" S3 poller that sends data to Kafka.
- flink_job.py: The Flink streaming application that consumes and analyzes data from Kafka.
- docker-compose.yml: Defines the Kafka, Zookeeper, and Flink services.

## Data Source
The data can be found in the AWS S3 bucket: https://noaa-goes19.s3.amazonaws.com/index.html

The datasets relevant for fire detection include:

* ABI-L2-FDCF: Fire detection and characterization
* ABI-L2-FM1: Fire Mask
* ABI-L2-MCMIPC: multi-channel imagery

The GOES-19 satellite is stationary at -> Longitude: 137.0°W (−137.0°), Altitude: 35,786 km above the equator.

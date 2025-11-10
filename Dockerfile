# Start from the official Flink image
FROM flink:1.18.1-scala_2.12-java11

# Switch to root user to install software
USER root

# Run all our setup commands ONCE during the build
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/lib/apt/lists/partial && \
    apt-get update && \
    # Install Python, pip, JDK (for pemja), and wget
    apt-get install -y python3 python3-pip python-is-python3 openjdk-11-jdk-headless wget && \
    \
    # Create the symlink for pemja (which requires the JDK)
    # This path is for the aarch64 (Apple Silicon) architecture
    ln -s /usr/lib/jvm/java-11-openjdk-arm64/include /opt/java/openjdk/include && \
    \
    # Install the Python (client) libraries
    pip3 install apache-flink==1.18.1 && \
    \
    # Download the Java (server) "translator" JAR
    FLINK_PYTHON_JAR="flink-python-1.18.1.jar" && \
    FLINK_OPT_DIR="/opt/flink/opt" && \
    JAR_URL="https://repo.maven.apache.org/maven2/org/apache/flink/flink-python/1.18.1/${FLINK_PYTHON_JAR}" && \
    mkdir -p ${FLINK_OPT_DIR} && \
    wget -O "${FLINK_OPT_DIR}/${FLINK_PYTHON_JAR}" "${JAR_URL}" && \
    \
    # Clean up apt cache
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the default, low-privilege Flink user
USER flink
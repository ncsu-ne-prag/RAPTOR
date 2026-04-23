FROM ubuntu:24.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies for SCRAM and Hyperfine for benchmarking
# Also install Wine for FTREX
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        cmake \
        libxml2-dev \
        libboost-all-dev \
        hyperfine \
        git \
        ninja-build \
        python3 \
        python3-lxml \
        wine64 \
        wine \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set up Wine environment for FTREX
ENV WINEDEBUG=-all
ENV WINEPREFIX=/opt/wine
ENV WINEARCH=win64
RUN wine winecfg /v win10 || true

# Set up working directory for the build
WORKDIR /build

# Copy the SCRAM source code into the container
COPY apps/solvers/scram /build/scram

# Build SCRAM
RUN mkdir -p /build/scram/build
WORKDIR /build/scram/build
RUN cmake -DCMAKE_BUILD_TYPE=Release -G Ninja .. && \
    cmake --build . --target scram-cli

# Create a symlink to make scram-cli available in the PATH
RUN find /build/scram/build -name scram-cli -type f -executable -exec ln -s {} /usr/local/bin/scram-cli \;

# Copy the Pracciolini tools into the container
COPY apps/tools/pracciolini /build/pracciolini

# Copy the XFTA Linux binary and make it executable
COPY apps/solvers/xfta/xftar /usr/local/bin/xftar
RUN chmod +x /usr/local/bin/xftar

# Set up FTREX
WORKDIR /opt/ftrex
COPY apps/solvers/ftrex/ /opt/ftrex/
RUN chmod +x /opt/ftrex/ftrex && \
    ln -s /opt/ftrex/ftrex /usr/local/bin/ftrex && \
    /opt/ftrex/ftrex "/SERIAL=$(cat /opt/ftrex/Serial.txt | tr -d '\r\n')"

# Set up working directory for benchmarks
WORKDIR /benchmark

# Default command
CMD ["bash"]

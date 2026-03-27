FROM ubuntu:24.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies for SCRAM and Hyperfine for benchmarking
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
        python3-lxml && \
    rm -rf /var/lib/apt/lists/*

# Set up working directory for the build
WORKDIR /build

# Copy the SCRAM source code into the container
COPY apps/solvers/scram/node-addon /build/scram

# Build SCRAM
WORKDIR /build/scram/build
RUN cmake -DCMAKE_BUILD_TYPE=Release -G Ninja .. && \
    cmake --build . --target scram-cli

# The binary should be available in the build directory.
# We will create a symlink to make it available in the PATH
RUN ln -s /build/scram/build/targets/scram/scram-cli /usr/local/bin/scram || \
    ln -s /build/scram/build/bin/scram-cli /usr/local/bin/scram || \
    find /build/scram/build -name scram-cli -type f -executable -exec ln -s {} /usr/local/bin/scram \;

# Copy the Pracciolini tools into the container
COPY apps/tools/pracciolini /build/pracciolini

# Set up working directory for benchmarks
WORKDIR /benchmark

# Default command
CMD ["bash"]

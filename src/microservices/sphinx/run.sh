#!/usr/bin/env bash

docker run -it\
    --env RMQ_ADDR=192.168.1.8 \
    --env STREAM_ADDR=192.168.1.8 \
    --env DB_API_ADDR=192.168.1.8 \
    --env DB_API_PORT=8000 \
    --mount type=bind,source=/mnt/test,target=/tmp navneetraju/video_benchmark:audio_analytics



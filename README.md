# ViStA: Video Streaming and Analytics Benchmark

 ViStA benchmark is a video streaming and analytics benchmark that can be used to measure the performance of systems running these workloads.
 ViStA benchmark was published in the 2021 IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS).\
 [Paper Link](https://ieeexplore.ieee.org/document/9408175)


## Setup
The ViStA benchmark consists of the following microservices:
1. Orchestrator - Orchestrates the processing jobs using a RESTful interface
2. Database - Acts as an interface layer to the MongoDB database
3. HLS Streamer - HLS based video streaming microservice
4. Sphinx - Sphinx speech to text analysis
5. YOLO - YOLOv3 object detection model
6. FFMPEG - FFMPEG video conversion tool for encoding raw videos into HLS streamable chunks
7. RabbitMQ - Message Broker
8. MongoDB - Storage of analytics results (or path of encoded HLS files)
9. Redis - Caching mechanism

## Prerequistes

Kubernetes single node cluster with Linkerd service mesh and prometheus service running. 

#### Note: This project only supports Kubernetes *single node* cluster.

### Setup instructions:



Linkerd and Prometheus:
- The current implementation uses a [Linkerd](https://linkerd.io/) service mesh for reliability, observaility and for ease of request tracing.
- Prometheus is also used in conjunction for metrics exploration. 
  - The prometheus directory provides sample configs that can help in setting up metrics job easily
  - Kubernetes deployments for rabbitmq,monogdb,redis also include metrics exporters to have insights on the core services
- Although prometheus and linkerd are used, feel free to setup your own observality system

Scaling:
- The scaling directory contains Kubernetes HPA configurations that enable you to autoscale your services based on custom metrics.

RabbitMQ:
- RabbitMQ is the AMQP broker choosen for this benchmark due to its ease of setup and ease of use.
- FFMPEG(HLS encoder),YOLO,Sphinx each have their individual queues which are consumed by the specific service.

Microservices Setup

- Each microservice has a seperate Dockerfile to build the docker image.
- Each microservice also has a Kubernetes deployment file showing the various parameters and configurations to spin up the deployment
- Ensure to spin up the services in the following order: \
RabbitMQ > MongoDB > Redis > Database service > Orchestrator > Other microservices

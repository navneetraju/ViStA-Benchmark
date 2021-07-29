## Orchestrator
Usage: 
```
docker run -d --hostname my-rabbit --name some-rabbit -p 15672:15672 -p 5672:5672 rabbitmq:3-management
docker run -dp 6379:6379 redis:latest
docker run -dp 27017:27017 mongo:latest
docker run -dp 8000:80 --env HOST_IP_ADDR=<HOST IP ADDRESS HERE> navneetraju/video_benchmark:db_api
docker run -p 80:80 --env DB_API_ADDR=<HOST IP ADDRESS HERE> --env RMQ_ADDR=<HOST IP ADDRESS HERE> --env DB_API_PORT=8000 --mount type=bind,source=/mnt/test,target=/tmp navneetraju/video_benchmark:orch
```
- Ensure a mount directory /mnt/test or change accordingly for testing
- HOST IP ADDRESS must NOT be localhost or 127.0.0.1. Use ip address by running ipconfig/ifconfig.
- Ensure all ports are available
- Ensure to pull all images before running to get up-to-date images.
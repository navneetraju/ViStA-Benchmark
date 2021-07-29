## Database API
Usage(Server):
```
docker pull navneetraju/video_benchmark:db_api
docker run -p 80:80 navneetraju/video_benchmark:db_api
```
Usage(local):
1. Get localhost ip using ipconfig/ifconfig, do not use 127.0.0.1/localhost
2. Modify Dockerfile HOST_IP_ADDR
3. ```
   docker build -t db_api .
   ```
4. ```
   docker run -dp 27017:27017 mongo:latest
   docker run -dp 6379:6379 redis:latest
   docker run -p 80:80 db_api
   ```

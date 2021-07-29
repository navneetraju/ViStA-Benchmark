FROM ubuntu:18.04

RUN apt clean && apt update && apt upgrade -y
RUN apt install -y ffmpeg
RUN apt install -y python3-pip
RUN apt install -y bc

WORKDIR /app

COPY ./app .
COPY ./requirements.txt .

RUN pip3 install -r requirements.txt 

CMD ["python3", "main.py"]


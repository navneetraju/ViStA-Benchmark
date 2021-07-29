FROM ubuntu:18.04

RUN apt clean && apt update && apt upgrade -y
RUN apt install ffmpeg -y
RUN apt install libsm6 -y 
RUN apt install libxext6 -y 
RUN apt install python3-pip -y
RUN pip3 install --upgrade pip

WORKDIR /app

COPY ./app .
COPY ./requirements.txt .

RUN pip3 install -r requirements.txt 

CMD ["python3", "main.py"]


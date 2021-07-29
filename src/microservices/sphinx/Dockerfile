FROM ubuntu:18.04

RUN apt clean && apt update && apt upgrade -y
RUN apt install -y python3-pip
RUN apt install git -y
RUN apt install swig -y
RUN apt install ffmpeg -y
WORKDIR /app

COPY ./app .
COPY ./sphinx_install.sh .
COPY ./requirements.txt .
RUN bash sphinx_install.sh
RUN pip3 install -r requirements.txt 

CMD ["python3", "main.py"]


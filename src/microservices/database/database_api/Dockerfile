FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY ./app /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV HOST_IP_ADDR '10.10.1.146'
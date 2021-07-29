from fastapi import FastAPI, File, UploadFile,HTTPException,Form,Query,Request
from fastapi.responses import JSONResponse
import shutil
from pydantic import BaseModel
import pika
import sys
import requests
from requests.auth import HTTPBasicAuth
from typing import List,Optional
import json
import os

DB_API_ADDR = os.environ['DB_API_ADDR']
DB_API_PORT = os.environ['DB_API_PORT']
RMQ_ADDR = os.environ['RMQ_ADDR']


class resultsClass(BaseModel):
    video_name : str
    operations : list

class UnicornException(Exception):
    def __init__(self, res: dict()):
        self.res = res


app = FastAPI()

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=206,
        content=exc.res,
    )

@app.post("/api/orch/submit")
async def video(video: UploadFile = File(...),operations: List[str] = []):
    if len(operations) == 0:
        raise HTTPException(422,detail="Need to give at least one operation")
    if video.content_type!="video/mp4":
        raise HTTPException(415,detail="Unaccepted media type, must be an MP4 file")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RMQ_ADDR))
    channel = connection.channel()

    path_final="/tmp/"+video.filename
    with open(path_final, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    message = video.filename
    failed_operations=[]
    
    for operation in operations:
        if not operation:
            failed_operations.append("<EMPTY OPERATION>")
            continue
        try:
            channel.queue_declare(queue=operation ,passive = True,durable = True)
        except:
            failed_operations.append(operation)
            channel=connection.channel()
            continue

        channel.basic_publish(
            exchange='',
            routing_key=operation,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2, 
            ))
        print(" [x] Operation %r scheduled successfully" % operation)
    connection.close()
    if len(failed_operations)==0:
        return {"video name ":video.filename,"details":"All jobs submitted succesfully"}
    elif len(failed_operations)==len(operations):
        raise HTTPException(500,detail="None of the submitted operations were successful")
    else:
        raise HTTPException(206,detail="Following operations were not submitted succesfully: "+str(failed_operations))

@app.get('/api/orch/get_operations')
async def get_operations():
    res = requests.get('http://'+RMQ_ADDR+':15672/api/queues', auth=HTTPBasicAuth('guest', 'guest'))
    res = res.json()
    avail_operations = []
    for i in res:
        avail_operations.append(i['name'])
    return {'available operations:':avail_operations}

@app.get('/api/orch/get_results')
async def get_results(query: resultsClass):
    queryResult = {}
    flag  = False
    for operation in query.operations:
        data={"video_name":query.video_name,"operation_name":operation}
        res = requests.get('http://'+DB_API_ADDR+':'+DB_API_PORT+'/api/db/read',data=json.dumps(data))
        if res.status_code == 200 or res.status_code == 206:
            queryResult[operation] = res.json()  
        else:
            flag = True
            queryResult[operation] = "NO RESULT"
    if flag:
        raise UnicornException(res=queryResult)
    return queryResult

@app.delete('/api/orch/clear_results')
async def get_results():
    res = requests.delete('http://'+DB_API_ADDR+':'+DB_API_PORT+'/api/db/clear')
    if res.status_code == 200:
        return {'detail':'cleared succesfully'}
    else:
        raise HTTPException(500,'could not clear succesfully')

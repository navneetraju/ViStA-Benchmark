from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from pymongo import MongoClient
from rediscluster import RedisCluster
import pickle
import os

MONGO_SERVER_IP = os.environ['MONGO_SERVER_IP']
REDIS_SERVER_IP = os.environ['REDIS_SERVER_IP']
startup_nodes = [{"host": "10.1.125.39", "port": "6379"},{"host": "10.1.125.23", "port": "6379"},{"host": "10.1.125.42", "port": "6379"},{"host": "10.1.125.28", "port": "6379"}]
class video_format(BaseModel):
    video_name:str
    data:dict
    operation_name: str

class video_format_read(BaseModel):
    video_name: str 
    operation_name: str

class UnicornException(Exception):
    def __init__(self, res: dict()):
        self.res = res

#redis_client=redis.Redis(host=REDIS_SERVER_IP,port=6379)
redis_client = RedisCluster(startup_nodes=startup_nodes)

def check_redis_connection():
    try:
        redis_client.set("hello")
    except:
        return False
    return True

def check_mongo_connection(mongoClient: MongoClient):
    try:
        mongoClient.server_info()
    except:
        return False
    return True

app=FastAPI()

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=206,
        content=exc.res,
    )

@app.post('/api/db/write',status_code=201)
async def storeDB(video: video_format):
    mongo_connect=MongoClient(MONGO_SERVER_IP,27017)
    if not check_mongo_connection(mongo_connect):
        raise HTTPException(500,'Could not connect to MongoDB')
    analytics_db=mongo_connect['analytics_db']
    operation_col=analytics_db[video.operation_name]
    data={}
    data['data']=video.data
    data['video_name']=video.video_name
    if len(list(operation_col.find({'video_name':video.video_name}))) != 0:
        newvalues={"$set":{"data":video.data}}
        try:
            operation_col.update_one({'video_name':video.video_name},newvalues)
        except:
            raise HTTPException(status_code=500,detail='Could not update in MongoDB')
        redisActiveState=check_redis_connection()
        redisName=video.video_name+video.operation_name
        if redisActiveState and redis_client.exists(redisName):
            try:
                res_dict=redis_client.delete(redisName)
            except:
                raise HTTPException(status_code=500,detail='Something went wrong, could not invalidate cache entry')
        return {'detail':'Updated MongoDB successfully'}
    try:
        operation_col.insert_one(data)
    except:
        raise HTTPException(status_code=500,detail='Could not insert into MongoDB')
    return {'detail':'Inserted into MongoDB successfully'}


@app.get('/api/db/read')
async def getFromDB(video: video_format_read):
    res={}
    video_name=video.video_name
    res['video_name']=video_name
    redisActiveState=check_redis_connection()
    redisName = video.video_name + video.operation_name
    if redis_client.exists(redisName):
        print('Found in Redis Cache!')
        '''
        try:
            res_dict=redis_client.get(redisName)
        except:
            raise HTTPException(status_code=500,detail='Something went wrong')
        '''
        res_dict=redis_client.get(redisName)
        res_dict=pickle.loads(res_dict)
        res['data']=res_dict
        return res
    else:
        mongo_connect=MongoClient(MONGO_SERVER_IP,27017)
        if not check_mongo_connection(mongo_connect):
            raise HTTPException(500,'Cache miss,Could not connect to MongoDB')
        analytics_db=mongo_connect['analytics_db']
        operation_col=analytics_db[video.operation_name]
        print('Cache Miss, Fecthing from MongoDB!')
        mongo_fetch_query={'video_name':video_name}
        fetched_doc=operation_col.find(mongo_fetch_query)
        fetched_doc=list(fetched_doc)
        if len(fetched_doc)==0:
            raise HTTPException(204)
        res['data']=fetched_doc[0]['data']
        pickled_tags=pickle.dumps(res['data'])
        '''
        if not redisActiveState:
            print('redis connection failed')
            raise UnicornException(res=res)
        try:
            redis_client.set(redisName,pickled_tags,ex=60)
        except:
            raise UnicornException(res=res)
        '''
        print('Stub here')
        redis_client.set(redisName,pickled_tags,ex=60)
        return res

@app.delete('/api/db/clear')
async def cleardb():
    mongo_connect=MongoClient(MONGO_SERVER_IP,27017)
    if not check_mongo_connection(mongo_connect):
        raise HTTPException(500,'MongoDB connection error')
    mongo_movie_db=mongo_connect['analytics_db']
    collections = mongo_movie_db.list_collection_names()
    try:
        for i in collections:
            mongo_movie_db[i].drop()
    except:
        raise HTTPException(500,'Could not clear MongoDB collection')

    if not check_redis_connection():
        raise HTTPException(500,'Redis connection error')
    try:
        redis_client.flushall()
    except:
        raise HTTPException(500,'Could not flush Redis cache')

    return {'detail':'MongoDB movie_tags collection cleared and cache flushed '}

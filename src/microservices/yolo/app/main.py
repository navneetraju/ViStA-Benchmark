import pika
import requests, json
import subprocess, os
import logging
import threading
import functools
import time

from video import * 

RMQ_ADDR = os.environ.get('RMQ_ADDR') or 'localhost'
STREAM_ADDR = os.environ.get('STREAM_ADDR') or 'localhost'
DB_API_ADDR = os.environ.get('DB_API_ADDR') or 'localhost'
DB_API_PORT = os.environ.get('DB_API_PORT') or '8000'
VIDEO_DIRECTORY = '/tmp'

#LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
#              '-35s %(lineno) -5d: %(message)s')
#LOGGER = logging.getLogger(__name__)

#logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

def ack_message(channel, delivery_tag):
    """Note that `channel` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).
    """
    if channel.is_open:
        channel.basic_ack(delivery_tag)
    else:
        # Channel is already closed, so we can't ACK this message;
        # log and/or do something that makes sense for your app in this case.
        pass

def do_work(connection, channel, delivery_tag, body):
    thread_id = threading.get_ident()
    fmt1 = 'Thread id: {} Delivery tag: {} Message body: {}'
    #LOGGER.info(fmt1.format(thread_id, delivery_tag, body))

    video_name = body.decode()
    print("[x] Recieved %r " % video_name)
    path_to_video = os.path.join(VIDEO_DIRECTORY, video_name) 
    path_to_storage = os.path.join(VIDEO_DIRECTORY, video_name.split('.')[0])
    objects = dict(get_large_videotranscription(path_to_video))
    print("[x] Done")
    payload = {
            "video_name": video_name,
            "data":objects, 
            "operation_name":"object_detection"
    }
    
    res = requests.post(
               'http://'+DB_API_ADDR+':'+DB_API_PORT+'/api/db/write',
               data=json.dumps(payload) 
            )
    if res.status_code == 201:
        print("object_detection: Written to video objects to DB.")
    else:
        print("object_detection: Something went wrong writing to DB: ", res.status_code)
    

    cb = functools.partial(ack_message, channel, delivery_tag)
    connection.add_callback_threadsafe(cb)

def on_message(channel, method_frame, header_frame, body, args):
    (connection, threads) = args
    delivery_tag = method_frame.delivery_tag
    t = threading.Thread(target=do_work, args=(connection, channel, delivery_tag, body))
    t.start()
    threads.append(t)

credentials = pika.PlainCredentials('guest', 'guest')
parameters =  pika.ConnectionParameters(RMQ_ADDR, credentials=credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()
channel.queue_declare(queue="object_detection",durable=True, auto_delete=True)
# Note: prefetch is set to 1 here as an example only and to keep the number of threads created
# to a reasonable amount. In production you will want to test with different prefetch values
# to find which one provides the best performance and usability for your solution
channel.basic_qos(prefetch_count=1)

threads = []
callback =  functools.partial(on_message, args=(connection, threads))
channel.basic_consume(queue='object_detection', on_message_callback=callback)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()

# Wait for all to complete
for thread in threads:
    thread.join()

connection.close()

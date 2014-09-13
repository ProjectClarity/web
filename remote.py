from pymongo import MongoClient
import boto, os
from boto.sqs.jsonmessage import JSONMessage

client = MongoClient(os.environ.get('MONGO_URI'))
db = client[os.environ.get('MONGO_URI').split('/')[-1]]
users = db.users
raw_data = db.raw_data
processed_data = db.processed_data

sqs_conn = boto.sqs.connect_to_region("us-east-1")
worker_queue = sqs_conn.get_queue(os.environ.get('SQS_QUEUE'))
worker_queue.set_message_class(JSONMessage)

from fastapi import FastAPI, HTTPException
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
from minio import Minio
from minio.error import S3Error
from pydantic import BaseModel
import redis
import json
import uvicorn
import io
import time
import uuid
import os

app = FastAPI()

# Kafka config (PLAINTEXT)
KAFKA_BOOTSTRAP_SERVERS = ['kafka:29092']
KAFKA_TOPIC_NAME = "test-topic"
REPLICATION_FACTOR = 1

# MinIO config
MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "minio_pass"
MINIO_BUCKET_NAME = "test-bucket"
MINIO_SECURE = False

# Redis config
REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 0

# Model
class Message(BaseModel):
    id: int
    content: str

# Kafka Producer (no SASL_SSL)
def init_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Kafka Producer connected successfully!")
        return producer
    except Exception as e:
        print(f"Failed to connect to Kafka: {e}")
        return None

# Kafka Topic
def init_kafka_topic():
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            client_id='fastapi_admin'
        )
        existing_topics = admin_client.list_topics()
        if KAFKA_TOPIC_NAME not in existing_topics:
            topic_list = [NewTopic(
                name=KAFKA_TOPIC_NAME,
                num_partitions=1,
                replication_factor=REPLICATION_FACTOR
            )]
            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            print(f"Topic '{KAFKA_TOPIC_NAME}' created successfully!")
        else:
            print(f"Topic '{KAFKA_TOPIC_NAME}' already exists!")
        admin_client.close()
    except TopicAlreadyExistsError:
        print(f"Topic '{KAFKA_TOPIC_NAME}' already exists, skipping creation.")
    except Exception as e:
        print(f"Error creating topic: {e}")

# MinIO client
def init_minio_client():
    try:
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        if not client.bucket_exists(MINIO_BUCKET_NAME):
            client.make_bucket(MINIO_BUCKET_NAME)
            print(f"Bucket '{MINIO_BUCKET_NAME}' created successfully!")
        else:
            print(f"Bucket '{MINIO_BUCKET_NAME}' already exists!")
        return client
    except S3Error as e:
        print(f"Failed to connect to MinIO: {e}")
        return None

# Redis client
def init_redis_client():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        r.ping()
        print("Connected to Redis successfully!")
        return r
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        return None

# Init all services
producer = init_producer()
print("Wait 3 seconds for Kafka...")
time.sleep(3)
init_kafka_topic()
minio_client = init_minio_client()
redis_client = init_redis_client()

# API Kafka
@app.post("/send-message/kafka/")
async def send_message_kafka(message: Message):
    if producer is None:
        raise HTTPException(status_code=500, detail="Cannot connect to Kafka")
    try:
        data = message.model_dump()
        future = producer.send(KAFKA_TOPIC_NAME, value=data)
        producer.flush()
        # Kiểm tra lỗi từ Kafka
        record_metadata = future.get(timeout=10)
        return {
            "status": "success",
            "topic": record_metadata.topic,
            "partition": record_metadata.partition,
            "offset": record_metadata.offset,
            "message": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kafka error: {str(e)}")

# API MinIO
@app.post("/send-message/minio/")
async def send_message_minio(message: Message):
    if minio_client is None:
        raise HTTPException(status_code=500, detail="Cannot connect to MinIO")
    try:
        data = message.model_dump()
        data_json = json.dumps(data, indent=2).encode('utf-8')
        object_name = f"message_{data['id']}_{uuid.uuid4().hex}.json"

        minio_client.put_object(
            bucket_name=MINIO_BUCKET_NAME,
            object_name=object_name,
            data=io.BytesIO(data_json),
            length=len(data_json),
            content_type="application/json"
        )
        return {"status": "success", "message": f"Saved to MinIO: {object_name}"}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=str(e))

# API Redis
@app.post("/send-message/redis/")
async def send_message_redis(message: Message):
    if redis_client is None:
        raise HTTPException(status_code=500, detail="Cannot connect to Redis")
    try:
        # Tạo key ngẫu nhiên với uuid4
        random_id = uuid.uuid4().hex
        key = f"message:{random_id}"
        
        # Lưu vào Redis
        redis_client.set(key, json.dumps(message.model_dump()))
        
        # Đọc lại để trả về
        value = redis_client.get(key)
        return {
            "status": "success",
            "stored_key": key,
            "stored_value": json.loads(value)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Shutdown
@app.on_event("shutdown")
def shutdown_event():
    if producer:
        producer.close()
        print("Kafka Producer closed")
    print("FastAPI shutdown complete.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from common.config import LgApiConfig, PostgresConfig, RabbitMQConfig
from common.device_dal import DeviceDAL
from common.lg_api_client import LGApiClient
from common.postgres_connection import PostgresConn
import pika

app = FastAPI()

rabbitmq_config = RabbitMQConfig()

postgres_config = PostgresConfig()
postgres_conn_string = f"postgresql://{postgres_config.POSTGRES_USER}:{postgres_config.POSTGRES_PASSWORD}@{postgres_config.POSTGRES_HOST}:5432/{postgres_config.POSTGRES_DB}"

lg_api_config = LgApiConfig()
lg_api_client = LGApiClient(
    lg_api_config.LG_COUNTRY,
    lg_api_config.LG_API_KEY,
    lg_api_config.LG_CLIENT_ID,
    lg_api_config.LG_API_TOKEN
)

@app.get("/devices")
def list_devices():
    with PostgresConn(postgres_conn_string) as conn:
        device_dal = DeviceDAL(conn)
        registered_devices = {d.id for d in device_dal.list()}
        all_devices = lg_api_client.get_devices()  # Returns List[Device]
        unregistered_devices = [d for d in all_devices if d.id not in registered_devices]
        return {
            "registered": [d.__dict__ for d in all_devices if d.id in registered_devices],
            "unregistered": [d.__dict__ for d in unregistered_devices]
        }

class DeviceRegisterRequest(BaseModel):
    device_ids: List[str]

@app.post("/devices/register")
def register_devices(request: DeviceRegisterRequest):
    with PostgresConn(postgres_conn_string) as conn:
        device_dal = DeviceDAL(conn)
        all_devices = {d.id: d for d in lg_api_client.get_devices()}
        to_register = []
        not_found = []
        for device_id in request.device_ids:
            device = all_devices.get(device_id)
            if device:
                to_register.append(device)
            else:
                not_found.append(device_id)
        if to_register:
            device_dal.bulk_insert(to_register)
        return {
            "registered": [d.id for d in to_register],
            "not_found": not_found
        }
    
class DeviceSyncRequest(BaseModel):
    device_id: str

@app.post("/devices/sync_energy")
def sync_energy(request: DeviceSyncRequest):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_config.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_config.RABBITMQ_QUEUE)
    channel.basic_publish(
        exchange='',
        routing_key=rabbitmq_config.RABBITMQ_QUEUE,
        body=request.device_id.encode(),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    return {"status": "published", "device_id": request.device_id}
import json
import boto3
import os
import uuid
from kafka import KafkaProducer

def scanImage(event, context):

    TOPIC_NAME = "image-scans"

    producer = KafkaProducer(
        bootstrap_servers=os.environ["KAFKA_SERVER_URL"],
        security_protocol="SSL",
        ssl_cafile="aiven-cred/ca.pem",
        ssl_certfile="aiven-cred/service.cert",
        ssl_keyfile="aiven-cred/service.key",
        value_serializer=lambda v: json.dumps(v).encode("ascii"),
        key_serializer=lambda v: json.dumps(v).encode("ascii")
    )
    
    bucket = os.environ['IMAGES_BUCKET']
    region_name = os.environ['REGION_NAME']
    files = event['Records']
    outputs = []
    
    for file in files:
        file_name = file["s3"]["object"]["key"]

        rekognition_client = boto3.client(
            'rekognition', 
            region_name=region_name
        )

        response = rekognition_client.detect_labels(
            Image={
                'S3Object':
                    {
                        'Bucket':bucket,
                        'Name':file_name
                    }
            },
            MaxLabels=5
        )

        outputs.append(
             {
               'imageKey':file_name,
                'labels':response["Labels"]
            }
        )

        producer.send(
            topic=TOPIC_NAME,
            key=str(uuid.uuid4()),
            value=json.dumps(outputs)
        )

    producer.close()

    return {
        "statusCode": 200
    }

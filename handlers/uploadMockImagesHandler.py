import requests
import os
import json
import boto3
import random

def uploadImages(event,context):

    lookup_key = os.environ['PIXABAY_KEY']
    lookup_url = f'https://pixabay.com/api/?key={lookup_key}&q=yellow+flowers&image_type=photo'
    lookup_response = requests.get(lookup_url)

    lookup = lookup_response.json()
    print(lookup)
    session = boto3.Session()
    s3 = session.resource('s3')

    bucket_name = os.environ['IMAGES_BUCKET']
    bucket = s3.Bucket(bucket_name)
    uploads=0

    for hit in lookup['hits']:
        imageURL = hit['largeImageURL']
        image = requests.get(imageURL, stream=True)
        file_name = hit['previewURL'].split('/')[-1]
        bucket.upload_fileobj(image.raw, file_name)
        uploads += 1

    return {
        "statusCode": 200,
        "body": f'images uploaded:{uploads}'
    }

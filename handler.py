import face_recognition
import pickle
import os
import subprocess
import boto3
import logging
import csv
from io import StringIO

# Configure the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

input_bucket = "cc-ss-input-2"
output_bucket = "cc-ss-output-2"
s3 = boto3.client('s3')
file_path = '/home/app/encoding'
table_name = 'cc-ss-proj2-table'

# Function to read the 'encoding' file
def open_encoding(filename):
    with open(filename, "rb") as file:
        data = pickle.load(file)
    return data

def get_info_from_dynamo(name):
    dynamodb = boto3.client('dynamodb')
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                'name': {'S': name}
            }
        )
        if 'Item' in response:
            item = response['Item']
            return item
        else:
            return "Item not found in DynamoDB."
    except Exception as e:
        return str(e)

def convert_ddb_item_to_row(fieldnames, information_from_dynamo):
    row = {}
    for key in fieldnames:
        value = information_from_dynamo[key]['S']
        logger.info(type(value))
        row[key] = str(value)
    return row

def upload_file_to_s3(video_file_name, information_from_dynamo):
    s3 = boto3.client('s3')
    bucket_name = 'cc-ss-output-2'
    object_name = video_file_name.replace('.mp4', '') + ".csv"
    csv_data = StringIO()
    fieldnames = ['name', 'major', 'year']
    row = convert_ddb_item_to_row(fieldnames, information_from_dynamo)
    csv_writer = csv.DictWriter(csv_data, fieldnames=fieldnames)
    csv_writer.writeheader()
    csv_writer.writerow({'name': row['name'], 'major': row['major'], 'year': row['year']})
    s3.put_object(Bucket=bucket_name, Key=object_name, Body=csv_data.getvalue())

def compare_encoding(array, arrays):
    for i in range(len(arrays)):
        result = face_recognition.compare_faces(array, arrays[i])
        if all(result):
            return i
    return -1

def face_recognition_handler(event, context):
    try:
        logger.info(event)
        logger.info(context)
        logger.info("Lambda function executed.")
        encoding_dict = open_encoding(file_path)
        encoding_names = encoding_dict['name']
        logger.info(encoding_names)
        encoding_values = encoding_dict['encoding']
        key = "placeholder"
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            logger.info(bucket)
            logger.info(key)
            frame_dir = "/tmp/frames/"
            os.makedirs(frame_dir, exist_ok=True)
            video_path = "/tmp/" + key
            video_dir = '/'.join(video_path.split('/')[:-1])
            os.makedirs(video_dir, exist_ok=True)
            s3.download_file(bucket, key, video_path)
            frame_pattern = f"{frame_dir}%04d.jpg"
            subprocess.call(['ffmpeg', '-i', video_path, frame_pattern])
            frame_files = os.listdir(frame_dir)
            frame_files.sort()
            result = None
            for frame_file in frame_files:
                frame_image = face_recognition.load_image_file(os.path.join(frame_dir, frame_file))
                unknown_face_encoding = face_recognition.face_encodings(frame_image)
                result = compare_encoding(unknown_face_encoding, encoding_values)
                if result != -1:
                    break
            if result != -1:
                name_of_person_detected = encoding_names[result]
                logger.info(f"First face detected for {key}! Name of the person identified is: {name_of_person_detected}")
                info_from_ddb = get_info_from_dynamo(name_of_person_detected)
                logger.info(info_from_ddb)
                upload_file_to_s3(key, info_from_ddb)
            else:
                logger.info(f"No faces detected for: {key}")
            for frame_file in frame_files:
                os.remove(os.path.join(frame_dir, frame_file))
            os.remove(video_path)
        return {
            'statusCode': 200,
            'body': f'Processing complete. File Uploaded to S3 for video: {key}'
        }
    except Exception as e:
        raise e

import face_recognition
import pickle
import os
import subprocess
import boto3
import numpy as np
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

input_bucket = "cc-ss-input-2"
output_bucket = "cc-ss-output-2"
s3 = boto3.client('s3')
# file_path = '/home/app/encoding'
file_path = 'encoding'

# Function to read the 'encoding' file
def open_encoding(filename):
    file = open(filename, "rb")
    data = pickle.load(file)
    file.close()
    return data


def face_recognition_handler(event, context):
    try:
        logger.info(event)
        logger.info(context)
        logger.info("Lambda function executed.")
        encoding_dict=open_encoding(file_path)
        encoding_names=encoding_dict['name']
        encoding_values = encoding_dict['encoding']

        for record in event['Records']:

            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            logger.info(bucket)
            logger.info(key)

            frame_dir = "/tmp/frames/"
            os.makedirs(frame_dir, exist_ok=True)
            video_path = "/tmp/"+key
            video_dir = '/'.join(video_path.split('/')[:-1])
            os.makedirs(video_dir, exist_ok=True)

            # Download the video from S3
            s3.download_file(bucket, key, video_path)

            # Use FFmpeg to extract frames
            frame_pattern = f"{frame_dir}%04d.jpg"
            subprocess.call(['ffmpeg', '-i', video_path, frame_pattern])

            # List the extracted frame files
            frame_files = os.listdir(frame_dir)
            frame_files.sort()

            # Initialize the first face location
            result = None

            for frame_file in frame_files:
                frame_image = face_recognition.load_image_file(os.path.join(frame_dir, frame_file))
                unknown_face_encoding = face_recognition.face_encodings(frame_image)
                for index, value in enumerate(encoding_values):
                    if value == unknown_face_encoding:
                        result= index

            if result:
                print(f"First face detected for {key}! Name of the person identified is  : {encoding_names[result]}")
            else:
                print(f"No faces detected for : {key}")

            # Cleanup: Delete the extracted frames and downloaded video
            for frame_file in frame_files:
                os.remove(os.path.join(frame_dir, frame_file))
            os.remove(video_path)

        return {
            'statusCode': 200,
            'body': 'Processing complete.'
        }
    except Exception as e:
        raise e
if __name__ == '__main__':
    event={
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "2023-10-21T06:32:01.378Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "A2UJIRMU9PGJGP"
      },
      "requestParameters": {
        "sourceIPAddress": "72.201.57.106"
      },
      "responseElements": {
        "x-amz-request-id": "RQPX9N2KAS9XEDSM",
        "x-amz-id-2": "SfMX+LhadYEOTOU5BnmDyTxe/w/ZgOH0RnvL6ccnz0AngKNgVzgf7/JGVL9kCuPv7QGfSgLxuQm1M0CQ3f0GSjtkEJY1ORkZ2fBUyoGzZJc="
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "c9361b17-de7b-4df9-b9fa-2193e28a4f41",
        "bucket": {
          "name": "cc-ss-input-2",
          "ownerIdentity": {
            "principalId": "A2UJIRMU9PGJGP"
          },
          "arn": "arn:aws:s3:::cc-ss-input-2"
        },
        "object": {
          "key": "raw/test_8.mp4",
          "size": 624083,
          "eTag": "1c6a7147ac6d63f70b0fb8fd4d691e72",
          "sequencer": "0065337061452A496C"
        }
      }
    }
  ]
}
    print(face_recognition_handler(event,[]))
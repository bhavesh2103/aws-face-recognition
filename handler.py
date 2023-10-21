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
file_path = 'encoding'


# Function to read the 'encoding' file
def open_encoding(filename):
    file = open(filename, "rb")
    data = pickle.load(file)
    file.close()
    return data


def face_recognition_handler(event, context):
    try:
        logger.info("Lambda function executed.")
        all_face_encodings = open_encoding(file_path).values()
        #print(all_face_encodings)
        logger.info(all_face_encodings)
        for record in event['Records']:

            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            frame_dir = "/tmp/frames/"
            os.makedirs(frame_dir, exist_ok=True)
            video_path = f"/tmp/{key}"
            frame_paths = []

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
                unknown_face = face_recognition.face_encodings(frame_image)
                result = face_recognition.compare_faces(all_face_encodings, unknown_face)

                if result:
                    break

            if result:
                print(f"First face detected for {key}! Result : {result}")
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
# if __name__ == '__main__':
#     event={
#         "Records" :{
#             "s3" : {
#                 "bucket" : {
#                     "name" : "s3://cc-ss-input-2"
#                 },
#                 "object" : {
#                     "key" : "raw/test_0.mp4"
#                 }
#             }
#         }
#     }
#     print(face_recognition_handler(event,[]))
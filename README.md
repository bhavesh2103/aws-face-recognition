#  Serverless server Cloud computing project 2 : Smart Classroom Assistant for Educators using PaaS

## Group Members:
    1. Bhavesh khubnani
    2. Aishwariya Ranjan
    3. Abhijeet Dixit


## S3 Buckets : 
    1. Input bucket  : cc-ss-input-2
    2. Output Bucket : cc-ss-output-2

## Steps to run the code from scratch :

    1. Clone the Repository
        Clone this repository to your local machine.

    2. Build Docker Image
        Create a Docker image by running the following command:

        `docker build -t your-app-name .`
    
    3. Set Up Amazon Elastic Container Registry (ECR)
        Create an Amazon Elastic Container Registry.
        Follow the instructions to push the Docker image you created in step 2 to your ECR repository.

    4. Create S3 Buckets
        Create two S3 buckets: one for uploading video files (Input) and the other for storing the results (Output).

    5. Create DynamoDB Table
        Create a DynamoDB table with 'name' as the primary key. This table will be used to store information related to recognized faces.
    
    6. Create Lambda Function
        Create a Lambda function in your AWS account.
        
    7. Configure Lambda as a Container Function
        When creating the Lambda function, select the option to create it from a Container Image. This will allow you to use the Docker image you pushed to ECR.
    
    8. Set Up S3 Trigger for Lambda
        After creating the Lambda function, add a trigger using the Lambda console. 
        Configure the trigger to respond to events in the S3 Input Bucket created in step 4. 
        This will initiate the face recognition process when a video is uploaded.
    
    9. Monitor the Output
        Add a video file to the Input S3 bucket.
         Monitor the S3 Output Bucket (created in step 4) to access details of recognized faces in the uploaded video.

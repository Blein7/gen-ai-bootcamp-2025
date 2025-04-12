import boto3
import json

print("Boto3 version:", boto3.__version__)

try:
    print("Initializing bedrock client...")
    bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
    print("Client initialized successfully")
    
    print("Testing converse method...")
    messages = [{
        "role": "user",
        "content": [{
            "text": "Say hello"
        }]
    }]
    
    response = bedrock_client.converse(
        modelId="amazon.nova-micro-v1:0",
        messages=messages,
        inferenceConfig={
            "temperature": 0.7,
            "topP": 0.9,
            "maxTokens": 100
        }
    )
    
    print("Response received successfully")
    print("Response text:", response['output']['message']['content'][0]['text'])
    print("Test completed successfully")
    
except Exception as e:
    print("Error occurred:", str(e))
    import traceback
    traceback.print_exc() 
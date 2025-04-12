import boto3
import json
import os
import sys

# Add parent directory to path to import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.chat import BedrockChat

def test_bedrock_integration():
    """
    Test Bedrock integration with various API calls
    """
    print("=== TESTING BEDROCK INTEGRATION ===")
    
    # Print environment variables (redacted for security)
    aws_key = os.environ.get('AWS_ACCESS_KEY_ID', '')
    aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    
    if aws_key:
        print(f"AWS_ACCESS_KEY_ID: {aws_key[:4]}...{aws_key[-4:]}")
    else:
        print("AWS_ACCESS_KEY_ID: Not set")
        
    if aws_secret:
        print(f"AWS_SECRET_ACCESS_KEY: {aws_secret[:4]}...{aws_secret[-4:]}")
    else:
        print("AWS_SECRET_ACCESS_KEY: Not set")
        
    print(f"AWS_DEFAULT_REGION: {aws_region}")
    
    # Test 1: Create basic Bedrock client
    print("\n=== TEST 1: Basic boto3 client creation ===")
    try:
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region
        )
        print("✓ Successfully created boto3 bedrock-runtime client")
    except Exception as e:
        print(f"✗ Error creating boto3 client: {str(e)}")
        return False
    
    # Test 2: Test basic embeddings API
    print("\n=== TEST 2: Testing embedding model ===")
    try:
        model_id = 'amazon.titan-embed-g1-text-02'
        request_body = json.dumps({"inputText": "日本語を勉強しています。"})
        
        response = bedrock.invoke_model(
            modelId=model_id,
            body=request_body
        )
        
        response_body = json.loads(response['body'].read())
        embedding_length = len(response_body.get('embedding', []))
        
        if embedding_length > 0:
            print(f"✓ Successfully received embeddings (length: {embedding_length})")
        else:
            print("✗ Received empty embeddings")
            return False
    except Exception as e:
        print(f"✗ Error invoking embedding model: {str(e)}")
        return False
    
    # Test 3: Test BedrockChat class (converse API)
    print("\n=== TEST 3: Testing BedrockChat class (converse API) ===")
    try:
        print("Creating BedrockChat instance...")
        bedrock_chat = BedrockChat()
        print("✓ Successfully created BedrockChat instance")
        
        print("Testing generate_response method with simple prompt...")
        response = bedrock_chat.generate_response("こんにちは")
        
        if response and isinstance(response, str) and len(response) > 0:
            print(f"✓ Successfully received chat response: '{response[:100]}'...")
            print("BedrockChat integration is working!")
        else:
            print("✗ Received empty or invalid response")
            return False
    except Exception as e:
        print(f"✗ Error using BedrockChat: {str(e)}")
        
        # Check if the error is related to the converse method
        if "has no attribute 'converse'" in str(e):
            print("\nThis error indicates your boto3 version might not support the 'converse' method.")
            print("The solution is to update boto3 to version 1.34.0 or higher:")
            print("pip install boto3>=1.34.0")
        return False
    
    # All tests passed
    print("\n=== OVERALL RESULT ===")
    print("✓ All Bedrock integration tests passed!")
    return True

if __name__ == "__main__":
    test_bedrock_integration() 
import boto3
import json
from botocore.config import Config
from datetime import datetime

def structure_jlpt_listening_data(transcript_path):
    # Initialize Amazon Bedrock client
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',
        config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
    )

    # Read the transcript from the file
    with open(transcript_path, 'r', encoding='utf-8') as file:
        transcript = file.read()

    # Prepare the prompt for Amazon Nova Micro
    prompt = f"""
    Extract only the JLPT listening test questions from the following transcript, excluding any introduction and outro:

    {transcript}

    For each question, provide the following structure:
    introduction:
    conversation:
    question:

    Separate each question with '---'.
    """

    # Define the system prompt
    system_list = [
        {
            "text": "You are a helpful assistant that extracts JLPT listening test questions from transcripts."
        }
    ]

    # Define the message list
    message_list = [{"role": "user", "content": [{"text": prompt}]}]

    # Configure the inference parameters
    inf_params = {"maxTokens": 1000, "topP": 0.9, "topK": 20, "temperature": 0.7}

    # Prepare the request body
    request_body = {
        "schemaVersion": "messages-v1",
        "messages": message_list,
        "system": system_list,
        "inferenceConfig": inf_params,
    }

    # Invoke the model with the response stream
    response = bedrock.invoke_model_with_response_stream(
        modelId='amazon.nova-micro-v1:0',  # Replace with the correct model identifier
        body=json.dumps(request_body)
    )

    # Process the response stream
    structured_data = ""
    stream = response.get("body")
    if stream:
        for event in stream:
            chunk = event.get("chunk")
            if chunk:
                chunk_json = json.loads(chunk.get("bytes").decode())
                content_block_delta = chunk_json.get("contentBlockDelta")
                if content_block_delta:
                    structured_data += content_block_delta.get("delta").get("text")

    # Split the structured data into individual questions
    questions = structured_data.split('---')

    # Further process each question if needed
    processed_questions = []
    for i, question in enumerate(questions, start=1):
        parts = question.strip().split('\n')
        if len(parts) >= 3:
            processed_question = {
                'introduction': parts[0].replace('introduction:', '').strip(),
                'conversation': parts[1].replace('conversation:', '').strip(),
                'question': parts[2].replace('question:', '').strip()
            }
            processed_questions.append(f"Question {i}:\nIntroduction: {processed_question['introduction']}\nConversation: {processed_question['conversation']}\nQuestion: {processed_question['question']}\n")

    return processed_questions


if __name__ == "__main__":
    structured_questions = structure_jlpt_listening_data("./transcripts/0e0duD8_LFE.txt")
    for question in structured_questions:
        print(question)
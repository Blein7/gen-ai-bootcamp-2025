import boto3
import json
from botocore.config import Config
from datetime import datetime
import os

def invoke_bedrock(prompt, model_id='amazon.nova-micro-v1:0'):
    # Initialize Amazon Bedrock client
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',
        config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
    )

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
        modelId=model_id,
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

    return structured_data

def process_section(structured_data):
    # Split the structured data into individual sections
    sections = structured_data.split('===')

    # Further process each section and its questions
    processed_sections = []
    for section in sections:
        section_parts = section.strip().split('---')
        section_description = section_parts[0].strip()
        questions = section_parts[1:]

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

        processed_sections.append(f"Section Description: {section_description}\nQuestions:\n" + "\n".join(processed_questions))

    return processed_sections

def save_output(processed_sections, output_path):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Handle versioning if the output file already exists
    base, ext = os.path.splitext(output_path)
    version = 1
    while os.path.exists(output_path):
        output_path = f"{base}_v{version}{ext}"
        version += 1

    # Save the output to a file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for section in processed_sections:
            output_file.write(section + "\n\n")

def structure_jlpt_listening_data(transcript_path, output_base_path):
    # Read the transcript from the file
    with open(transcript_path, 'r', encoding='utf-8') as file:
        transcript = file.read()

    # Define prompts for each section
    prompts = [
        f"""
        Extract the first section of the JLPT listening test questions from the following transcript, excluding any introduction and outro. Extract the description of the format and the questions for this section.

        {transcript}

        For this section, provide the following structure:
        section_description: <description of the section in Japanese>
        questions:
        - introduction: <introduction text>
          conversation: <conversation text>
          question: <question text>

        Ensure that the 'question' part is not empty and contains the actual question being asked.

        Separate each question with '---'.
        """,
        f"""
        Extract the second section of the JLPT listening test questions from the following transcript, excluding any introduction and outro. Extract the description of the format and the questions for this section.

        {transcript}

        For this section, provide the following structure:
        section_description: <description of the section in Japanese>
        questions:
        - introduction: <introduction text>
          conversation: <conversation text>
          question: <question text>

        Ensure that the 'question' part is not empty and contains the actual question being asked.

        Separate each question with '---'.
        """,
        f"""
        Extract the third section of the JLPT listening test questions from the following transcript, excluding any introduction and outro. Extract the description of the format and the questions for this section.

        {transcript}

        For this section, provide the following structure:
        section_description: <description of the section in Japanese>
        questions:
        - introduction: <introduction text>
          conversation: <conversation text>
          question: <question text>

        Ensure that the 'question' part is not empty and contains the actual question being asked.

        Separate each question with '---'.
        """
    ]

    # Process each section separately
    for i, prompt in enumerate(prompts, start=1):
        structured_data = invoke_bedrock(prompt)
        processed_sections = process_section(structured_data)
        output_path = f"{output_base_path}_section_{i}.txt"
        save_output(processed_sections, output_path)

if __name__ == "__main__":
    transcript_path = "./data/transcripts/0e0duD8_LFE.txt"
    output_base_path = "./data/questions/structured_questions"
    structure_jlpt_listening_data(transcript_path, output_base_path)